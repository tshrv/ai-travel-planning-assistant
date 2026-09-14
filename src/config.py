from pydantic_settings import BaseSettings


class Config(BaseSettings):
    embedding_model_name: str = "BAAI/bge-m3"
    # embedding_model_name: str = "BAAI/bge-large-en-v1.5"
    reranker_model_name: str = "BAAI/bge-reranker-v2-m3"
    similarity_search_results_limit: int = 20
    reranked_search_results_limit: int = 3
    reranking_enabled: bool = False
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


settings = Config()
