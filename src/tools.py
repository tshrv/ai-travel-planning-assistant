from datetime import datetime, timedelta, timezone

from langchain.tools import tool
from loguru import logger

from rag import RAG

rag = RAG()


@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for tourism information relevant to the user's question."""
    logger.info(f"search_knowledge_base: {query}")
    results = rag.search(query)
    logger.info(f"search_knowledge_base: {len(results)} results")
    if not results:
        return "No relevant information was found in the knowledge base."
    context = "\n\n---\n\n".join(
        f"""
Source URL: {result.document.metadata.get("source_url", "Unknown")}
{result.document.page_content}"""
        for result in results
    )
    return context


@tool
def datetime_now(timezone_offset_hour: int = 0, timezone_offset_minute: int = 0) -> str:
    """Get timezone aware today's date in isoformat (YYYY-MM-DD). Provide hour and minute offset as  timezone_offset_hour and timezone_offset_minute (both default to 0) for specific timezone, other than UTC"""
    logger.info(
        f"fetching today's date: offset_hour {timezone_offset_hour}, offset_minute {timezone_offset_minute}"
    )
    dt = datetime.now(
        tz=timezone(
            offset=timedelta(hours=timezone_offset_hour, minutes=timezone_offset_minute)
        )
    )
    return dt.date().isoformat()
