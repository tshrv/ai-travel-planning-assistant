import asyncio
from pathlib import Path

import html2text
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from loguru import logger
from playwright.async_api import async_playwright

from ingestion.models import Source
from vector_store import create_collection, get_vector_store

SOURCES = {
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


async def _fetch_dynamic_html(url: str) -> str:
    """Fetch client-side rendered HTML via Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Wait until network calls complete so dynamic JS loads
        await page.goto(url, wait_until="networkidle")
        html_content = await page.content()
        await browser.close()
        return html_content


def _html_to_clean_markdown(html_content: str) -> str:
    """Convert raw rendered HTML into clean Markdown."""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0  # Prevents unnecessary line wrapping mid-sentence
    return converter.handle(html_content)


def _download_content(source: Source) -> Path:
    """Extract contents from web in markdown and save to file"""
    logger.info(f"source id {source.source_id}: downloading {source.url}")
    html_content = asyncio.run(_fetch_dynamic_html(source.url))
    markdown_text = _html_to_clean_markdown(html_content)

    # write to file
    outfile = Path(f"data/{source.uid}/{source.name}_{source.label}.md")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"writing contents to {outfile}")
    with open(outfile, "w") as f:
        f.write(markdown_text)
    # add outfile to source
    source.file_path = outfile
    return outfile


def _embed_and_save(source: Source):
    """Create embeddings for chunks and save to vector store"""
    logger.info(f"source id {source.source_id} : saving to vector db")
    vector_store = get_vector_store()
    results = vector_store.add_documents(documents=source.chunks)


def _build_chunks(source: Source) -> list[Document]:
    """Read markdown files, generate chunks and add to source"""
    logger.info(f"source id {source.source_id}: building chunks")
    markdown_text = ""
    with open(source.file_path, "r") as f:
        markdown_text = f.read()

    if not markdown_text:
        return []

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
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(header_splits)
    ln_chunks = len(chunks)

    # inject metadata into all chunks
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{source.uid}_{source.source_id}_{i}"
        chunk.metadata["source_id"] = source.source_id
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = ln_chunks
        chunk.metadata["uid"] = source.uid
        chunk.metadata["name"] = source.name
        chunk.metadata["label"] = source.label
        chunk.metadata["source_url"] = source.url
        chunk.metadata["file_path"] = str(source.file_path)

    # update source attribute
    source.chunks = chunks
    return chunks


def _get_sources(name: str, uid: str) -> list[Source]:
    """Build source objects"""
    name = name.strip().lower()
    if name not in SOURCES:
        raise ValueError(f"Sources not available for {name}")
    sources = SOURCES[name]
    ln = len(sources)
    source_objs: list[Source] = []
    logger.info(f"found {ln} sources for {name}")
    for i, (label, url) in enumerate(sources.items(), start=1):
        source_objs.append(
            Source(uid=uid, source_id=f"{uid}_s{i}", name=name, label=label, url=url)
        )
    return source_objs


def initiate(name: str, uid: str):
    """Initiate the ingestion process"""
    create_collection()
    sources = _get_sources(name, uid)
    sources_ln = len(sources)
    for i, source in enumerate(sources, start=1):
        logger.info(f"processing source {i}/{sources_ln}")
        # download
        file_path = _download_content(source)
        # chunk
        chunks = _build_chunks(source)
        # embed and save
        _embed_and_save(source)
    logger.info(f"processing completed for {sources_ln} sources")
