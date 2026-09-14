from pydantic_settings import BaseSettings


class Config(BaseSettings):
    embedding_model_name: str = "BAAI/bge-m3"
    # embedding_model_name: str = "BAAI/bge-large-en-v1.5"

    # qdrant
    vector_store_url: str = "http://localhost:6333"
    vector_store_collection: str = "aitpa_knowledge_base"
    force_recreate_collection_on_ingestion: bool = True


settings = Config()
