from enum import Enum


class EmbeddingProvider(str, Enum):
    GCP = "gcp"
    HUGGING_FACE = "hugging_face"
