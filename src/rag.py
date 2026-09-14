import time

from loguru import logger
from sentence_transformers import CrossEncoder

from config import settings
from models import RAGResult
from vector_store import get_vector_store


class RAG:
    def __init__(self):
        self._vector_store = get_vector_store()
        self._reranker = None

    def _get_reranker(self) -> CrossEncoder:
        if self._reranker is None:
            logger.info("initializing reranker")
            t = time.perf_counter()
            self._reranker = CrossEncoder(
                settings.reranker_model_name,
                device="cuda",
            )
            logger.info(f"reranker loaded in {(time.perf_counter() - t):.4f} sec")
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

        if settings.reranking_enabled:
            logger.info("reranking")
            pairs = [
                (query, doc.page_content)
                for doc, vector_score in similarity_search_results
            ]

            reranker = self._get_reranker()
            _t = time.perf_counter()
            rerank_scores = reranker.predict(
                pairs, batch_size=settings.reranking_batch_size
            )
            logger.info(f"reranking completed in {time.perf_counter() - _t} sec")

            logger.info("filtering best results based on new ranks")
            ranked_results = sorted(
                zip(similarity_search_results, rerank_scores),
                key=lambda x: x[1],
                reverse=True,
            )

        else:
            ranked_results = [(result, None) for result in similarity_search_results]

        return [
            RAGResult(
                document=doc, vector_score=vector_score, rerank_score=rerank_score
            )
            for (doc, vector_score), rerank_score in ranked_results[
                : settings.reranked_search_results_limit
            ]
        ]
