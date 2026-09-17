import time
from functools import lru_cache

from langchain.embeddings import Embeddings
from loguru import logger

from config import settings
from embedding.models import EmbeddingProvider


@lru_cache(maxsize=1)
def get_embedddings(
    embedding_provider: EmbeddingProvider = settings.embedding_provider,
) -> Embeddings:
    """Get embedding model"""
    logger.info(f"initializing embeddings model: {embedding_provider.value}")
    _start_time = time.perf_counter()
    embedding_provider_map = {
        EmbeddingProvider.GCP: _get_gcp_embeddings,
        EmbeddingProvider.HUGGING_FACE: _get_hugging_face_embeddings,
    }
    embeddings = embedding_provider_map.get(embedding_provider.value)()
    logger.info(f"completed in {time.perf_counter() - _start_time}")
    return embeddings


def _get_hugging_face_embeddings():
    """Get embedding model from Hugging Face"""
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        # TODO: benchmark BGE-M3 vs BGE-large
        model_name=settings.hf_embedding_model_name,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return embeddings


def _get_gcp_embeddings():
    """Get embedding model from GCP"""
    from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.gcp_embedding_model_name,
        project=settings.gcp_project_id,
        location=settings.gcp_location,
    )
    return embeddings
