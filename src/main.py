import typer
from loguru import logger

import ingestion
from rag import RAG
from utils.time import get_current_timestamp

app = typer.Typer()
from rich import print

from agent import rag_chain


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
def rag_search():
    """Search RAG results on query"""
    rag = RAG()
    while True:
        query = input("> Enter search phrase: ")
        results = rag.search(query=query)
        print("\n-----RESULTS-----\n")
        for i, result in enumerate(results, start=1):
            print(f"#{i}")
            print("- vector score:", result.vector_score)
            print("- rerank score:", result.rerank_score)
            print("- metadata:")
            print(result.document.metadata)
            print("- page content:")
            print(result.document.page_content)
            print("\n")


@app.command()
def agent():
    logger.info("Hi, how can I help you?")
    while True:
        user_input = input(">> ")
        resp = rag_chain.invoke(user_input)
        print(resp)


if __name__ == "__main__":
    app()
