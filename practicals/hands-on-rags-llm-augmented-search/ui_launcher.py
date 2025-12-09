#!/usr/bin/env python3
"""
Launcher script for Streamlit UI with proper PYTHONPATH
"""

import os
import sys
from pathlib import Path


# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = str(src_path)


def main():
    """Main function to run the Streamlit UI"""
    # Import and run streamlit
    import subprocess

    # Run streamlit with the UI file
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/demo_indabax/ui.py",
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ]
    )


if __name__ == "__main__":
    main()
