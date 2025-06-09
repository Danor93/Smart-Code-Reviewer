"""
Document loader for RAG knowledge base.

This module handles loading and chunking of coding guidelines and best practices
documents for vector storage and retrieval.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads and chunks documents from the knowledge base directory."""

    def __init__(
        self,
        docs_path: str = "rag-knowledge-base",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the document loader.

        Args:
            docs_path: Path to the knowledge base directory
            chunk_size: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.docs_path = Path(docs_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize text splitter with optimal settings for code guidelines
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

        logger.info(f"DocumentLoader initialized with docs_path: {self.docs_path}")

    async def load_documents(self) -> List[Document]:
        """
        Load all documents from the knowledge base directory.

        Returns:
            List of Document objects with content and metadata
        """
        try:
            if not self.docs_path.exists():
                logger.error(f"Knowledge base directory not found: {self.docs_path}")
                return []

            # Load markdown files from all subdirectories
            loader = DirectoryLoader(
                str(self.docs_path),
                glob="**/*.md",
                loader_cls=TextLoader,
                show_progress=True,
            )

            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {self.docs_path}")

            # Add category metadata based on directory structure
            for doc in documents:
                self._add_metadata(doc)

            return documents

        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []

    def _add_metadata(self, doc: Document) -> None:
        """
        Add metadata to document based on file path and content.

        Args:
            doc: Document to add metadata to
        """
        file_path = Path(doc.metadata.get("source", ""))

        # Extract category from directory structure
        relative_path = (
            file_path.relative_to(self.docs_path)
            if self.docs_path in file_path.parents
            else file_path
        )
        category = relative_path.parts[0] if relative_path.parts else "general"

        # Add enhanced metadata
        doc.metadata.update(
            {
                "category": category,
                "filename": file_path.name,
                "file_type": file_path.suffix,
                "content_length": len(doc.page_content),
            }
        )

        # Extract document title from first heading
        lines = doc.page_content.split("\n")
        title = None
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        if title:
            doc.metadata["title"] = title

    async def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.

        Args:
            documents: List of documents to chunk

        Returns:
            List of chunked documents
        """
        try:
            chunks = self.text_splitter.split_documents(documents)

            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_id"] = i
                chunk.metadata["chunk_size"] = len(chunk.page_content)

            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            return documents

    async def load_and_chunk(self) -> List[Document]:
        """
        Load documents and split them into chunks in one operation.

        Returns:
            List of chunked documents ready for vector storage
        """
        documents = await self.load_documents()
        if not documents:
            return []

        return await self.chunk_documents(documents)

    def get_categories(self) -> List[str]:
        """
        Get list of available categories in the knowledge base.

        Returns:
            List of category names
        """
        categories = []
        if self.docs_path.exists():
            for item in self.docs_path.iterdir():
                if item.is_dir():
                    categories.append(item.name)
        return sorted(categories)

    async def load_category(self, category: str) -> List[Document]:
        """
        Load documents from a specific category.

        Args:
            category: Category name (subdirectory name)

        Returns:
            List of documents from the specified category
        """
        category_path = self.docs_path / category
        if not category_path.exists():
            logger.warning(f"Category directory not found: {category_path}")
            return []

        try:
            loader = DirectoryLoader(
                str(category_path), glob="*.md", loader_cls=TextLoader
            )

            documents = loader.load()
            for doc in documents:
                self._add_metadata(doc)
                doc.metadata["category"] = category

            logger.info(f"Loaded {len(documents)} documents from category: {category}")
            return documents

        except Exception as e:
            logger.error(f"Error loading category {category}: {str(e)}")
            return []
