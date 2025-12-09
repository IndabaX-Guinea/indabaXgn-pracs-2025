"""
Optional Reranker Module - Small cross-encoder for better ranking
Using cross-encoder/ms-marco-MiniLM-L-6-v2 (lightweight, fast)
"""

from typing import Any

from sentence_transformers import CrossEncoder


class Reranker:
    """Lightweight reranker for improving retrieval results"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker model

        Args:
            model_name: HuggingFace cross-encoder model
                - ms-marco-MiniLM-L-6-v2: Fast, good quality (default)
                - ms-marco-MiniLM-L-12-v2: Slower, better quality
        """
        print(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
        print("Reranker model loaded!")

    def rerank(
        self, query: str, documents: list[tuple[dict[str, Any], float]], top_k: int = 5
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Rerank documents based on query relevance

        Args:
            query: Search query
            documents: List of (doc, score) tuples from initial retrieval
            top_k: Number of documents to return after reranking

        Returns:
            Reranked list of (doc, rerank_score) tuples
        """
        if not documents:
            return []

        # Prepare pairs for cross-encoder
        pairs = [[query, doc[0]["content"]] for doc in documents]

        # Get reranking scores
        scores = self.model.predict(pairs)

        # Combine documents with new scores
        reranked = [(doc[0], float(score)) for doc, score in zip(documents, scores, strict=False)]

        # Sort by score (descending) and return top_k
        reranked.sort(key=lambda x: x[1], reverse=True)

        return reranked[:top_k]
