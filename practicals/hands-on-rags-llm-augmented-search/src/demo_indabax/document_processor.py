"""
PDF Extraction and Chunking using Docling
Simple and clean implementation for RAG demo
"""

from pathlib import Path
from typing import Any

from docling.document_converter import DocumentConverter


class DocumentProcessor:
    """Extract text from PDFs and chunk them intelligently"""

    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128):
        self.converter = DocumentConverter()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text(self, pdf_path: str) -> dict[str, Any]:
        """
        Extract structured text from PDF using Docling

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with document structure (sections, text, metadata)
        """
        result = self.converter.convert(pdf_path)
        doc = result.document

        # Extract metadata
        metadata = {
            "filename": Path(pdf_path).name,
            "title": getattr(doc, "title", Path(pdf_path).stem),
            "pages": len(doc.pages) if hasattr(doc, "pages") else None,
        }

        # Extract full text with section hierarchy
        sections = []
        for element in doc.iterate_items():
            # Docling returns tuples: (item, level)
            if isinstance(element, tuple) and len(element) >= 2:
                item, level = element
                if hasattr(item, "text") and hasattr(item, "label") and item.text.strip():
                    sections.append(
                        {
                            "type": item.label.value if hasattr(item.label, "value") else str(item.label),
                            "text": item.text,
                            "level": getattr(item, "level", level),
                        }
                    )
            elif hasattr(element, "label") and hasattr(element, "text") and element.text.strip():
                sections.append(
                    {
                        "type": element.label.value if hasattr(element.label, "value") else str(element.label),
                        "text": element.text,
                        "level": getattr(element, "level", 0),
                    }
                )

        return {
            "metadata": metadata,
            "sections": sections,
            "full_text": doc.export_to_markdown(),
        }

    def chunk_document(self, doc_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Chunk document into larger pieces by combining sections

        Args:
            doc_data: Document data from extract_text()

        Returns:
            List of chunks with metadata
        """
        chunks = []
        current_chunk_text = ""
        current_chunk_metadata = {
            "filename": doc_data["metadata"]["filename"],
            "title": doc_data["metadata"]["title"],
            "section": None,
            "subsection": None,
            "types": [],
        }

        for section in doc_data["sections"]:
            # Track section hierarchy
            if section["type"] in ["section_header", "heading", "title", "h1"]:
                current_chunk_metadata["section"] = section["text"]
                current_chunk_metadata["subsection"] = None
            elif section["type"] in ["h2", "h3", "subtitle"]:
                current_chunk_metadata["subsection"] = section["text"]

            # Add this section to current chunk
            if current_chunk_text:
                current_chunk_text += "\n\n" + section["text"]
            else:
                current_chunk_text = section["text"]

            current_chunk_metadata["types"].append(section["type"])

            # If chunk is big enough, create a chunk
            if len(current_chunk_text) >= self.chunk_size:
                chunk = {
                    "content": current_chunk_text.strip(),
                    "metadata": {
                        **current_chunk_metadata,
                        "chunk_index": len(chunks),
                    },
                }
                chunks.append(chunk)

                # Start new chunk
                current_chunk_text = ""
                current_chunk_metadata = {
                    "filename": doc_data["metadata"]["filename"],
                    "title": doc_data["metadata"]["title"],
                    "section": current_chunk_metadata["section"],
                    "subsection": current_chunk_metadata["subsection"],
                    "types": [],
                }

        # Add remaining text as final chunk
        if current_chunk_text.strip():
            chunk = {
                "content": current_chunk_text.strip(),
                "metadata": {
                    **current_chunk_metadata,
                    "chunk_index": len(chunks),
                },
            }
            chunks.append(chunk)

        return chunks

    def _chunk_text(self, text: str) -> list[str]:
        """Simple sliding window chunking"""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end markers
                for marker in [". ", ".\n", "! ", "? "]:
                    last_marker = text[start:end].rfind(marker)
                    if last_marker != -1:
                        end = start + last_marker + len(marker)
                        break

            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap

        return chunks

    def process_pdf(self, pdf_path: str) -> list[dict[str, Any]]:
        """One-shot: extract and chunk PDF"""
        doc_data = self.extract_text(pdf_path)
        return self.chunk_document(doc_data)
