import time

from langchain_core.retrievers import BaseRetriever
from loguru import logger

from config import settings
from rag.models import Document, RAGResult
from rag.reranker.base import Reranker
from rag.reranker.reranker import get_reranker
from vector_store import get_vector_store


class RAG:
    def __init__(self):
        self._vector_store = get_vector_store()
        self._reranker = None

    def _get_reranker(self) -> Reranker:
        if self._reranker is None:
            self._reranker = get_reranker()
        return self._reranker

    def search(self, query: str) -> list[RAGResult]:
        """Search vector store against query"""
        logger.info("similarity based lookup")
        similarity_search_results = self._vector_store.similarity_search_with_score(
            query,
            k=settings.similarity_search_results_limit,
        )
        logger.info(
            f"similarity search results found: {len(similarity_search_results)}"
        )
        similarity_search_rag_results = [
            RAGResult(document=doc, vector_score=vector_score)
            for doc, vector_score in similarity_search_results
        ]
        if settings.reranking_enabled:
            _t = time.perf_counter()
            ranked_results = self._get_reranker().rerank(
                query, similarity_search_rag_results
            )

        else:
            ranked_results = similarity_search_rag_results

        return ranked_results


class RAGRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str) -> Document:
        results = RAG().search(query)
        return [result.document for result in results]
