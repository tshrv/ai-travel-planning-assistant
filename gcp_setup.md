# 1. Pick your project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable Vertex AI
gcloud services enable aiplatform.googleapis.com

# 3. Authenticate
gcloud auth application-default login

# 4. Set quota project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 5. Install SDK
uv add google-genai

# 6. Test direct Vertex AI
uv run python test_vertex.py

# 7. Install LangChain integration
uv add langchain-google-vertexai

# 8. Test LangChain
uv run python test_llm.py