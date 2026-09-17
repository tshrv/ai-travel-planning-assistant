from abc import ABC, abstractmethod

from rag.models import RAGResult


class Reranker(ABC):
    """Abstract base class for document rerankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[RAGResult],
        top_k: int | None = None,
    ) -> list[RAGResult]:
        """Rerank a list of documents based on relevance to a query.

        Args:
            query: The input search query string.
            documents: List of LangChain Document objects to rerank.
            top_k: Optional maximum number of top results to return.

        Returns:
            list[RAGResult]
        """
