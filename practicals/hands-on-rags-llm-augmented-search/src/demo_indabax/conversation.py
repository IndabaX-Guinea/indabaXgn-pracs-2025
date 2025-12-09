"""
Conversation History Manager using Redis
Simplified version inspired by Itnovem's redis_client.py
"""

import json
from datetime import datetime
from typing import Any

import redis


class ConversationManager:
    """Simple Redis-based conversation history"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int = 0,
    ):
        self.client = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
        self.ttl = 3600 * 24  # 24 hours

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Add a message to conversation history

        Args:
            conversation_id: Unique conversation identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (sources, scores, etc.)
        """
        key = f"conversation:{conversation_id}"

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # Append to list
        self.client.rpush(key, json.dumps(message))

        # Set expiration
        self.client.expire(key, self.ttl)

    def get_history(self, conversation_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve conversation history

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of recent messages

        Returns:
            List of messages (oldest first)
        """
        key = f"conversation:{conversation_id}"

        # Get last N messages
        messages = self.client.lrange(key, -limit, -1)

        return [json.loads(msg) for msg in messages]

    def format_for_llm(self, conversation_id: str, limit: int = 5, include_system: bool = True) -> list[dict[str, str]]:
        """
        Format history for LLM consumption (OpenAI format)

        Args:
            conversation_id: Conversation ID
            limit: Number of recent exchanges
            include_system: Include system message

        Returns:
            List of {'role': ..., 'content': ...} dicts
        """
        history = self.get_history(conversation_id, limit)

        messages = []

        if include_system:
            messages.append(
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant with access to documents via RAG.",
                }
            )

        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        return messages

    def clear_history(self, conversation_id: str):
        """Delete conversation history"""
        key = f"conversation:{conversation_id}"
        self.client.delete(key)

    def list_conversations(self) -> list[str]:
        """List all active conversation IDs"""
        keys = self.client.keys("conversation:*")
        return [k.replace("conversation:", "") for k in keys]
