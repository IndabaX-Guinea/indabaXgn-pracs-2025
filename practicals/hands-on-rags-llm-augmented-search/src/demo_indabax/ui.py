#!/usr/bin/env python3
"""
Streamlit UI for RAG Demo with Langfuse Integration
Beautiful, simple interface for querying documents
"""

import os
from datetime import datetime

import streamlit as st
from conversation import ConversationManager
from dotenv import load_dotenv

# Import our RAG components
from embeddings import EmbeddingModel
from rag import RAGSystem
from reranker import Reranker
from vector_store import VectorStore


# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="IndabaX RAG Demo", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-card {
        background-color: #1e1e1e;
        color: #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .source-card b {
        color: #4db8ff;
    }
    .source-card small {
        color: #a0a0a0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def init_rag_system():
    """Initialize RAG components (cached)"""
    with st.spinner("Initializing RAG system..."):
        embedding_model = EmbeddingModel()
        vector_store = VectorStore()

        # Optional components
        reranker = None
        conversation_manager = None

        if st.session_state.get("use_reranker", False):
            reranker = Reranker()

        try:
            conversation_manager = ConversationManager()
        except:
            st.warning("Redis not available - conversation history disabled")

        rag_system = RAGSystem(
            embedding_model=embedding_model,
            vector_store=vector_store,
            conversation_manager=conversation_manager,
            reranker=reranker,
        )

    return rag_system, vector_store


def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")

        # Langfuse link
        if os.getenv("LANGFUSE_HOST"):
            st.markdown(
                f"""
            <div class="metric-card">
                <b>📊 Langfuse Dashboard</b><br>
                <a href="{os.getenv("LANGFUSE_HOST")}" target="_blank">
                    View Traces & Analytics →
                </a>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Retrieval settings
        st.markdown("#### Retrieval Settings")
        k = st.slider("Number of chunks (k)", 1, 10, 5)
        use_mmr = st.checkbox("Use MMR (diversity)", value=False)
        use_rerank = st.checkbox("Use Reranker", value=False)

        st.markdown("---")

        # LLM settings
        st.markdown("#### LLM Settings")
        eco_mode = st.checkbox("Eco Mode (concise)", value=False)

        st.markdown("---")

        # Conversation
        st.markdown("#### Conversation")
        use_conversation = st.checkbox("Enable history", value=True)
        if use_conversation:
            conversation_id = st.text_input(
                "Session ID",
                value=st.session_state.get("conversation_id", f"session-{datetime.now().strftime('%Y%m%d-%H%M')}"),
            )
            st.session_state["conversation_id"] = conversation_id

            if st.button("🗑️ Clear History"):
                st.session_state.pop("messages", None)
                st.success("History cleared!")
                st.rerun()

        st.markdown("---")

        # Document filter
        st.markdown("#### Document Filter")
        try:
            _, vector_store = init_rag_system()
            docs = vector_store.get_all_documents()
            filter_doc = st.selectbox("Filter by document", options=["All documents", *docs])
            filter_doc = None if filter_doc == "All documents" else filter_doc
        except:
            filter_doc = None

        st.markdown("---")
        st.markdown("### 📚 Documents")
        if st.button("🔄 Refresh"):
            st.cache_resource.clear()
            st.rerun()

    # Main area
    st.markdown('<div class="main-header">🤖 IndabaX RAG Demo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Ask questions about your documents with advanced RAG features</div>',
        unsafe_allow_html=True,
    )

    # Initialize system
    rag_system, vector_store = init_rag_system()

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_docs = len(vector_store.get_all_documents())
        st.metric("Documents", total_docs)
    with col2:
        total_chunks = vector_store.count_chunks()
        st.metric("Total Chunks", total_chunks)
    with col3:
        st.metric("Retrieval", "MMR" if use_mmr else "Similarity")
    with col4:
        st.metric("Reranking", "✓" if use_rerank else "✗")

    st.markdown("---")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander(f"📄 Sources ({len(message['sources'])})"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(
                            f"""
                        <div class="source-card">
                            <b>Source {i}</b> - {source["filename"]}<br>
                            <small>Section: {source.get("section", "N/A")} | Score: {source["score"]:.3f}</small><br>
                            <p style="margin-top: 0.5rem;">{source["content"]}</p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = rag_system.query(
                    question=prompt,
                    conversation_id=st.session_state.get("conversation_id") if use_conversation else None,
                    k=k,
                    use_mmr=use_mmr,
                    use_rerank=use_rerank,
                    eco_mode=eco_mode,
                    filter_document=filter_doc,
                )

                # Display answer
                st.markdown(result["answer"])

                # Show metadata
                with st.expander("ℹ️ Metadata"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tool Used", result["tool_used"])
                    with col2:
                        method = result.get("retrieval_method", "N/A")
                        st.metric("Retrieval", method)
                    with col3:
                        st.metric("Tokens", result["num_tokens"])

                # Show sources
                if result["sources"]:
                    with st.expander(f"📄 Sources ({len(result['sources'])})"):
                        for i, source in enumerate(result["sources"], 1):
                            st.markdown(
                                f"""
                            <div class="source-card">
                                <b>Source {i}</b> - {source["filename"]}<br>
                                <small>Section: {source.get("section", "N/A")} | Score: {source["score"]:.3f}</small><br>
                                <p style="margin-top: 0.5rem;">{source["content"]}</p>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

        # Save assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"], "sources": result["sources"]}
        )

    # Langfuse link in footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>
            Powered by Docling, PostgreSQL + pgvector, Sentence Transformers, OpenAI
            <br>
            Observability by <a href="https://langfuse.com" target="_blank">Langfuse</a>
        </small>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
