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
