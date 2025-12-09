#!/usr/bin/env python3
"""
Test script to verify vector operations work correctly
"""

import sys
from pathlib import Path


# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


from demo_indabax.embeddings import EmbeddingModel
from demo_indabax.vector_store import VectorStore


def test_vector_operations():
    """Test vector store operations"""
    print("Testing vector operations...")

    # Initialize components
    vector_store = VectorStore()
    embedding_model = EmbeddingModel()

    # Initialize database
    print("Initializing database...")
    vector_store.initialize(vector_size=384)

    # Create test data
    test_chunks = [
        {
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
            "metadata": {"filename": "test.pdf", "chunk_index": 0},
            "embedding": embedding_model.embed_text(
                "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed."
            ),
        },
        {
            "content": "Deep learning uses neural networks with multiple layers to process complex patterns in data.",
            "metadata": {"filename": "test.pdf", "chunk_index": 1},
            "embedding": embedding_model.embed_text(
                "Deep learning uses neural networks with multiple layers to process complex patterns in data."
            ),
        },
        {
            "content": "Natural language processing helps computers understand and generate human language.",
            "metadata": {"filename": "test.pdf", "chunk_index": 2},
            "embedding": embedding_model.embed_text(
                "Natural language processing helps computers understand and generate human language."
            ),
        },
    ]

    # Insert test data
    print("Inserting test chunks...")
    count = vector_store.insert_chunks(test_chunks)
    print(f"Inserted {count} chunks")

    # Test similarity search
    print("Testing similarity search...")
    query = "What is machine learning?"
    query_embedding = embedding_model.embed_text(query)

    results = vector_store.similarity_search(query_embedding, k=2)
    print(f"Found {len(results)} results for query: '{query}'")

    for _i, (_chunk, _score) in enumerate(results):
        print(".3f")

    # Test MMR search
    print("Testing MMR search...")
    mmr_results = vector_store.mmr_search(query_embedding, k=2, lambda_mult=0.5)
    print(f"Found {len(mmr_results)} MMR results")

    for _i, (_chunk, _score) in enumerate(mmr_results):
        print(".3f")

    print("✅ All vector operations working correctly!")


if __name__ == "__main__":
    test_vector_operations()
