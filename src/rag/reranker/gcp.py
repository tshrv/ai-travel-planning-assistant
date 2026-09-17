from google.cloud import discoveryengine_v1 as discoveryengine
from loguru import logger

from config import settings
from rag.models import RAGResult
from rag.reranker.base import Reranker


class GCPReranker(Reranker):
    """GCP Ranking API reranker."""

    def __init__(self):
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location
        self.model = settings.gcp_reranker_model_name

        logger.info(
            f"initializing Vertex reranker: model={self.model}, location={self.location}"
        )

        self.client = discoveryengine.RankServiceClient()

        self.ranking_config = self.client.ranking_config_path(
            project=self.project_id,
            location=self.location,
            ranking_config="default_ranking_config",
        )

    def rerank(
        self,
        query: str,
        rag_results: list[RAGResult],
        top_k: int | None = settings.reranked_search_results_limit,
    ) -> list[RAGResult]:
        if not rag_results:
            logger.warning("No documents to rerank, skipping")
            return []

        records = [
            discoveryengine.RankingRecord(
                id=str(i),
                title=rag_result.document.metadata.get("source_url"),
                content=rag_result.document.page_content,
            )
            for i, rag_result in enumerate(rag_results)
        ]

        request = discoveryengine.RankRequest(
            ranking_config=self.ranking_config,
            model=self.model,
            query=query,
            records=records,
            top_n=top_k or len(records),
            ignore_record_details_in_response=True,
        )

        response = self.client.rank(request=request)
        reranked_rag_results: list[RAGResult] = []
        for record in response.records:
            rag_result = rag_results[int(record.id)]
            rag_result.rerank_score = float(record.score)
            reranked_rag_results.append(rag_result)

        return reranked_rag_results


def get_gcp_reranker():
    return GCPReranker()
