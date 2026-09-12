import io

import typer
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_core.documents import Document
from loguru import logger
from markitdown import MarkItDown

from utils.time import get_current_timestamp

app = typer.Typer()

@app.command()
def ping():
    """Ping-pong"""
    logger.success("Pong")

def extract_content(url: str) -> list[Document]:
    """Extract content from dynamic webpages"""
    loader = AsyncChromiumLoader([url])
    html_docs = loader.load()
    md = MarkItDown()
    markdown_docs = []
    for doc in html_docs:
        stream = io.BytesIO(doc.page_content.encode("utf-8"))
        result = md.convert_stream(stream, file_extension=".html")
        markdown_docs.append(
            Document(
                page_content=result.text_content,
                metadata={"title": result.title, **doc.metadata},
            )
        )
    return markdown_docs


@app.command()
def sync_location_data(
    name: str = typer.Argument(
        ..., help='Name of location to sync data, like "Singapore"'
    ),
):
    """Extract and load data from all sources for the mentioned location"""
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

    timestamp = get_current_timestamp()
    for label, url in data[name].items():
        label = label.lower()
        docs = extract_content(url)
        for i, doc in enumerate(docs):
            outfile = f"data/{name}_{label}_{timestamp}_{i}.md"
            logger.info(f"Writing contents to {outfile}")
            with open(outfile, "w") as f:
                f.write(doc.page_content)
        logger.info(f"Completed for {len(docs)} file(s) for {label}")
    logger.info(f'Sync completed for "{name}"')


if __name__ == "__main__":
    app()
