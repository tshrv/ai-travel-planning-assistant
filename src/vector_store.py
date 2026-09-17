from langchain.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import exceptions
from qdrant_client.models import Distance, VectorParams

from config import settings
from embedding.embeddings import get_embedddings
from embedding.models import EmbeddingProvider


def _get_client():
    """Create a client for Qdrant"""
    return QdrantClient(url=settings.vector_store_url)


def _get_dense_vectors_size() -> int:
    """Get dense vector size based on embedding provider and model"""
    ep = settings.embedding_provider.value
    dense_vectors_size_map = {
        EmbeddingProvider.GCP: 3072,
        EmbeddingProvider.HUGGING_FACE: 1024,
    }
    dense_vectors_size = dense_vectors_size_map.get(ep)
    logger.info(f"Vector collection size {dense_vectors_size} for provider {ep}")
    return dense_vectors_size


def create_collection(
    force_recreate: bool = settings.force_recreate_collection_on_ingestion,
):
    """Create a new collection in vector db"""
    try:
        client = _get_client()
        if force_recreate:
            # delete if exists
            deleted: bool = client.delete_collection(
                collection_name=settings.vector_store_collection
            )
            logger.info(
                f"deleted collection {settings.vector_store_collection} : {deleted}"
            )
        client.create_collection(
            collection_name=settings.vector_store_collection,
            vectors_config=VectorParams(
                size=_get_dense_vectors_size(),
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"created collection {settings.vector_store_collection}")
    except exceptions.UnexpectedResponse as e:
        logger.error(
            f"failed to create collection {settings.vector_store_collection}: {e}"
        )


def get_vector_store() -> QdrantVectorStore:
    """Controller for vector database"""
    embeddings: Embeddings = get_embedddings()
    vector_store = QdrantVectorStore(
        client=_get_client(),
        embedding=embeddings,
        collection_name=settings.vector_store_collection,
    )
    return vector_store
