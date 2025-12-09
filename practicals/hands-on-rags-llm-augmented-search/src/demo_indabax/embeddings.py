"""
Embeddings Module - Small, efficient HuggingFace model for demo
Using sentence-transformers/all-MiniLM-L6-v2 (384 dimensions, very fast)
"""

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Lightweight embedding model for RAG demo"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model

        Args:
            model_name: HuggingFace model name
                - all-MiniLM-L6-v2: 384 dim, very fast (default)
                - all-MiniLM-L12-v2: 384 dim, more accurate
                - paraphrase-multilingual-MiniLM-L12-v2: 384 dim, multilingual
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded! Embedding dimension: {self.dimension}")

    def embed_text(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """
        Generate embeddings for text(s)

        Args:
            text: Single text string or list of texts

        Returns:
            Single embedding or list of embeddings
        """
        embeddings = self.model.encode(text, convert_to_numpy=True)

        # Convert to list format for PostgreSQL
        if isinstance(text, str):
            return embeddings.tolist()
        else:
            return [emb.tolist() for emb in embeddings]

    def embed_documents(self, texts: list[str], show_progress: bool = True) -> list[list[float]]:
        """
        Batch embed multiple documents efficiently

        Args:
            texts: List of document texts
            show_progress: Show progress bar

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=show_progress, batch_size=32)
        return [emb.tolist() for emb in embeddings]
