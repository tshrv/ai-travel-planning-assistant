from functools import lru_cache

from config import settings
from rag.models import RerankProvider
from rag.reranker.base import Reranker
from rag.reranker.gcp import get_gcp_reranker
from rag.reranker.hugging_face import get_hugging_face_reranker


@lru_cache(maxsize=1)
def get_reranker(
    rerank_provider: RerankProvider = settings.rerank_provider,
) -> Reranker:
    rerank_provider_map = {
        RerankProvider.GCP: get_gcp_reranker,
        RerankProvider.HUGGING_FACE: get_hugging_face_reranker,
    }
    return rerank_provider_map.get(rerank_provider.value)()
