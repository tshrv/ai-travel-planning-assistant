import time
from functools import lru_cache

from langchain.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

from config import settings


@lru_cache(maxsize=1)
def get_embedddings() -> Embeddings:
    """Get embedding model"""
    logger.info("initializing HF embeddings model")
    _start_time = time.perf_counter()
    hf_embeddings = HuggingFaceEmbeddings(
        # TODO: benchmark BGE-M3 vs BGE-large
        # model_name="BAAI/bge-m3",
        model_name=settings.embedding_model_name,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    logger.info(f"completed in {time.perf_counter() - _start_time}")

    return hf_embeddings
