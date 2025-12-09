# Simple RAG Demo for IndabaX

A clean, minimal implementation of Retrieval Augmented Generation (RAG) for a 1-hour demonstration. Built with completely opensource tools and inspired by production patterns from Itnovem's IA Factory.

## Features

- **PDF Extraction**: Docling for clean, structured text extraction
- **Vector Storage**: PostgreSQL with pgvector for efficient similarity search
- **Embeddings**: Small, fast sentence-transformers models (384 dimensions)
- **Smart Retrieval**: 
  - Similarity search
  - MMR (Maximal Marginal Relevance) for diversity
  - Optional reranking with cross-encoders
- **Tool Routing**: Intelligent decision between RAG and direct LLM responses
- **Conversation History**: Redis-based chat history with context
- **CLI Interface**: Clean Click-based CLI for all operations

## Architecture

```
├── document_processor.py   # PDF extraction & chunking (Docling)
├── embeddings.py           # Sentence transformers embeddings
├── vector_store.py         # PostgreSQL + pgvector client
├── reranker.py             # Optional cross-encoder reranking
├── conversation.py         # Redis conversation history
├── rag.py                  # Main RAG orchestration with tool routing
└── cli.py                  # Command-line interface
```

## Prerequisites

1. **PostgreSQL with pgvector**:
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Install pgvector extension
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

2. **Redis** (optional, for conversation history):
```bash
brew install redis
brew services start redis
```

3. **Python 3.9+**
```bash
python --version  # Should be 3.9 or higher
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Setup

1. **Initialize Database**:
```bash
python src/cli.py init-db --vector-size 384
```

2. **Set OpenAI API Key**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### 1. Ingest a PDF Document

```bash
# Process and ingest a PDF
python src/cli.py ingest path/to/document.pdf

# With custom chunking
python src/cli.py ingest path/to/document.pdf --chunk-size 512 --chunk-overlap 50
```

### 2. Query the System

```bash
# Basic query
python src/cli.py query "What is the main topic of the document?"

# With MMR for diversity
python src/cli.py query "Explain the methodology" --mmr

# With reranking for better relevance
python src/cli.py query "What are the key findings?" --rerank

# Eco mode (concise answers, fewer tokens)
python src/cli.py query "Summarize the conclusion" --eco-mode

# Filter by document
python src/cli.py query "What is discussed?" --document report.pdf

# With conversation history
python src/cli.py query "Tell me more" --conversation-id session-123
```

### 3. Search Without LLM

```bash
# Just find similar chunks
python src/cli.py search "machine learning applications" --k 3
```

### 4. Manage Documents

```bash
# List all documents
python src/cli.py list-docs

# Check specific document
python src/cli.py list-docs --filename report.pdf

# Delete a document
python src/cli.py delete-doc report.pdf
```

### 5. Conversation Management

```bash
# View conversation history
python src/cli.py show-history session-123

# List all conversations
python src/cli.py list-conversations
```

### 6. Preview PDF Processing

```bash
# See how a PDF will be chunked (without ingesting)
python src/cli.py process-pdf path/to/document.pdf
```

## Demo Flow (1 Hour)

### Part 1: Setup & Ingestion (15 min)

1. Show architecture diagram
2. Initialize database
3. Process a sample PDF and show chunks
4. Ingest the PDF into vector store
5. List documents to verify

### Part 2: Basic RAG (15 min)

1. Simple query without RAG (direct LLM)
2. Query with RAG - show sources
3. Search command to show raw similarity search
4. Explain metadata (sections, scores)

### Part 3: Advanced Features (15 min)

1. **MMR**: Show difference with/without MMR
   ```bash
   python src/cli.py query "research methods" 
   python src/cli.py query "research methods" --mmr
   ```

2. **Reranking**: Compare with/without reranking
   ```bash
   python src/cli.py query "conclusion" 
   python src/cli.py query "conclusion" --rerank
   ```

3. **Tool Routing**: Show how system chooses tools
   ```bash
   python src/cli.py query "Hello, how are you?"  # Direct LLM
   python src/cli.py query "What does the document say?"  # RAG
   ```

### Part 4: Conversation & Eco Mode (15 min)

1. Start a conversation
   ```bash
   python src/cli.py query "What is this about?" --conversation-id demo-1
   python src/cli.py query "Tell me more" --conversation-id demo-1
   python src/cli.py show-history demo-1
   ```

2. Eco mode comparison
   ```bash
   python src/cli.py query "Explain the findings"
   python src/cli.py query "Explain the findings" --eco-mode
   ```

## Key Concepts Demonstrated

1. **Document Processing**: Docling's structure-aware extraction
2. **Chunking Strategy**: Semantic chunking with overlap
3. **Vector Embeddings**: Sentence transformers (384D)
4. **Similarity Search**: Cosine similarity via pgvector
5. **MMR**: Balancing relevance and diversity
6. **Reranking**: Cross-encoder for precision
7. **Tool Routing**: Smart decision making
8. **Conversation Context**: Redis-based history
9. **Metadata**: Tracking sources, sections, scores

## Configuration

### Embedding Models

Default: `sentence-transformers/all-MiniLM-L6-v2` (384 dim, very fast)

Alternatives in `src/embeddings.py`:
- `all-MiniLM-L12-v2`: More accurate, slightly slower
- `paraphrase-multilingual-MiniLM-L12-v2`: Multilingual support

### Reranker Models

Default: `cross-encoder/ms-marco-MiniLM-L-6-v2` (fast)

Alternative in `src/reranker.py`:
- `ms-marco-MiniLM-L-12-v2`: Better quality, slower

### Database Connection

Edit in source files or use environment variables:
```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_DATABASE=rag_demo
export PG_USER=postgres
export PG_PASSWORD=postgres

export REDIS_HOST=localhost
export REDIS_PORT=6379
```

## Comparison with Itnovem IA Factory

This demo simplifies several production features:

| Feature | IA Factory | This Demo |
|---------|-----------|-----------|
| Vector DB | PostgreSQL + pgvector | Same |
| Search | Hybrid (vector + FTS) + RRF | Vector only |
| Metadata | Complex authorization | Simple (filename, section) |
| Tools | LangGraph ReAct Agent | Simple routing |
| History | Redis with vector search | Redis with simple storage |
| Reranking | LLM + Sagemaker | Cross-encoder |
| Observability | Langfuse tracing | None |
| API | Flask REST | CLI only |

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
brew services list

# Restart if needed
brew services restart postgresql@15
```

### Redis Connection Error
```bash
# Check Redis
brew services list

# The system works without Redis (conversation history disabled)
```

### Model Download Issues
```bash
# Models auto-download on first use
# Ensure internet connection and sufficient disk space (~1GB)
```

### Out of Memory
```bash
# Reduce batch size in embeddings.py
# Or use CPU instead of GPU for sentence-transformers
```

## License

MIT License - Educational purposes

## Credits

- Inspired by Itnovem's IA Factory RAG implementation
- Built for IndabaX presentation
- Uses opensource tools: Docling, PostgreSQL, pgvector, sentence-transformers
