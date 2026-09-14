from vector_store import get_vector_store


def search(phrase: str):
    """Search vector store against phrase"""
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(
        query=phrase,
        k=5,
    )
    return results
