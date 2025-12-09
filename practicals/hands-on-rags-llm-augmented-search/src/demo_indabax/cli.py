#!/usr/bin/env python3
"""
RAG Demo CLI - Simple command-line interface for all operations
Using Click for clean, demo-friendly CLI
"""

import sys
from pathlib import Path

import click
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from conversation import ConversationManager
from document_processor import DocumentProcessor
from embeddings import EmbeddingModel
from rag import RAGSystem
from reranker import Reranker
from vector_store import VectorStore


# Global configuration
class Config:
    """Shared configuration"""

    def __init__(self):
        self.embedding_model = None
        self.vector_store = None
        self.reranker = None
        self.conversation_manager = None
        self.rag_system = None


config = Config()


def init_components(use_reranker: bool = False):
    """Lazy initialization of components"""
    if not config.embedding_model:
        config.embedding_model = EmbeddingModel()

    if not config.vector_store:
        config.vector_store = VectorStore()

    if use_reranker and not config.reranker:
        config.reranker = Reranker()

    if not config.conversation_manager:
        try:
            config.conversation_manager = ConversationManager()
        except Exception as e:
            click.echo(f"Warning: Could not connect to Redis: {e}", err=True)
            config.conversation_manager = None

    if not config.rag_system:
        config.rag_system = RAGSystem(
            embedding_model=config.embedding_model,
            vector_store=config.vector_store,
            conversation_manager=config.conversation_manager,
            reranker=config.reranker,
        )


@click.group()
def cli():
    """RAG Demo CLI - Simple Retrieval Augmented Generation System"""
    pass


