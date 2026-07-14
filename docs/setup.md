# Local Setup

This guide sets up ParaRAG as a local Python module, without the API server. A server-based setup is available as an alternative at the end.

## Prerequisites

- Git
- Python 3.11
- Docker with Docker Compose, used to run Qdrant
- An OpenAI API key

## 1. Clone the Repository

```bash
git clone https://github.com/Adamczewski22/Para-RAG.git
cd Para-RAG
```

## 2. Configure the Environment

Create the local environment file:

```bash
cp .env.example .env
```

Open `.env` and set `OPENAI_API_KEY`. The other values have suitable local defaults:

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Required for LLM and embedding requests. |
| `QDRANT_URL` | Qdrant endpoint; Docker Compose overrides this for the API container. |
| `RETRIEVAL_COUNT` | Maximum number of memories returned per retrieval query. |
| `FOR_LOCOMO` | Enables LOCOMO-specific storage behavior; keep `false` for normal use. |
| `LANGSMITH_TRACING` | Enables optional LangSmith tracing. |

## 3. Install ParaRAG Dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements/core.txt
```

Run commands from the repository root while this virtual environment is active.

## 4. Start Qdrant

ParaRAG stores memories in Qdrant. Start only the Qdrant service:

```bash
docker compose up -d qdrant
docker compose ps qdrant
```

Its dashboard is available at <http://localhost:6333/dashboard>. Data is persisted in the `qdrant_storage` Docker volume.

## 5. Run the Chatbot Example

```bash
python -m examples.chatbot_integration
```

Enter messages at the prompt and enter `exit` to stop the chatbot. The example uses ParaRAG directly in the Python process; no ParaRAG server is involved.

ParaRAG uses embedded SQLite for profile storage, so no additional database service is required. Local profile data is created under `infra/sqlite/`.

When finished, stop Qdrant with:

```bash
docker compose stop qdrant
```

## Server Setup (Alternative)

The API server exposes ParaRAG over HTTP. The simplest server setup runs both the API and Qdrant with Docker Compose:

```bash
docker compose up --build -d
docker compose ps
```

Once both services are running:

- API documentation: <http://localhost:8000/docs>
- Qdrant dashboard: <http://localhost:6333/dashboard>

Follow server logs with `docker compose logs -f pararag-server`. Stop the stack with `docker compose down`. Qdrant data remains in a Docker volume; `docker compose down -v` also deletes that local data.

To run the server in the local Python environment instead, install its additional dependencies and start Uvicorn:

```bash
python -m pip install -r requirements/server.txt
docker compose up -d qdrant
uvicorn pararag_server.endpoints:app --host 0.0.0.0 --port 8000
```
