import typer
from loguru import logger

import ingestion
import search
from utils.time import get_current_timestamp

app = typer.Typer()
from rich import print


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
    ingestion.initiate(name, uid)
    logger.info(f'sync completed for "{name}"')


@app.command()
def search_vectors():
    """Mode: search vector store"""
    logger.info("Search Vectors")
    while True:
        phrase = input("> Enter search phrase: ")
        results = search.search(phrase=phrase)
        print("\n-----RESULTS-----\n")
        for i, (doc, score) in enumerate(results, start=1):
            print(f"#{i}")
            print("- score:", score)
            print("- metadata:")
            print(doc.metadata)
            print("- page content:")
            print(doc.page_content)
            print("\n")


if __name__ == "__main__":
    app()
