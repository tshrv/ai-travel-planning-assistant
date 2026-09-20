# Project Submission: AI Travel Planning Assistant

## Git Repositories
1. `ai-travel-planning-assistant`: https://github.com/tshrv/ai-travel-planning-assistant
2. `weather-forecast-mcp-server`: https://github.com/tshrv/weather-forecast-mcp-server
3. `currency-converter-mcp-server`: https://github.com/tshrv/currency-converter-mcp-server

## Knowledge-base Documents
1. URLs to source web pages are available at [https://github.com/tshrv/ai-travel-planning-assistant/blob/19995618f2cc5d2ad4f85bb721ce268c6a5556ef/src/ingestion/ingestion.py#L16](https://github.com/tshrv/ai-travel-planning-assistant/blob/19995618f2cc5d2ad4f85bb721ce268c6a5556ef/src/ingestion/ingestion.py#L16)
   ```py
   SOURCES = {
        "singapore": {
            "wiki": "https://en.wikivoyage.org/wiki/Singapore",
            "essential-travel-information": "https://www.visitsingapore.com/travel-tips/essential-travel-information/",
            "solo-travel-to-singapore-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/solo-travel-to-singapore-guide/",
            "singapore-city-tour-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/singapore-city-tour-guide/",
            "7-days-in-singapore": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/7-days-in-singapore/",
            "24-hours-in-singapore": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/24-hours-in-singapore/",
            "singapore-food-guide": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/singapore-food-guide/",
            "places-to-visit-with-family": "https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/places-to-visit-with-family/",
            "top-things-to-do": "https://www.visitsingapore.com/things-to-do/top-things-to-do/",
        }
    }
    ```
2. The contents from the webpages are scraped via command `uv run python src/main.py extract-load-data Singapore` and respective markdown files are created.
3. Follow steps mentioned in `README.md` to set up all required dependencies, as the `extract-load-data` command also generated embeddings and stores data in vector database.
4. **Sample run results** at [https://github.com/tshrv/ai-travel-planning-assistant/tree/main/data/20260918022724](https://github.com/tshrv/ai-travel-planning-assistant/tree/main/data/20260918022724)

## Project Documents
1. `README.md`: [https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md)
2. Architecture: [https://github.com/tshrv/ai-travel-planning-assistant/blob/main/design.excalidraw.png](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/design.excalidraw.png)
3. MCP Tools:
   1. `weather-forecast-mcp-server`: [https://github.com/tshrv/weather-forecast-mcp-server/blob/main/README.md](https://github.com/tshrv/weather-forecast-mcp-server/blob/main/README.md)
   2. `currency-converter-mcp-server`: [https://github.com/tshrv/currency-converter-mcp-server/blob/main/README.md](https://github.com/tshrv/currency-converter-mcp-server/blob/main/README.md)

## RAG workflow
1. **Ingestion**
   1. A headless browser instance opens the provided urls, waits for javascript to render and network to get idle.
   2. All html is downloaded and converted into markdown to retain hierarchial structure
   3. The markdown content is divided into chunks based on splitting on headers 1, 2 and 3 (`#`, `##` and `###`)
   4. These are further chunked, if needed, into `1000` character size chunks with an overlap of `150` characters to retain relevancy with previous chunks.
   5. Each chunks also carries metadata which associates it to other relevant details such as the source url, markdown file path, chunk number, total chunks, a unique id, a source id (based on uid), chunk id (based on source id), location name, label of information type (from seed data)
   ```py
   # metadata
   {
       "Header 1": "Singapore",
       "Header 2": "Talk",
       "chunk_id": "20260918022724_20260918022724_s1_71",
       "source_id": "20260918022724_s1",
       "chunk_index": 71,
       "total_chunks": 414,
       "uid": "20260918022724",
       "name": "singapore",
       "label": "wiki",
       "source_url": "https://en.wikivoyage.org/wiki/Singapore",
       "file_path": "data/20260918022724/singapore_wiki.md"
   }
   ```
   6. Using `gemini-embedding-001` **from GCP** as embedding model (`BAAI/bge-m3` from HuggingFace also available), the page_content is converted into embeddings.
   7. Page content, metadata and embeddings are stored into the vector database (Qdrant).
2. **Retrieval**
   1. The user message is converted into embedding and a similarity search is performed, top `20` results are captured.
   2. These 20 results go though a **GCP reranker** `semantic-ranker-default@latest` (`BAAI/bge-reranker-v2-m3` from Huggingface also avaliable but is slow as it runs locally) and **top 5** reranked results are captured.
   3. These top 5 reranked results from the knowledge base are the final results of the retrieval pipeline.

## Prompt and Context Strategy
1. Prompt: [https://github.com/tshrv/ai-travel-planning-assistant/blob/main/src/agent/system_prompt.md](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/src/agent/system_prompt.md)
2. Context strategy
   1. Chunking: Structure-aware splits of 1,000 characters with 150 overlap. Markdown headings, source URL, and position are kept as metadata.
   2. Retrieval: Dense vector search returns 20 candidates, and a reranker cuts them to the top 5, so only the most relevant chunks reach the model in `source_url + page_content` format. This retrieval can be done iteratively via available `search_knowledge_base` tool.
   3. Live context via tools: Weather forecast, currency exchange, and timezone aware date come from MCP servers and tools rather than the model's memory.
   4. Conversation state: Kept in memory for one agent session only, with nothing persisted across sessions.
   5. Grounding rules: The system prompt strongly instructs to use source url of information used from knowledge base and forbids inventing facts, prices, or live information.
   
## Setup instructions
1. Detailed setup instructions at
   1. `ai-travel-planning-assistant`: [https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md#installation](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md#installation)
   2. `weather-forecast-mcp-server`: [https://github.com/tshrv/weather-forecast-mcp-server/blob/main/README.md#running-with-docker](https://github.com/tshrv/weather-forecast-mcp-server/blob/main/README.md#running-with-docker)
   3. `currency-converter-mcp-server`: [https://github.com/tshrv/currency-converter-mcp-server/blob/main/README.md#docker](https://github.com/tshrv/currency-converter-mcp-server/blob/main/README.md#docker)
2. The **weather forecast** and **currency converter** mcp servers can be run via their `docker-compose.yaml` files, their dependencies require no API keys.
3. Qdrant runs on docker
4. For **LLM**
   1. The project was built with both **GCP** `gemini-2.5-flash` and **Groq** `qwen/qwen3.8-27b`, but current version works with GCP only due to strict rate limits with Groq free tier.
   2. GCP setup is required before running. Step by step instructions available in [gcp_setup.md](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/gcp_setup.md)
5. For **Embedding** and **Reranking**
   1. Best performace is observed via GCP Agent Platform and Reranking API, which required setting up `gcloud` cli, enabling services and granting permissions. Step by step instructions available in [gcp_setup.md](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/gcp_setup.md)
   2. While setup, one can switch to HuggingFace models, running them locally with GPU, however, observed performance is very slow, specially with reranking (with my PC's specs, yours may differ).
   3. To use HuggingFace, update your `.env` with `EMBEDDING_PROVIDER=hugging_face` and `RERANK_PROVIDER=hugging_face`, as they default to GCP.
6. Commands to run **(CLI only)**
   1. Download and ingest data: `uv run python src/main.py extract-load-data Singapore`
   2. Inspect RAG search: `uv run python src/main.py rag-search`
   3. Start session with agent: `uv run python src/main.py agent`
   4. Detailed steps at [https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md#usage](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/README.md#usage)

## Sample Conversations
[sample_chats.md](https://github.com/tshrv/ai-travel-planning-assistant/blob/main/sample_chats.md) contains 4 conversations.
1. RAG search + weather mcp + currency mcp + conversation history
   1. Conversation #1
   2. Conversation #2
   3. Conversation #3
   4. Conversation #4
2. Tool failure handling
   1. Conversation #4