"""
RAG Orchestration Module with Tool Routing
Inspired by Itnovem's tool-based approach
"""

import os
from typing import Any

from dotenv import load_dotenv


# Load environment variables
load_dotenv()

from conversation import ConversationManager
from embeddings import EmbeddingModel
from openai import OpenAI
from reranker import Reranker
from vector_store import VectorStore
from web_search import WebSearchTool


# Optional Langfuse integration
try:
    from langfuse import Langfuse

    # Only initialize if keys are present
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if public_key and secret_key:
        langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com"),
        )
        LANGFUSE_ENABLED = True
        print(
            f"✓ Langfuse enabled - traces will be sent to {langfuse_client._client_wrapper._base_url if hasattr(langfuse_client, '_client_wrapper') else 'Langfuse Cloud'}"
        )
    else:
        langfuse_client = None
        LANGFUSE_ENABLED = False
except Exception:
    langfuse_client = None
    LANGFUSE_ENABLED = False


class RAGSystem:
    """Main RAG orchestrator with tool routing capabilities"""

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        conversation_manager: ConversationManager | None = None,
        reranker: Reranker | None = None,
        llm_api_key: str | None = None,
        llm_model: str = "gpt-3.5-turbo",
        enable_web_search: bool = True,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.conversation_manager = conversation_manager
        self.reranker = reranker

        # LLM client (OpenAI-compatible)
        self.llm = OpenAI(api_key=llm_api_key or os.getenv("OPENAI_API_KEY"))
        self.llm_model = llm_model

        # Web search tool (optional fallback)
        self.web_search = WebSearchTool() if enable_web_search else None

    def query(
        self,
        question: str,
        conversation_id: str | None = None,
        k: int = 5,
        use_mmr: bool = False,
        use_rerank: bool = False,
        eco_mode: bool = False,
        filter_document: str | None = None,
    ) -> dict[str, Any]:
        """
        Main query method with intelligent tool routing

        Args:
            question: User question
            conversation_id: Optional conversation ID for history
            k: Number of chunks to retrieve
            use_mmr: Use MMR for diverse results
            use_rerank: Use reranker for better relevance
            eco_mode: Concise answers (fewer tokens)
            filter_document: Optional document filename filter

        Returns:
            Dict with answer, sources, and metadata
        """
        # Start Langfuse trace
        main_trace = None
        if LANGFUSE_ENABLED:
            # Create a trace and get the span object
            main_trace = langfuse_client.start_span(
                name="rag_query",
                input={
                    "question": question,
                    "k": k,
                    "use_mmr": use_mmr,
                    "use_rerank": use_rerank,
                    "eco_mode": eco_mode,
                },
                metadata={"conversation_id": conversation_id, "filter_document": filter_document},
            )

        # Decide which tool to use
        tool = self._route_to_tool(question)

        # Log tool routing decision
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="tool_routing",
                input={"question": question},
                output={"selected_tool": tool},
                metadata={"routing_logic": "keyword_based"},
            ).end()

        # Route to appropriate tool
        if tool == "direct_llm":
            result = self._answer_directly(question, conversation_id, eco_mode)
        elif tool == "web_search":
            result = self._answer_with_web_search(question, conversation_id, eco_mode)
        elif tool == "rag":
            result = self._answer_with_rag(
                question,
                conversation_id,
                k,
                use_mmr,
                use_rerank,
                eco_mode,
                filter_document,
            )
        else:  # fallback to RAG
            result = self._answer_with_rag(
                question,
                conversation_id,
                k,
                use_mmr,
                use_rerank,
                eco_mode,
                filter_document,
            )

        # End trace with result
        if main_trace:
            trace_output = {
                "answer": result["answer"],
                "tool_used": result["tool_used"],
                "num_sources": len(result.get("sources", [])),
                "num_tokens": result.get("num_tokens", 0),
            }
            main_trace.update(output=trace_output)
            main_trace.end()
            langfuse_client.flush()

        return result

    def _route_to_tool(self, question: str) -> str:
        """
        Intelligent tool routing logic

        Returns:
            'direct_llm', 'web_search', or 'rag'
        """
        question_lower = question.lower()

        # 1. Direct LLM for greetings (no context needed)
        greeting_keywords = ["hello", "hi", "hey", "thank", "thanks", "good morning", "good evening"]
        if any(kw in question_lower for kw in greeting_keywords):
            return "direct_llm"

        # 2. Web Search for real-time/current information
        web_search_keywords = [
            "weather",
            "temperature",
            "forecast",
            "news",
            "today",
            "current",
            "latest",
            "recent",
            "price",
            "stock",
            "market",
            "who is the current",
            "who won",
            "when did",
            "what happened",
        ]
        if any(kw in question_lower for kw in web_search_keywords):
            return "web_search"

        # 3. RAG for document-specific questions
        rag_keywords = ["document", "pdf", "according to", "in the", "from the", "docling", "paper"]
        if any(kw in question_lower for kw in rag_keywords):
            return "rag"

        # 4. Default to RAG (try documents first)
        return "rag"

    def _answer_directly(self, question: str, conversation_id: str | None, eco_mode: bool) -> dict[str, Any]:
        """Answer without RAG (direct LLM)"""

        # Start span for direct LLM
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(name="direct_llm", input={"question": question, "eco_mode": eco_mode})

        messages = []

        # Add conversation history if available
        if conversation_id and self.conversation_manager:
            messages = self.conversation_manager.format_for_llm(conversation_id, limit=3)
        else:
            messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

        # Add eco mode instruction
        if eco_mode:
            messages[0]["content"] += " Be concise and direct in your answers."

        messages.append({"role": "user", "content": question})

        # Call LLM
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="llm_generation",
                input={
                    "model": self.llm_model,
                    "messages": messages,
                    "temperature": 0.7,
                },
                metadata={
                    "system_prompt": messages[0]["content"] if messages else "",
                    "user_question": question,
                    "conversation_context": len(messages) > 1,
                },
            )

        response = self.llm.chat.completions.create(model=self.llm_model, messages=messages, temperature=0.7)

        answer = response.choices[0].message.content

        # Update span with result
        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(
                output={
                    "answer": answer,
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            )

        # Save to conversation history
        if conversation_id and self.conversation_manager:
            self.conversation_manager.add_message(conversation_id, "user", question)
            self.conversation_manager.add_message(conversation_id, "assistant", answer)

        return {
            "answer": answer,
            "sources": [],
            "tool_used": "direct_llm",
            "num_tokens": response.usage.total_tokens,
        }

    def _answer_with_rag(
        self,
        question: str,
        conversation_id: str | None,
        k: int,
        use_mmr: bool,
        use_rerank: bool,
        eco_mode: bool,
        filter_document: str | None,
    ) -> dict[str, Any]:
        """Answer using RAG pipeline"""

        # Start span for RAG
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="rag_pipeline",
                input={"question": question, "k": k, "use_mmr": use_mmr, "use_rerank": use_rerank},
            )

        # 1. Embed question
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(name="embedding", input={"text": question})
        query_embedding = self.embedding_model.embed_text(question)
        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(output={"embedding_dim": len(query_embedding)})

        # 2. Retrieve documents
        filter_metadata = {"filename": filter_document} if filter_document else None

        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="vector_retrieval",
                input={"method": "mmr" if use_mmr else "similarity", "k": k, "filter": filter_metadata},
            )

        if use_mmr:
            # MMR for diversity
            results = self.vector_store.mmr_search(
                query_embedding,
                k=k,
                lambda_mult=0.5,
                fetch_k=k * 4,
                filter_metadata=filter_metadata,
            )
        else:
            # Standard similarity search
            results = self.vector_store.similarity_search(
                query_embedding,
                k=k * 2 if use_rerank else k,  # Fetch more if reranking
                filter_metadata=filter_metadata,
            )

        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(output={"num_results": len(results)})

        # 3. Optional reranking
        if use_rerank and self.reranker and results:
            if LANGFUSE_ENABLED:
                langfuse_client.start_span(name="reranking", input={"num_docs": len(results)})
            results = self.reranker.rerank(question, results, top_k=k)
            if LANGFUSE_ENABLED:
                langfuse_client.update_current_span(output={"num_reranked": len(results)})

        # If no relevant results from RAG, return empty
        if not results:
            return {
                "answer": "I couldn't find relevant information in the documents.",
                "sources": [],
                "tool_used": "rag",
                "retrieval_method": "similarity",
                "reranked": False,
                "num_tokens": 0,
            }

        # 4. Format context
        context = self._format_context(results)

        # 5. Build prompt with conversation history
        messages = []
        if conversation_id and self.conversation_manager:
            messages = self.conversation_manager.format_for_llm(conversation_id, limit=2, include_system=False)

        system_prompt = "You are a helpful AI assistant. Answer based on the provided context."
        if eco_mode:
            system_prompt += " Be concise and direct."

        messages.insert(0, {"role": "system", "content": system_prompt})

        user_prompt = f"""Context from documents:
{context}

Question: {question}

Answer based on the context above. If the context doesn't contain relevant information, say so."""

        messages.append({"role": "user", "content": user_prompt})

        # 6. Generate answer
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="llm_generation",
                input={
                    "model": self.llm_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "context_chunks": len(results),
                    "context_length": len(context),
                },
                metadata={
                    "system_prompt": system_prompt,
                    "user_question": question,
                    "full_context": context,
                    "context_chunks": [
                        {
                            "filename": doc["metadata"].get("filename"),
                            "section": doc["metadata"].get("section"),
                            "content_preview": doc["content"][:200] + "...",
                            "score": score,
                        }
                        for doc, score in results
                    ],
                },
            )

        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.3,  # Lower temp for factual answers
        )

        answer = response.choices[0].message.content

        # Update LLM span with result
        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(
                output={
                    "answer": answer,
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            )

        # 7. Extract sources
        sources = [
            {
                "content": doc["content"][:200] + "...",
                "filename": doc["metadata"].get("filename"),
                "section": doc["metadata"].get("section"),
                "score": score,
            }
            for doc, score in results
        ]

        # Score each source in Langfuse
        if LANGFUSE_ENABLED:
            for i, (_doc, score) in enumerate(results):
                langfuse_client.score_current_trace(name=f"source_{i + 1}_relevance", value=float(score))

        # 8. Save to conversation history
        if conversation_id and self.conversation_manager:
            self.conversation_manager.add_message(
                conversation_id,
                "user",
                question,
                metadata={"sources_used": len(sources)},
            )
            self.conversation_manager.add_message(conversation_id, "assistant", answer, metadata={"sources": sources})

        return {
            "answer": answer,
            "sources": sources,
            "tool_used": "rag",
            "retrieval_method": "mmr" if use_mmr else "similarity",
            "reranked": use_rerank and self.reranker is not None,
            "num_tokens": response.usage.total_tokens,
        }

    def _answer_with_web_search(
        self,
        question: str,
        conversation_id: str | None,
        eco_mode: bool,
    ) -> dict[str, Any]:
        """Answer using web search for real-time/current information"""

        # Start span for web search
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(name="web_search_pipeline", input={"question": question, "eco_mode": eco_mode})

        print("🌐 Searching the web for current information...")

        # 1. Search the web
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(name="web_search", input={"query": question})
        search_results = self.web_search.search(question, max_results=3)
        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(output={"num_results": len(search_results)})

        if not search_results:
            return {
                "answer": "I couldn't find relevant information on the web.",
                "sources": [],
                "tool_used": "web_search",
                "num_tokens": 0,
            }

        # 2. Format search results as context
        context = self.web_search.format_results_for_context(search_results)

        # 3. Build prompt
        messages = []
        if conversation_id and self.conversation_manager:
            messages = self.conversation_manager.format_for_llm(conversation_id, limit=2, include_system=False)

        system_prompt = "You are a helpful AI assistant. Answer based on the web search results provided."
        if eco_mode:
            system_prompt += " Be concise and direct."

        messages.insert(0, {"role": "system", "content": system_prompt})

        user_prompt = f"""{context}

Question: {question}

Answer based on the web search results above."""

        messages.append({"role": "user", "content": user_prompt})

        # 4. Generate answer
        if LANGFUSE_ENABLED:
            langfuse_client.start_span(
                name="llm_generation",
                input={
                    "model": self.llm_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "web_results": len(search_results),
                    "context_length": len(context),
                },
                metadata={
                    "system_prompt": system_prompt,
                    "user_question": question,
                    "web_search_results": [
                        {
                            "title": result["title"],
                            "snippet": result["snippet"][:200] + "...",
                            "link": result["link"],
                        }
                        for result in search_results
                    ],
                    "full_context": context,
                },
            )

        response = self.llm.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.3,  # Lower temp for factual answers
        )

        answer = response.choices[0].message.content

        # Update LLM span with result
        if LANGFUSE_ENABLED:
            langfuse_client.update_current_span(
                output={
                    "answer": answer,
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            )

        # 5. Format sources for display
        sources = [
            {
                "filename": "Web Search",
                "section": result["title"],
                "content": result["snippet"][:200] + "...",
                "score": 1.0 - (i * 0.1),  # Decreasing score
                "link": result["link"],
            }
            for i, result in enumerate(search_results)
        ]

        # Save to conversation history
        if conversation_id and self.conversation_manager:
            self.conversation_manager.add_message(
                conversation_id,
                "user",
                question,
                metadata={"web_search": True},
            )
            self.conversation_manager.add_message(
                conversation_id,
                "assistant",
                answer,
                metadata={"sources": sources, "from_web": True},
            )

        return {
            "answer": answer,
            "sources": sources,
            "tool_used": "web_search",
            "num_tokens": response.usage.total_tokens,
        }

    def _format_context(self, results: list[tuple[dict[str, Any], float]]) -> str:
        """Format retrieved chunks as context"""
        formatted = []
        for i, (doc, score) in enumerate(results, 1):
            metadata = doc["metadata"]
            source_info = f"[Source {i}: {metadata.get('filename', 'Unknown')}"
            if metadata.get("section"):
                source_info += f" - {metadata['section']}"
            source_info += f" (relevance: {score:.2f})]"

            formatted.append(f"{source_info}\n{doc['content']}\n")

        return "\n".join(formatted)
