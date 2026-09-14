from pathlib import Path

from langchain_core.documents import Document
from pydantic import BaseModel


class Source(BaseModel):
    uid: str
    source_id: str
    name: str
    label: str
    url: str
    file_path: Path | None = None
    chunks: list[Document] = []


class RAGResult(BaseModel):
    document: Document
    vector_score: float
    rerank_score: float | None
