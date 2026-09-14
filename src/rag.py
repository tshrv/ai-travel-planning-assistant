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
        if self._reranker == None:
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
        pairs = [
            (query, doc.page_content) for doc, vector_score in similarity_search_results
        ]
        logger.info(f"similarity search results found: {len(pairs)}")

        if settings.reranking_enabled:
            logger.info("reranking")
            reranker = self._get_reranker()
            _t = time.perf_counter()
            rerank_scores = reranker.predict(
                pairs, batch_size=settings.reranking_batch_size
            )
            logger.info(f"reranking completed in {time.perf_counter() - _t} sec")
        else:
            rerank_scores = [
                None for _ in range(settings.similarity_search_results_limit)
            ]

        results = zip(similarity_search_results, rerank_scores)

        if settings.reranking_enabled:
            logger.info("filtering best results based on new ranks")
            results = sorted(
                results,
                key=lambda x: x[1],
                reverse=True,
            )
        results = list(results)
        rag_results: list[RAGResult] = []
        for (doc, vector_score), rerank_score in results[
            : settings.reranked_search_results_limit
        ]:
            rag_results.append(
                RAGResult(
                    document=doc, vector_score=vector_score, rerank_score=rerank_score
                )
            )
        return rag_results
