# Langfuse Trace Capture - Complete Details

## ✅ Confirmed Working

All traces are now capturing **complete input and output data** and sending to Langfuse Cloud.

## Trace Structure by Tool

### 1. RAG Tool (Document Q&A)

**Main Trace (`rag_query`):**
```json
{
  "name": "rag_query",
  "input": {
    "question": "What is Docling?",
    "k": 2,
    "use_mmr": false,
    "use_rerank": false,
    "eco_mode": false
  },
  "output": {
    "answer": "Docling is a system designed to allow easy extension...",
    "tool_used": "rag",
    "num_sources": 2,
    "num_tokens": 417
  },
  "metadata": {
    "conversation_id": null,
    "filter_document": null
  }
}
```

**Child Spans:**
1. **`tool_routing`**
   - Input: `{"question": "What is Docling?"}`
   - Output: `{"selected_tool": "rag"}`
   - Metadata: `{"routing_logic": "keyword_based"}`

2. **`rag_pipeline`**
   - Input: `{"question": "...", "k": 2, "use_mmr": false, "use_rerank": false}`

3. **`embedding`** (child of `rag_pipeline`)
   - Input: `{"text": "What is Docling?"}`
   - Output: `{"embedding_dim": 384}`

4. **`vector_retrieval`** (child of `rag_pipeline`)
   - Input: `{"method": "similarity", "k": 2, "filter": null}`
   - Output: `{"num_results": 2}`

5. **`llm_generation`** (child of `rag_pipeline`)
   - Input:
     ```json
     {
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "system", "content": "You are a helpful AI assistant. Answer based on the provided context."},
         {"role": "user", "content": "Context from documents:\n[Source 1: ...]...\n\nQuestion: What is Docling?"}
       ],
       "temperature": 0.3,
       "context_chunks": 2,
       "context_length": 1200
     }
     ```
   - Output:
     ```json
     {
       "answer": "Docling is a system designed...",
       "input_tokens": 350,
       "output_tokens": 67,
       "total_tokens": 417
     }
     ```
   - Metadata:
     ```json
     {
       "system_prompt": "You are a helpful AI assistant...",
       "user_question": "What is Docling?",
       "full_context": "[Source 1: docling_paper.pdf - 6 Future work...]...",
       "context_chunks": [
         {
           "filename": "docling_paper.pdf",
           "section": "6 Future work and contributions",
           "content_preview": "Docling is designed to allow easy extension...",
           "score": 0.408
         },
         {
           "filename": "docling_paper.pdf",
           "section": "5 EXPERIMENTS",
           "content_preview": "The primary goal of DocLayNet...",
           "score": 0.254
         }
       ]
     }
     ```

6. **Scores:**
   - `source_1_relevance`: 0.408
   - `source_2_relevance`: 0.254

---

### 2. Direct LLM Tool (Greetings)

**Main Trace (`rag_query`):**
```json
{
  "name": "rag_query",
  "input": {
    "question": "Hello!",
    "k": 5,
    "use_mmr": false,
    "use_rerank": false,
    "eco_mode": false
  },
  "output": {
    "answer": "Hello! How can I assist you today?",
    "tool_used": "direct_llm",
    "num_sources": 0,
    "num_tokens": 29
  }
}
```

**Child Spans:**
1. **`tool_routing`**
   - Output: `{"selected_tool": "direct_llm"}`

2. **`direct_llm`**
   - Input: `{"question": "Hello!", "eco_mode": false}`

3. **`llm_generation`** (child of `direct_llm`)
   - Input:
     ```json
     {
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "system", "content": "You are a helpful AI assistant."},
         {"role": "user", "content": "Hello!"}
       ],
       "temperature": 0.7
     }
     ```
   - Output:
     ```json
     {
       "answer": "Hello! How can I assist you today?",
       "input_tokens": 20,
       "output_tokens": 9,
       "total_tokens": 29
     }
     ```
   - Metadata:
     ```json
     {
       "system_prompt": "You are a helpful AI assistant.",
       "user_question": "Hello!",
       "conversation_context": false
     }
     ```

