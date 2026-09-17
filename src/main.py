import asyncio

import typer
from loguru import logger
from rich import print

import ingestion
from utils.time import get_current_timestamp

app = typer.Typer()


@app.command()
def extract_load_data(
    name: str = typer.Argument(
        ..., help='Name of location to load data, like "Singapore"'
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
    from rag.rag import RAG

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
    asyncio.run(_agent())


async def _agent():
    from agent import create_travel_planner_agent

    try:
        conversation_id = get_current_timestamp()
        config = {"configurable": {"thread_id": conversation_id}}
        logger.info(f"Agent online (conversation id {conversation_id})")
        tp_agent = await create_travel_planner_agent()

        while True:
            user_input = input("> User : ")
            result = await tp_agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                },
                config=config,
            )
            response_message = result["messages"][-1].content
            print("> AI:", response_message[0]["text"])
    except KeyboardInterrupt:
        logger.success("Shutting down agent")
    except Exception as e:
        logger.error(f"{e}")


if __name__ == "__main__":
    app()
