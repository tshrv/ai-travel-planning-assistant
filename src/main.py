import asyncio
from dataclasses import dataclass
from pathlib import Path

import html2text
import typer
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from loguru import logger
from playwright.async_api import async_playwright

from utils.time import get_current_timestamp


@dataclass
class Source:
    uid: str
    source_id: str
    name: str
    label: str
    url: str
    file_path: Path


app = typer.Typer()


@app.command()
def ping():
    """Ping-pong"""
    logger.success("Pong")


async def fetch_dynamic_html(url: str) -> str:
    """Fetch client-side rendered HTML via Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Wait until network calls complete so dynamic JS loads
        await page.goto(url, wait_until="networkidle")
        html_content = await page.content()
        await browser.close()
        return html_content


def html_to_clean_markdown(html_content: str) -> str:
    """Convert raw rendered HTML into clean Markdown."""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0  # Prevents unnecessary line wrapping mid-sentence
    return converter.handle(html_content)


def download_content(location_name: str, label: str, url: str, uid: str) -> Path:
    """Extract contents from web in markdown and save to file"""
    logger.info(f"downloading from url {url}")
    html_content = asyncio.run(fetch_dynamic_html(url))
    markdown_text = html_to_clean_markdown(html_content)

    # write to file
    outfile = Path(f"data/{uid}/{location_name}_{label}.md")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"writing contents to {outfile}")
    with open(outfile, "w") as f:
        f.write(markdown_text)
    return outfile


def ingest_contents(sources: list[Source]):
    """Read markdown files, chunk and ingest into storage"""
    chunks = build_chunks(sources)
    embeddings = HuggingFaceEmbeddings(
        # TODO: benchmark BGE-M3 vs BGE-large
        # model_name="BAAI/bge-m3",
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="ai_travel_planning_assistant",
    )


def build_chunks(sources: list[Source]) -> list[Document]:
    """Read markdown files and generate chunks"""
    ln_sources = len(sources)
    all_chunks: list[Document] = []
    for i, source in enumerate(sources):
        logger.info(
            f"processing {i}/{ln_sources}: source_id {source.source_id}, source_url {source.url}"
        )

        with open(source.file_path, "r") as f:
            markdown_text = f.read()
            # structure-aware markdown split (preserves H1, H2, H3 headers in metadata)
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on,
                strip_headers=False,  # Retains headers inside the text body for context
            )
            header_splits = markdown_splitter.split_text(markdown_text)

            # secondary character split (ensures large sections fit within context windows)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=150
            )
            final_chunks = text_splitter.split_documents(header_splits)
            ln_final_chunks = len(final_chunks)

            # inject metadata into all chunks
            for i, chunk in enumerate(final_chunks):
                chunk.metadata["chunk_id"] = f"{source.uid}_{source.source_id}_{i}"
                chunk.metadata["source_id"] = source.source_id
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = ln_final_chunks
                chunk.metadata["uid"] = source.uid
                chunk.metadata["location_name"] = source.name
                chunk.metadata["label"] = source.label
                chunk.metadata["source_url"] = source.url
                chunk.metadata["file_path"] = str(source.file_path)

            all_chunks.extend(final_chunks)
    return all_chunks


@app.command()
def sync_location_data(
    name: str = typer.Argument(
        ..., help='Name of location to sync data, like "Singapore"'
    ),
):
    """Extract and load data from all sources for the mentioned location"""
    uid = get_current_timestamp()
    logger.info(f"unique id: {uid}")
    name = name.strip().lower()
    data = {
        "singapore": {
            "wiki": "https://en.wikivoyage.org/wiki/Singapore",
            "essential-travel-information": "https://www.visitsingapore.com/travel-tips/essential-travel-information/",
            "solo-travel-to-singapore-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/solo-travel-to-singapore-guide/",
            "singapore-city-tour-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/singapore-city-tour-guide/",
            "7-days-in-singapore": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/7-days-in-singapore/",
            "24-hours-in-singapore": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/24-hours-in-singapore/",
            "singapore-food-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/singapore-food-guide/",
            "places-to-visit-with-family": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/places-to-visit-with-family/",
            "top-things-to-do": "https://www.visitsingapore.com/things-to-do/top-things-to-do/",
        }
    }
    if name not in data:
        raise ValueError(f"Location data not available for {name}")
    ln = len(data[name])

    sources: list[Source] = []

    # download
    logger.info(f"Found {ln} sources for {name}")
    for i, (label, url) in enumerate(data[name].items(), start=1):
        logger.info(f"{i}/{ln}")
        file_path = download_content(name, label.lower(), url, uid)
        sources.append(Source(uid, i, name, label, url, file_path))

    # ingest
    ingest_contents(sources)

    logger.info(f'sync completed for "{name}"')


@app.command()
def query(query: str):
    """Search query"""
    embeddings = HuggingFaceEmbeddings(
        # TODO: benchmark BGE-M3 vs BGE-large
        # model_name="BAAI/bge-m3",
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="ai_travel_planning_assistant",
    )

    results = vector_store.similarity_search_with_score(
        query=query,
        k=5,
    )
    for doc, score in results:
        print(score)
        print(doc.page_content)
        print(doc.metadata)
        print("*" * 50)


if __name__ == "__main__":
    app()
