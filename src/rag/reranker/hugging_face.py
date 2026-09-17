import time

from loguru import logger
from sentence_transformers import CrossEncoder

from config import settings
from rag.models import RAGResult
from rag.reranker.base import Reranker


class HuggingFaceReranker(Reranker):
    """GCP Ranking API reranker."""

    def __init__(self):
        self.model = settings.hf_reranker_model_name
        logger.info(f"initializing Hugging Face reranker: model={self.model}")
        t = time.perf_counter()
        self._reranker = CrossEncoder(
            self.model,
            device="cuda",
        )
        logger.info(f"reranker loaded in {(time.perf_counter() - t):.4f} sec")

    def rerank(
        self,
        query: str,
        rag_results: list[RAGResult],
        top_k: int | None = settings.reranked_search_results_limit,
    ) -> list[RAGResult]:
        if not rag_results:
            logger.warning("No documents to rerank, skipping")
            return []
        logger.info(f"reranking {len(rag_results)} documents")

        t = time.perf_counter()
        pairs = [
            (query, rag_result.document.page_content) for rag_result in rag_results
        ]
        rerank_scores = self._reranker.predict(
            pairs, batch_size=settings.reranking_batch_size
        )

        ranked_rag_results: list[RAGResult] = []
        for rag_result, rerank_score in sorted(
            zip(rag_results, rerank_scores),
            key=lambda x: x[1],
            reverse=True,
        ):
            rag_result.rerank_score = float(rerank_score)
            ranked_rag_results.append(rag_result)

        logger.info(f"reranking completed in {(time.perf_counter() - t):.4f} sec")
        return ranked_rag_results[:top_k]


def get_hugging_face_reranker():
    return HuggingFaceReranker()
