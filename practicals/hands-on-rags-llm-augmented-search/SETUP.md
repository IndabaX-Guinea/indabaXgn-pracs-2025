# Setup Guide - IndabaX RAG Demo

## ✅ What's Been Created

### Project Structure
```
hands-on-rags-llm-augmented-search/
├── pyproject.toml              # uv + ruff config (ready!)
├── .env.example                # Environment variables template
├── src/demo_indabax/
│   ├── __init__.py
│   ├── document_processor.py  # Docling PDF extraction
│   ├── embeddings.py           # Sentence transformers
│   ├── vector_store.py         # PostgreSQL + pgvector
│   ├── reranker.py             # Cross-encoder reranking
│   ├── conversation.py         # Redis conversation history
│   ├── rag.py                  # Main RAG with tool routing
│   ├── cli.py                  # Click-based CLI
│   └── ui.py                   # Streamlit dashboard ⭐
├── requirements.txt
└── README.md
```

### Key Features Added

1. **pyproject.toml with uv**
   - Based on your traffic-shaping config
   - Ruff linting with same rules
   - Scripts: `demo-rag` (CLI) and `demo-ui` (Streamlit)
   - Environment: "indabaX" (managed by uv)

2. **Streamlit Dashboard** (`ui.py`)
   - Beautiful chat interface
   - Real-time configuration (k, MMR, reranker, eco-mode)
   - Source visualization with highlighting
   - Direct link to Langfuse dashboard
   - Session management
   - Document filtering

3. **Langfuse Integration** (Ready to add)
   - Environment variables configured in `.env.example`
   - Dashboard link in Streamlit UI
   - Need to update `rag.py` with decorators (see below)

## 🚀 Quick Start

### 1. Install uv (if not installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create environment and install dependencies
```bash
cd hands-on-rags-llm-augmented-search

# Create uv environment named "indabaX"
uv venv --python 3.10 .venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### 3. Start PostgreSQL and Redis with Docker
```bash
# Start services (PostgreSQL + pgvector + Redis)
docker-compose up -d

# Check services are running
docker-compose ps

# View logs if needed
docker-compose logs -f
```

### 4. Setup environment variables
```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
```

Required variables:
- `OPENAI_API_KEY` - Your OpenAI key
- `LANGFUSE_PUBLIC_KEY` - From https://cloud.langfuse.com (optional)
- `LANGFUSE_SECRET_KEY` - From https://cloud.langfuse.com (optional)

Database variables (already set in .env.example for Docker):
- `PG_HOST=localhost`
- `PG_PORT=5432`
- `PG_USER=postgres`
- `PG_PASSWORD=postgres`
- `PG_DATABASE=rag_demo`

### 5. Initialize database
```bash
# Initialize with pgvector extension
demo-rag init-db
```

### 6. Ingest a PDF
```bash
demo-rag ingest path/to/your/document.pdf
```

### 7. Launch Streamlit UI
```bash
demo-ui
# Or: streamlit run src/demo-indabaX/ui.py
```

Visit: http://localhost:8501

## 📊 Langfuse Integration (To Complete)

### Step 1: Update `rag.py` with Langfuse decorators

Add to imports:
```python
from langfuse.decorators import observe, langfuse_context
```

Wrap methods with `@observe()`:
```python
class RAGSystem:
    @observe()
    def query(self, question: str, **kwargs):
        langfuse_context.update_current_trace(
            name="rag_query",
            user_id=kwargs.get('conversation_id'),
            metadata={
                "use_mmr": kwargs.get('use_mmr'),
                "use_rerank": kwargs.get('use_rerank'),
                "eco_mode": kwargs.get('eco_mode')
            }
        )
        # ... rest of code
    
    @observe(name="tool_routing")
    def _route_to_tool(self, question: str) -> str:
        # ... code
    
    @observe(name="retrieval")
    def _answer_with_rag(self, question: str, **kwargs):
        # Track retrieval
        langfuse_context.update_current_observation(
            input=question,
            metadata={"k": kwargs.get('k'), "method": "mmr" if kwargs.get('use_mmr') else "similarity"}
        )
        # ... rest of code
```

### Step 2: Add Langfuse initialization

In `ui.py` or `cli.py` startup:
```python
from langfuse import Langfuse

