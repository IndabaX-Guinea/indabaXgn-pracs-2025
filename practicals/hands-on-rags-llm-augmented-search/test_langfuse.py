#!/usr/bin/env python3
"""Quick test to verify Langfuse tracing is working"""

import os

from dotenv import load_dotenv


load_dotenv()

try:
    from langfuse import Langfuse

    # Initialize Langfuse
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        print("❌ Langfuse keys not found in .env")
        exit(1)

    print("✓ Initializing Langfuse client...")
    print(f"  Host: {host}")
    print(f"  Public Key: {public_key[:20]}...")

    langfuse_client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )

    # Create a trace using the correct Langfuse API
    print("\n✓ Creating test trace...")
    trace = langfuse_client.start_as_current_span(
        name="test_trace", input={"test": "Hello Langfuse!"}, metadata={"source": "test_script"}
    )

    # Add a nested span
    print("✓ Adding test span...")
    span = langfuse_client.start_span(name="test_span", input={"operation": "test"}, output={"result": "success"})
    span.end()

    # Update current trace
    langfuse_client.update_current_trace(output={"status": "completed"})

    # Flush to send to Langfuse
    print("✓ Flushing to Langfuse cloud...")
    langfuse_client.flush()

    print("\n✅ SUCCESS! Langfuse tracing is working!")
    print("   Check your dashboard at: https://cloud.langfuse.com")
    print("   Trace name: 'test_trace'")

except ImportError:
    print("❌ Langfuse not installed. Run: uv add langfuse")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
