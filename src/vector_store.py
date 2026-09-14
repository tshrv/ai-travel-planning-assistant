from langchain.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import exceptions
from qdrant_client.models import Distance, VectorParams

from config import settings
from embeddings import get_embedddings


def _get_client():
    """Create a client for Qdrant"""
    return QdrantClient(url=settings.vector_store_url)


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
                size=1024,
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
