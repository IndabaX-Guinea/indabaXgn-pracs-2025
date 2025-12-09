"""
PostgreSQL Vector Store with pgvector
Simplified version inspired by Itnovem's postgresql_db_client.py
"""

import json
from typing import Any

import psycopg
from pgvector.psycopg import Vector, register_vector
from psycopg.rows import dict_row


class VectorStore:
    """Simple PostgreSQL vector store with pgvector extension"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "rag_demo",
        user: str = "postgres",
        password: str = "postgres",
        schema: str = "public",
        table: str = "documents",
    ):
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.schema = schema
        self.table = table
        self.vector_size = None  # Will be set when first embedding is added

    def initialize(self, vector_size: int = 384):
        """Create table with pgvector extension"""
        self.vector_size = vector_size

        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Enable pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                # Create schema if not exists
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")

                # Create table
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.{self.table} (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        content TEXT NOT NULL,
                        metadata JSONB NOT NULL,
                        embedding vector({vector_size}) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)

                # Create index for vector similarity search (using cosine distance)
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table}_embedding_idx
                    ON {self.schema}.{self.table}
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)

                # Create GIN index for metadata searches (like document name)
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.table}_metadata_idx
                    ON {self.schema}.{self.table}
                    USING GIN (metadata);
                """)

                conn.commit()

    def insert_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """
        Insert document chunks with embeddings

        Args:
            chunks: List of dicts with 'content', 'metadata', 'embedding'

        Returns:
            Number of chunks inserted
        """
        with psycopg.connect(self.connection_string) as conn:
            # Register vector type
            register_vector(conn)
            with conn.cursor() as cur:
                for chunk in chunks:
                    cur.execute(
                        f"""
                        INSERT INTO {self.schema}.{self.table}
                        (content, metadata, embedding)
                        VALUES (%s, %s, %s)
                    """,
                        (
                            chunk["content"],
                            json.dumps(chunk["metadata"]),
                            chunk["embedding"],
                        ),
                    )
                conn.commit()

        return len(chunks)

    def similarity_search(
        self,
        query_embedding: list[float],
        k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Perform similarity search using cosine similarity

        Args:
            query_embedding: Query vector
            k: Number of results to return
            filter_metadata: Optional metadata filter (e.g., {'filename': 'doc.pdf'})

        Returns:
            List of (chunk, similarity_score) tuples
        """
        with psycopg.connect(self.connection_string, row_factory=dict_row) as conn:
            # Register vector type
            register_vector(conn)
            with conn.cursor() as cur:
                # Build query
                where_clause = ""
                params = [query_embedding, k]

                if filter_metadata:
                    # Build JSONB containment filter
                    where_clause = "WHERE metadata @> %s"
                    params.insert(0, json.dumps(filter_metadata))

                query = f"""
                    SELECT
                        id,
                        content,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM {self.schema}.{self.table}
                    {where_clause}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """

                if filter_metadata:
                    cur.execute(
                        query,
                        (
                            json.dumps(filter_metadata),
                            Vector(query_embedding),
                            Vector(query_embedding),
                            k,
                        ),
                    )
                else:
                    cur.execute(query, (Vector(query_embedding), Vector(query_embedding), k))

                results = cur.fetchall()

                return [(dict(row), row["similarity"]) for row in results]

    def mmr_search(
        self,
        query_embedding: list[float],
        k: int = 5,
        lambda_mult: float = 0.5,
        fetch_k: int = 20,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Maximal Marginal Relevance search for diversity

        Args:
            query_embedding: Query vector
            k: Number of results to return
            lambda_mult: Balance between relevance (1.0) and diversity (0.0)
            fetch_k: Number of candidates to consider
            filter_metadata: Optional metadata filter

        Returns:
            List of (chunk, score) tuples
        """

        with psycopg.connect(self.connection_string, row_factory=dict_row) as conn:
            # Register vector type
            register_vector(conn)
            with conn.cursor() as cur:
                # Build WHERE clause
                where_clause = ""
                if filter_metadata:
                    where_clause = "WHERE metadata @> %s::jsonb"

                # 1. Get initial candidates (fetch_k most similar)
                query = f"""
                    SELECT
                        id,
                        content,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity
                    FROM {self.schema}.{self.table}
                    {where_clause}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """

                if filter_metadata:
                    cur.execute(
                        query,
                        (
                            json.dumps(filter_metadata),
                            Vector(query_embedding),
                            Vector(query_embedding),
                            fetch_k,
                        ),
                    )
                else:
                    cur.execute(query, (Vector(query_embedding), Vector(query_embedding), fetch_k))

                candidates = cur.fetchall()

                if not candidates:
                    return []

                # 2. Simple MMR: Select diverse results
                # Start with the most similar document
                selected = [candidates[0]]
                remaining = candidates[1:]

                # 3. Iteratively select documents that maximize MMR score
                while len(selected) < k and remaining:
                    mmr_scores = []

                    for candidate in remaining:
                        # Relevance to query (already have similarity score)
                        relevance = candidate["similarity"]

                        # Max similarity to already selected docs (diversity penalty)
                        # For simplicity, use content length difference as proxy
                        max_sim_to_selected = 0
                        for sel in selected:
                            # Simple diversity: penalize similar content lengths
                            len_diff = abs(len(candidate["content"]) - len(sel["content"]))
                            similarity = 1.0 / (1.0 + len_diff / 100)  # Normalize
                            max_sim_to_selected = max(max_sim_to_selected, similarity)

                        # MMR score: balance relevance and diversity
                        mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_sim_to_selected
                        mmr_scores.append((candidate, mmr_score))

                    # Select document with highest MMR score
                    if mmr_scores:
                        best_candidate, best_score = max(mmr_scores, key=lambda x: x[1])
                        selected.append(best_candidate)
                        remaining.remove(best_candidate)

                # 4. Format results
                results = []
                for doc in selected[:k]:
                    chunk = {
                        "id": doc["id"],
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                    }
                    results.append((chunk, doc["similarity"]))

                return results

    def count_chunks(self, filename: str | None = None) -> int:
        """Count chunks, optionally filtered by filename"""
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                if filename:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {self.schema}.{self.table} WHERE metadata->>'filename' = %s",
                        (filename,),
                    )
                else:
                    cur.execute(f"SELECT COUNT(*) FROM {self.schema}.{self.table}")
                return cur.fetchone()[0]

    def get_all_documents(self) -> list[str]:
        """Get all unique document filenames"""
        with psycopg.connect(self.connection_string, row_factory=dict_row) as conn:
            # Register vector type
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT DISTINCT metadata->>'filename' as filename
                    FROM {self.schema}.{self.table}
                    ORDER BY filename
                """)
                return [row["filename"] for row in cur.fetchall() if row["filename"]]

    def delete_document(self, filename: str) -> int:
        """Delete all chunks from a document"""
        with psycopg.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"DELETE FROM {self.schema}.{self.table} WHERE metadata->>'filename' = %s",
                    (filename,),
                )
                conn.commit()
                return cur.rowcount