# Initialize
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)
```

### Step 3: View traces

Visit your Langfuse dashboard to see:
- Query latency
- Token usage
- Tool decisions
- Retrieval performance
- Full conversation traces

## 🎨 Streamlit Features

The UI includes:
- **Chat Interface**: Clean, modern chat with history
- **Live Configuration**: Adjust k, MMR, reranking in real-time
- **Source Display**: Expandable cards showing retrieved chunks
- **Metadata**: Tool used, retrieval method, token count
- **Document Filter**: Query specific documents
- **Langfuse Link**: Direct link to observability dashboard
- **Session Management**: Persistent conversation with Redis

## 🧹 Linting & Formatting

```bash
# Format code
uv run ruff format src/

# Lint
uv run ruff check src/

# Fix auto-fixable issues
uv run ruff check src/ --fix

# Type checking
uv run mypy src/
```

## 📝 CLI Commands

```bash
# Initialize database
demo-rag init-db

# Ingest PDF
demo-rag ingest document.pdf

# Query (with options)
demo-rag query "What is this about?" --mmr --rerank --eco-mode

# List documents
demo-rag list-docs

# Search without LLM
demo-rag search "machine learning" --k 3

# View conversation history
demo-rag show-history session-123
```

## 🔧 Development Workflow

1. **Make changes** to Python files
2. **Lint**: `uv run ruff check src/ --fix`
3. **Format**: `uv run ruff format src/`
4. **Test locally**: 
   - CLI: `demo-rag query "test"`
   - UI: `demo-ui`
5. **Check Langfuse** for traces

## 📦 Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Remove dependency
uv remove package-name
```

## 🐛 Troubleshooting

### PostgreSQL connection error
```bash
# Check if Docker containers are running
docker-compose ps

# Restart services
docker-compose restart

# View logs
docker-compose logs postgres

# Stop and remove (if needed)
docker-compose down

# Fresh start
docker-compose up -d
```

### Redis connection error
- Redis is optional
- UI will show warning but continue without conversation history
- Check with: `docker-compose logs redis`

### Langfuse not showing traces
- Check `.env` has correct keys
- Ensure `@observe()` decorators are added
- Check Langfuse dashboard for your project

### Import errors
```bash
# Reinstall
uv pip install -e .
```

## 🎯 Demo Flow (1 Hour)

### Part 1: Setup & Ingestion (10 min)
1. Show project structure
2. Initialize database
3. Ingest sample PDF
4. Show Streamlit UI

### Part 2: Basic Queries (15 min)
1. Simple query in UI
2. Show sources and metadata
3. Compare with/without MMR
4. Show Langfuse traces

### Part 3: Advanced Features (20 min)
1. **Reranking**: Toggle on/off, compare results
2. **Tool Routing**: Ask general vs document questions
3. **Eco Mode**: Show token savings
4. **Conversation**: Multi-turn dialogue

### Part 4: Observability (15 min)
1. **Langfuse Dashboard**: Show traces, latency, costs
2. **Tool Analytics**: Which tools are used most?
3. **Performance**: Identify slow retrievals
4. **Debugging**: Trace a problematic query

## 📊 Metrics to Show in Langfuse

- **Query latency** (embedding + retrieval + LLM)
- **Token usage** per query
- **Tool selection** distribution
- **Retrieval scores** (similarity/MMR)
- **Reranking impact** (score improvements)
- **Cost tracking** (OpenAI API costs)

## 🎓 Key Concepts Demonstrated

1. **Docling**: Structure-aware PDF extraction
2. **PostgreSQL + pgvector**: Efficient vector storage
3. **Sentence Transformers**: Fast, local embeddings
4. **MMR**: Balancing relevance and diversity
5. **Reranking**: Cross-encoder precision
6. **Tool Routing**: Smart decision making
7. **Langfuse**: Production-grade observability
8. **Streamlit**: Rapid UI development

## 📚 Next Steps

1. **Add Langfuse decorators** to `rag.py` (see above)
2. **Ingest your demo PDFs**
3. **Test all features** in Streamlit
4. **Review Langfuse traces**
5. **Prepare talking points** for demo
6. **Optional**: Add evaluation metrics in Langfuse

---

**Note**: The system is 95% complete. Just need to add Langfuse `@observe()` decorators to `rag.py` methods for full observability.

For questions or issues, check the main README.md
