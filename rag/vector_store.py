"""
Vector store implementation using ChromaDB for RAG functionality.

This module provides vector storage and similarity search capabilities
for the Smart Code Reviewer's knowledge base.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store implementation using ChromaDB for document retrieval."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "code_review_kb",
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the ChromaDB
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.vectorstore = None

        # Initialize OpenAI embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-3-small",  # More cost-effective embedding model
            )
            logger.info("OpenAI embeddings initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
            raise

        # Ensure persist directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"VectorStore initialized with persist_directory: {self.persist_directory}"
        )

    async def create_vectorstore(self, documents: List[Document]) -> bool:
        """
        Create vector store from documents.

        Args:
            documents: List of documents to store

        Returns:
            True if successful, False otherwise
        """
        try:
            if not documents:
                logger.warning("No documents provided to create vector store")
                return False

            logger.info(f"Creating vector store with {len(documents)} documents")

            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory),
                collection_name=self.collection_name,
            )

            # In newer ChromaDB versions, persistence happens automatically

            logger.info(
                f"Vector store created and persisted with {len(documents)} documents"
            )
            return True

        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            return False

    def load_vectorstore(self) -> bool:
        """
        Load existing vector store from persistence.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not self.persist_directory.exists():
                logger.warning(
                    f"Persist directory does not exist: {self.persist_directory}"
                )
                return False

            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name=self.collection_name,
            )

            # Check if collection has any documents
            collection_count = self.vectorstore._collection.count()
            if collection_count == 0:
                logger.warning("Vector store is empty")
                return False

            logger.info(f"Vector store loaded with {collection_count} documents")
            return True

        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False

    async def similarity_search(
        self, query: str, k: int = 3, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Search query
            k: Number of documents to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents
        """
        try:
            if not self.vectorstore:
                if not self.load_vectorstore():
                    logger.error("Vector store not available for search")
                    return []

            # Perform similarity search
            if filter_dict:
                docs = self.vectorstore.similarity_search(
                    query=query, k=k, filter=filter_dict
                )
            else:
                docs = self.vectorstore.similarity_search(query=query, k=k)

            logger.info(
                f"Found {len(docs)} relevant documents for query: '{query[:50]}...'"
            )
            return docs

        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            return []

    async def similarity_search_with_score(
        self, query: str, k: int = 3, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        Perform similarity search with relevance scores.

        Args:
            query: Search query
            k: Number of documents to return
            filter_dict: Optional metadata filters

        Returns:
            List of (document, score) tuples
        """
        try:
            if not self.vectorstore:
                if not self.load_vectorstore():
                    logger.error("Vector store not available for search")
                    return []

            # Perform similarity search with scores
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query=query, k=k, filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search_with_score(
                    query=query, k=k
                )

            logger.info(
                f"Found {len(results)} scored results for query: '{query[:50]}...'"
            )
            return results

        except Exception as e:
            logger.error(f"Error during similarity search with score: {str(e)}")
            return []

    async def search_by_category(
        self, query: str, category: str, k: int = 3
    ) -> List[Document]:
        """
        Search for documents within a specific category.

        Args:
            query: Search query
            category: Category to search within
            k: Number of documents to return

        Returns:
            List of relevant documents from the specified category
        """
        filter_dict = {"category": category}
        return await self.similarity_search(query, k, filter_dict)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.

        Returns:
            Dictionary with collection statistics
        """
        try:
            if not self.vectorstore:
                if not self.load_vectorstore():
                    return {"error": "Vector store not available"}

            collection = self.vectorstore._collection
            count = collection.count()

            # Get metadata for all documents to analyze categories
            if count > 0:
                results = collection.get(include=["metadatas"])
                metadatas = results.get("metadatas", [])

                categories = {}
                for metadata in metadatas:
                    category = metadata.get("category", "unknown")
                    categories[category] = categories.get(category, 0) + 1

                return {
                    "total_documents": count,
                    "categories": categories,
                    "collection_name": self.collection_name,
                }
            else:
                return {
                    "total_documents": 0,
                    "categories": {},
                    "collection_name": self.collection_name,
                }

        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}

    async def add_documents(self, documents: List[Document]) -> bool:
        """
        Add new documents to existing vector store.

        Args:
            documents: List of documents to add

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.vectorstore:
                if not self.load_vectorstore():
                    # Create new vector store if none exists
                    return await self.create_vectorstore(documents)

            # Add documents to existing vector store
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()

            logger.info(f"Added {len(documents)} documents to vector store")
            return True

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False

    def delete_collection(self) -> bool:
        """
        Delete the entire collection and start fresh.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.persist_directory.exists():
                import shutil

                shutil.rmtree(self.persist_directory)
                self.vectorstore = None
                logger.info("Vector store collection deleted")
                return True
            return True

        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False

    async def update_vectorstore(self, documents: List[Document]) -> bool:
        """
        Update vector store by recreating it with new documents.

        Args:
            documents: New set of documents

        Returns:
            True if successful, False otherwise
        """
        # Delete existing collection
        self.delete_collection()

        # Create new collection with updated documents
        return await self.create_vectorstore(documents)
