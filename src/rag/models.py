from enum import Enum

from langchain_core.documents import Document
from pydantic import BaseModel


class RerankProvider(str, Enum):
    GCP = "gcp"
    HUGGING_FACE = "hugging_face"


class RAGResult(BaseModel):
    document: Document
    vector_score: float
    rerank_score: float | None = None