---

### 3. Web Search Tool (Current Info)

**Main Trace (`rag_query`):**
```json
{
  "name": "rag_query",
  "input": {
    "question": "current weather",
    "k": 5,
    "use_mmr": false,
    "use_rerank": false,
    "eco_mode": false
  },
  "output": {
    "answer": "I couldn't find relevant information on the web.",
    "tool_used": "web_search",
    "num_sources": 0,
    "num_tokens": 0
  }
}
```

**Child Spans:**
1. **`tool_routing`**
   - Output: `{"selected_tool": "web_search"}`

2. **`web_search_pipeline`**
   - Input: `{"question": "current weather", "eco_mode": false}`

3. **`web_search`** (child of `web_search_pipeline`)
   - Input: `{"query": "current weather"}`
   - Output: `{"num_results": 3}`

4. **`llm_generation`** (child of `web_search_pipeline`)
   - Input:
     ```json
     {
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "system", "content": "You are a helpful AI assistant. Answer based on the web search results provided."},
         {"role": "user", "content": "Web search results:\n1. Title: ...\n   Snippet: ...\n\nQuestion: current weather"}
       ],
       "temperature": 0.7,
       "web_results": 3,
       "context_length": 800
     }
     ```
   - Output:
     ```json
     {
       "answer": "Based on the web search results...",
       "input_tokens": 250,
       "output_tokens": 85,
       "total_tokens": 335
     }
     ```
   - Metadata:
     ```json
     {
       "system_prompt": "You are a helpful AI assistant...",
       "user_question": "current weather",
       "web_search_results": [
         {
           "title": "Weather Forecast Example",
           "snippet": "Today's weather is...",
           "link": "https://example.com"
         }
       ],
       "full_context": "Web search results:\n1. ..."
     }
     ```

---

## What's Captured for Evaluation

### ✅ Complete Input
- User question
- All parameters (k, use_mmr, use_rerank, eco_mode)
- Conversation ID and filters

### ✅ Complete Output  
- **Final answer** (the actual response given to the user)
- Tool used (rag/direct_llm/web_search)
- Number of sources used
- Total tokens consumed

### ✅ Full Prompts
- System prompts
- User prompts with context
- Complete message history sent to LLM

### ✅ Context Details
- **RAG**: Full document chunks with filenames, sections, scores
- **Web Search**: Search results with titles, snippets, links
- **Direct LLM**: Conversation history (if any)

### ✅ Performance Metrics
- Token usage (input/output/total)
- Retrieval method (similarity/MMR)
- Reranking status
- Source relevance scores
- Latency per span

---

## Verification Commands

```bash
# Test RAG tool
uv run demo-rag query "What is Docling?" --k 2

# Test Direct LLM
uv run demo-rag query "Hello!"

# Test Web Search
uv run demo-rag query "current weather"
```

All commands show:
```
✓ Langfuse enabled - traces will be sent to Langfuse Cloud
📊 Langfuse trace output: {'answer': '...', 'tool_used': '...', ...}
✓ Langfuse trace sent to cloud
```

---

## Dashboard Access

**URL:** https://cloud.langfuse.com

**What to Look For:**
1. Traces named `rag_query` with complete input/output
2. Nested spans showing execution flow
3. Metadata with full prompts and context
4. Source scores for retrieved documents
5. Token usage and performance metrics

---

## Key Features for Evaluation

1. **Answer Quality**: Full final answers captured in trace output
2. **Prompt Engineering**: See exactly what prompts are sent to LLM
3. **Context Quality**: Review all chunks and their relevance scores
4. **Tool Selection**: Understand which tool was chosen and why
5. **Token Efficiency**: Track token usage across all queries
6. **Performance**: Latency breakdown by operation

**All data needed for comprehensive RAG evaluation is now captured!** 🎯
