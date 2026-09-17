from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings

chat_gcp = ChatGoogleGenerativeAI(
    model=settings.gcp_model_name,
    project=settings.gcp_project_id,
    location=settings.gcp_location,
    temperature=settings.gcp_temperature,
    max_tokens=settings.gcp_max_tokens,
)
