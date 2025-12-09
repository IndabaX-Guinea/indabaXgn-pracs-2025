# Langfuse Observability Setup

Complete guide to add Langfuse tracing to your IndabaX RAG demo.

## 🎯 Quick Setup

### 1. Get Langfuse Credentials

**Option A: Cloud (Recommended for Demo)**
1. Go to [https://cloud.langfuse.com](https://cloud.langfuse.com)
2. Sign up / Log in
3. Create a new project: "IndabaX RAG Demo"
4. Go to **Settings** → **API Keys**
5. Click **Create new API key**
6. Copy the credentials

**Option B: Self-Hosted (Optional)**
```bash
docker run -d -p 3000:3000 \
  -e DATABASE_URL="postgresql://user:password@localhost:5432/langfuse" \
  langfuse/langfuse:latest
```

### 2. Configure Environment

Edit your `.env` file:
```bash
# Langfuse Observability (Optional)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Test the Integration

```bash
cd hands-on-rags-llm-augmented-search
source .venv/bin/activate

# Run a test query
demo-rag query "What is Docling?"

# Check Langfuse dashboard
# You should see a new trace appear!
```

## 📊 What Gets Tracked

With Langfuse enabled, you'll see:

### **Trace Overview**
- **Query**: User's question
- **Tool Used**: direct_llm, web_search, or rag
- **Latency**: Total response time
- **Tokens**: OpenAI token usage
- **Cost**: Estimated cost per query

### **RAG Pipeline Details**
- Embedding generation time
- Vector search results (k, scores)
- Retrieved document chunks
- Reranking (if used)
- LLM generation time

### **Metadata Tracked**
```python
{
    "tool_selected": "rag",
    "k": 3,
    "use_mmr": false,
    "use_rerank": false,
    "eco_mode": false,
    "num_sources": 2,
    "retrieval_method": "similarity",
    "tokens": 418
}
```

## 🎨 Dashboard Features

### **Traces View**
See all queries in real-time:
- User ID (conversation_id)
- Query text
- Response time
- Token count
- Tool used

### **Sessions View**
Track conversation sessions:
- Multiple queries grouped by conversation_id
- Session duration
- Total tokens used
- Cost per session

### **Analytics**
- Average latency per tool
- Token usage trends
- Most common queries
- Error rates

## 🔧 Advanced Configuration

### Custom Trace Names

Update `rag.py` to add custom trace names:

```python
if LANGFUSE_ENABLED:
    trace = langfuse_client.trace(
        name="rag_query",
        user_id=conversation_id or "anonymous",
        metadata={
            "tool": tool,
            "k": k,
            "mmr": use_mmr,
        }
    )
```

### Track Individual Steps

```python
# Track retrieval step
if LANGFUSE_ENABLED:
    span = trace.span(
        name="vector_search",
        input=question,
        metadata={"k": k, "method": "similarity"}
    )
    
# ... do retrieval ...

if LANGFUSE_ENABLED:
    span.end(
        output=results,
        metadata={"num_results": len(results)}
    )
```

### Track Source Quality

```python
# Score each retrieved source
for i, source in enumerate(sources):
    if LANGFUSE_ENABLED:
        trace.score(
            name=f"source_{i+1}_relevance",
            value=source["score"],
            comment=f"{source['filename']} - {source.get('section', 'N/A')}"
        )
```

## 🎯 For Your Demo

### Demo Flow with Langfuse

1. **Start Demo** 
   ```bash
   demo-ui  # Streamlit dashboard
   ```

2. **Show Live Tracing**
   - Open [https://cloud.langfuse.com](https://cloud.langfuse.com) in another browser tab
   - Run queries in Streamlit
   - Show traces appearing in real-time!

3. **Highlight Features**
   - Show different tools being used (RAG vs Web Search vs Direct LLM)
   - Show retrieval scores for each source
   - Show token usage and latency
   - Show session tracking (multiple queries)

### Key Points to Demonstrate

✅ **Transparency**: See exactly what the system is doing
✅ **Performance**: Track latency and identify bottlenecks  
✅ **Cost Tracking**: Monitor OpenAI API usage
✅ **Quality**: Score source relevance
✅ **Debugging**: Identify failed queries or low-quality retrievals

## 🔒 Security Notes

- **Never commit** `.env` file with real credentials
- Use environment variables in production
- Langfuse credentials are in `.env` (gitignored)
- Public key is safe to share, secret key is NOT

## 🐛 Troubleshooting

### "Langfuse not tracking"

Check:
```bash
# Verify credentials are set
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Check if keys are in .env
cat .env | grep LANGFUSE
```

### "ModuleNotFoundError: langfuse"

```bash
# Reinstall
uv pip install langfuse>=2.0.0
```

### "No traces appearing"

1. Check Langfuse project is correct
2. Verify network connection
3. Check Langfuse dashboard project selector
4. Flush traces manually:
   ```python
   if langfuse_client:
       langfuse_client.flush()
   ```

## 📚 Resources

- **Langfuse Docs**: https://langfuse.com/docs
- **OpenAI Integration**: https://langfuse.com/docs/integrations/openai
- **Python SDK**: https://langfuse.com/docs/sdk/python

## 🎬 Demo Script

**"Now let me show you the observability layer..."**

1. Open Langfuse dashboard
2. Run query: "What is Docling?"
3. Show trace appearing in real-time
4. Explain:
   - Tool selection (RAG)
   - Retrieval scores
   - Token usage
   - Latency breakdown

5. Run another query: "What is the weather?"
6. Show different tool (web_search)
7. Compare latencies and costs

8. Show session view
9. Explain conversation tracking

**Impact**: "This gives us complete transparency and helps optimize performance and costs in production."

---

**Langfuse is optional but highly recommended for production deployments and demos!**
