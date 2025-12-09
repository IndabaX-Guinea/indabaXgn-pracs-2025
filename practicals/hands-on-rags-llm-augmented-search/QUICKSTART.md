# Quick Start Guide

## Prerequisites
- Docker installed and running
- Python 3.10+
- uv package manager

## Setup (5 minutes)

### 1. Install uv (if needed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and setup environment
```bash
cd /Users/ahmedbalde/projects/00000/demo-indabaX

# Create virtual environment
uv venv --python 3.10 .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### 3. Start Docker services
```bash
# IMPORTANT: Stop local PostgreSQL if running
brew services stop postgresql@15

# Start PostgreSQL (with pgvector) and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
# Both should show status: "Up X seconds (healthy)"
```

### 4. Setup environment
```bash
# Copy template
cp .env.example .env

# Edit and add your OpenAI key
nano .env  # or use your preferred editor
```

**Required:**
- `OPENAI_API_KEY=sk-your-key-here`

**Optional (for Langfuse observability):**
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST`

### 5. Initialize database
```bash
demo-rag init-db
```

Expected output: `✓ Database initialized with vector size 384`

### 6. Ingest a document
```bash
demo-rag ingest path/to/your/document.pdf
```

### 7. Launch Streamlit UI
```bash
demo-ui
```

Visit: **http://localhost:8501**

## Quick Test (CLI)

```bash
# Query with basic settings
demo-rag query "What is this document about?"

# Query with MMR for diversity
demo-rag query "What are the main topics?" --mmr

# Query with reranking for precision
demo-rag query "Tell me about X" --rerank

# Query with eco mode (concise answers)
demo-rag query "Summarize the document" --eco-mode

# All features combined
demo-rag query "What is X?" --mmr --rerank --eco-mode --k 5
```

## Management Commands

```bash
# List ingested documents
demo-rag list-docs

# Delete a document
demo-rag delete-doc "filename.pdf"

# Search without LLM (just retrieval)
demo-rag search "keyword" --k 3

# View conversation history
demo-rag show-history <session-id>

# Clear conversation
demo-rag clear-history <session-id>
```

## Stopping Services

```bash
# Stop Docker containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove with volumes (full cleanup)
docker-compose down -v
```

## Troubleshooting

### "role postgres does not exist"
You have local PostgreSQL running on port 5432:
```bash
# Stop it
brew services stop postgresql@15

# Or change Docker port in docker-compose.yml:
# ports: - "5433:5432"  # Use 5433 on host
# Then update .env: PG_PORT=5433
```

### Docker containers not starting
```bash
# Check logs
docker-compose logs postgres
docker-compose logs redis

# Restart
docker-compose restart
```

### Import errors
```bash
# Reinstall package
uv pip install -e .
```

### Can't connect to Redis
Redis is optional - the app will work without it (no conversation history).

## Project Structure

```
demo-indabaX/
├── docker-compose.yml         # PostgreSQL + Redis
├── .env                       # Your API keys
├── pyproject.toml             # Dependencies
└── src/demo_indabax/
    ├── cli.py                # CLI commands
    ├── ui.py                 # Streamlit interface
    ├── rag.py                # RAG system
    ├── vector_store.py       # PostgreSQL + pgvector
    ├── embeddings.py         # Sentence transformers
    ├── reranker.py           # Cross-encoder
    ├── conversation.py       # Redis history
    └── document_processor.py # Docling PDF extraction
```

## Next Steps

1. **Test the UI** - Run `demo-ui` and try different configurations
2. **Add Langfuse** - Follow SETUP.md for observability setup
3. **Ingest demo PDFs** - Prepare documents for your presentation
4. **Practice demo flow** - See SETUP.md for 1-hour demo structure

## Demo Features to Showcase

1. **Docling** - Structure-aware PDF extraction (better than PyPDF2)
2. **PostgreSQL + pgvector** - Production-ready vector storage
3. **MMR** - Maximal Marginal Relevance for diverse results
4. **Reranking** - Cross-encoder for improved precision
5. **Tool Routing** - Smart decision: RAG vs direct LLM
6. **Eco Mode** - Token optimization
7. **Streamlit UI** - Modern, interactive interface
8. **Langfuse** - Observability and tracing (if setup)

## Support

- Full setup guide: `SETUP.md`
- Project README: `README.md`
- Langfuse integration: `SETUP.md` section "Langfuse Integration"
