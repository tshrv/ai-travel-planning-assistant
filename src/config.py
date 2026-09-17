from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings

from embedding.models import EmbeddingProvider
from rag.models import RerankProvider


class Config(BaseSettings):
    # hugging face
    hf_embedding_model_name: str = "BAAI/bge-m3"  # BAAI/bge-m3 | BAAI/bge-large-en-v1.5
    hf_reranker_model_name: str = "BAAI/bge-reranker-v2-m3"

    similarity_search_results_limit: int = 20
    reranked_search_results_limit: int = 5
    reranking_enabled: bool = True
    reranking_batch_size: int = 8  # 8/16/32
    # 8 => 150s
    # 32 => 165s

    # qdrant
    vector_store_url: str = "http://localhost:6333"
    vector_store_collection: str = "aitpa_knowledge_base"
    force_recreate_collection_on_ingestion: bool = True

    # groq
    groq_api_key: str
    groq_model_name: str = "qwen/qwen3.8-27b"
    groq_model_temp: float = 0.2

    # gcp
    gcp_api_key: str
    gcp_project_id: str
    gcp_model_name: str = "gemini-2.5-flash"
    gcp_location: str = "global"
    gcp_temperature: float = 0.2
    gcp_max_tokens: int = 1024
    gcp_embedding_model_name: str = "gemini-embedding-001"
    gcp_reranker_model_name: str = "semantic-ranker-default@latest"

    # mcp
    weather_forecast_mcp_url: str = "http://localhost:8000/mcp"
    currency_converter_mcp_url: str = "http://localhost:8001/mcp"

    # project
    root_dir: ClassVar[Path] = Path(__file__).resolve().parent.parent
    system_prompt_path: ClassVar[Path] = root_dir / "src" / "system_prompt.md"
    embedding_provider: EmbeddingProvider = "hugging_face"  # gcp | hugging_face
    rerank_provider: RerankProvider = "hugging_face"  # gcp | hugging_face


settings = Config()
