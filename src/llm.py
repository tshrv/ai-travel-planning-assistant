from langchain_groq import ChatGroq

from config import settings

llm = ChatGroq(
    model=settings.groq_model_name,
    temperature=settings.groq_model_temp,
    api_key=settings.groq_api_key,
    max_completion_tokens=800,
    reasoning_effort="none",
)
