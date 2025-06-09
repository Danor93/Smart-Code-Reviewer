"""
RAG (Retrieval-Augmented Generation) module for Smart Code Reviewer.

This module provides document loading, vector storage, and retrieval capabilities
to enhance code reviews with relevant coding guidelines and best practices.
"""

from .document_loader import DocumentLoader
from .vector_store import VectorStore

__all__ = ["DocumentLoader", "VectorStore"]