@cli.command()
@click.option("--vector-size", default=384, help="Vector embedding dimension")
def init_db(vector_size):
    """Initialize PostgreSQL database with pgvector"""
    click.echo("Initializing database...")
    store = VectorStore()
    store.initialize(vector_size=vector_size)
    click.echo(f"✓ Database initialized with vector size {vector_size}")


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--chunk-size", default=512, help="Chunk size in characters")
@click.option("--chunk-overlap", default=50, help="Overlap between chunks")
def process_pdf(pdf_path, chunk_size, chunk_overlap):
    """Extract and display chunks from a PDF"""
    click.echo(f"Processing PDF: {pdf_path}")

    processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = processor.process_pdf(pdf_path)

    click.echo(f"\n✓ Extracted {len(chunks)} chunks\n")

    for i, chunk in enumerate(chunks[:3], 1):  # Show first 3
        click.echo(f"--- Chunk {i} ---")
        click.echo(f"Section: {chunk['metadata'].get('section', 'N/A')}")
        click.echo(f"Content: {chunk['content'][:200]}...")
        click.echo()

    if len(chunks) > 3:
        click.echo(f"... and {len(chunks) - 3} more chunks")


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--chunk-size", default=512, help="Chunk size in characters")
@click.option("--chunk-overlap", default=50, help="Overlap between chunks")
def ingest(pdf_path, chunk_size, chunk_overlap):
    """Process PDF and insert into vector database"""
    click.echo(f"Ingesting PDF: {pdf_path}")

    # Initialize components
    init_components()

    # Process PDF
    click.echo("1. Extracting and chunking PDF...")
    processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = processor.process_pdf(pdf_path)
    click.echo(f"   ✓ Extracted {len(chunks)} chunks")

    # Generate embeddings
    click.echo("2. Generating embeddings...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = config.embedding_model.embed_documents(texts, show_progress=True)

    # Combine
    for chunk, embedding in zip(chunks, embeddings, strict=False):
        chunk["embedding"] = embedding

    # Insert into database
    click.echo("3. Inserting into vector database...")
    count = config.vector_store.insert_chunks(chunks)
    click.echo(f"   ✓ Inserted {count} chunks into database")

    click.echo(f"\n✓ Ingestion complete for {Path(pdf_path).name}")


@cli.command()
@click.option("--filename", help="Filter by document filename")
def list_docs(filename):
    """List documents in the vector store"""
    init_components()

    if filename:
        count = config.vector_store.count_chunks(filename)
        click.echo(f"Document: {filename}")
        click.echo(f"Chunks: {count}")
    else:
        docs = config.vector_store.get_all_documents()
        click.echo(f"Total documents: {len(docs)}\n")

        for doc in docs:
            count = config.vector_store.count_chunks(doc)
            click.echo(f"- {doc}: {count} chunks")


@cli.command()
@click.argument("filename")
def delete_doc(filename):
    """Delete a document from the vector store"""
    init_components()

    if click.confirm(f'Delete all chunks from "{filename}"?'):
        count = config.vector_store.delete_document(filename)
        click.echo(f"✓ Deleted {count} chunks from {filename}")


@cli.command()
@click.argument("question")
@click.option("--conversation-id", help="Conversation ID for history")
@click.option("--k", default=5, help="Number of chunks to retrieve")
@click.option("--mmr/--no-mmr", default=False, help="Use MMR for diversity")
@click.option("--rerank/--no-rerank", default=False, help="Use reranker")
@click.option("--eco-mode/--no-eco-mode", default=False, help="Concise answers")
@click.option("--document", help="Filter by document filename")
@click.option("--show-sources/--no-show-sources", default=True, help="Show sources")
def query(question, conversation_id, k, mmr, rerank, eco_mode, document, show_sources):
    """Ask a question using RAG"""
    init_components(use_reranker=rerank)

    click.echo(f"Question: {question}\n")

    result = config.rag_system.query(
        question=question,
        conversation_id=conversation_id,
        k=k,
        use_mmr=mmr,
        use_rerank=rerank,
        eco_mode=eco_mode,
        filter_document=document,
    )

    click.echo(f"Answer: {result['answer']}\n")

    if show_sources and result["sources"]:
        click.echo(f"Sources ({len(result['sources'])}):")
        for i, source in enumerate(result["sources"], 1):
            click.echo(f"\n{i}. {source['filename']} - {source.get('section', 'N/A')} (score: {source['score']:.3f})")
            click.echo(f"   {source['content']}")

    click.echo("\nMetadata:")
    click.echo(f"  Tool: {result['tool_used']}")
    if "retrieval_method" in result:
        click.echo(f"  Retrieval: {result['retrieval_method']}")
    if "reranked" in result:
        click.echo(f"  Reranked: {result['reranked']}")
    click.echo(f"  Tokens: {result['num_tokens']}")


@cli.command()
@click.argument("conversation_id")
def show_history(conversation_id):
    """Show conversation history"""
    try:
        conv_mgr = ConversationManager()
        history = conv_mgr.get_history(conversation_id)

        if not history:
            click.echo(f"No history found for conversation: {conversation_id}")
            return

        click.echo(f"Conversation: {conversation_id}\n")
        for msg in history:
            role = msg["role"].upper()
            content = msg["content"]
            timestamp = msg["timestamp"]
            click.echo(f"[{timestamp}] {role}:")
            click.echo(f"{content}\n")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def list_conversations():
    """List all active conversations"""
    try:
        conv_mgr = ConversationManager()
        convs = conv_mgr.list_conversations()

        if not convs:
            click.echo("No active conversations")
        else:
            click.echo(f"Active conversations: {len(convs)}\n")
            for conv_id in convs:
                history = conv_mgr.get_history(conv_id, limit=1)
                last_msg = history[-1] if history else None
                if last_msg:
                    click.echo(f"- {conv_id} (last message: {last_msg['timestamp']})")
                else:
                    click.echo(f"- {conv_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("question")
@click.option("--k", default=5, help="Number of chunks to retrieve")
@click.option("--document", help="Filter by document")
def search(question, k, document):
    """Search for similar chunks (without LLM)"""
    init_components()

    click.echo(f"Searching for: {question}\n")

    # Embed question
    query_embedding = config.embedding_model.embed_text(question)

    # Search
    filter_metadata = {"filename": document} if document else None
    results = config.vector_store.similarity_search(query_embedding, k=k, filter_metadata=filter_metadata)

    click.echo(f"Found {len(results)} results:\n")

    for i, (doc, score) in enumerate(results, 1):
        metadata = doc["metadata"]
        click.echo(f"{i}. Score: {score:.3f}")
        click.echo(f"   File: {metadata.get('filename', 'Unknown')}")
        click.echo(f"   Section: {metadata.get('section', 'N/A')}")
        click.echo(f"   Content: {doc['content'][:200]}...")
        click.echo()


if __name__ == "__main__":
    cli()
