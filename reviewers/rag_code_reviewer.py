"""
RAG-Enhanced Code Reviewer.

This module extends the EnhancedCodeReviewer with Retrieval-Augmented Generation
capabilities, using relevant coding guidelines and best practices to enhance reviews.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

from models.data_models import ReviewResult
from rag import DocumentLoader, VectorStore

from .code_reviewer import EnhancedCodeReviewer

logger = logging.getLogger(__name__)


class RAGCodeReviewer(EnhancedCodeReviewer):
    """Enhanced code reviewer with RAG capabilities for knowledge-aware reviews."""

    def __init__(self):
        """Initialize the RAG-enhanced code reviewer."""
        super().__init__()

        # Initialize RAG components
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()

        # Track initialization status
        self.rag_initialized = False
        self.setup_rag_chain()

        logger.info("RAGCodeReviewer initialized")

    def setup_rag_chain(self):
        """Setup the RAG chain with enhanced prompts."""

        # RAG-enhanced prompt template
        self.rag_template = """
You are an expert code reviewer with access to comprehensive coding guidelines and best practices.

RELEVANT CODING GUIDELINES:
{context}

CODE TO REVIEW:
```{language}
{code}
```

Based on the coding guidelines above, provide a comprehensive code review following this exact JSON format:

{{
    "issues": [
        {{
            "type": "security|performance|style|maintainability|bug",
            "severity": "critical|high|medium|low",
            "description": "Detailed description of the issue",
            "line_reference": "Specific line or function if applicable",
            "guideline_reference": "Which guideline from the context this violates"
        }}
    ],
    "suggestions": [
        {{
            "type": "improvement|best_practice|optimization",
            "description": "Actionable improvement suggestion",
            "code_example": "Improved code example if applicable",
            "guideline_reference": "Which guideline supports this suggestion"
        }}
    ],
    "rating": "Excellent|Good|Fair|Poor",
    "reasoning": "Detailed explanation of the rating based on the guidelines",
    "guidelines_used": [
        "List of specific guidelines referenced from the context"
    ],
    "rag_context_quality": "high|medium|low"
}}

Focus on issues and improvements that are specifically supported by the provided guidelines.
If the code follows best practices mentioned in the guidelines, acknowledge this in your review.
"""

        self.rag_prompt = PromptTemplate(template=self.rag_template, input_variables=["context", "code", "language"])

        logger.info("RAG chain setup completed")

    async def initialize_rag(self) -> bool:
        """
        Initialize RAG components by loading documents and creating vector store.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing RAG components...")

            # Try to load existing vector store first
            if self.vector_store.load_vectorstore():
                self.rag_initialized = True
                logger.info("Loaded existing vector store")
                return True

            # If no existing vector store, create one from documents
            documents = await self.document_loader.load_and_chunk()
            if not documents:
                logger.warning("No documents found in knowledge base")
                return False

            # Create vector store
            success = await self.vector_store.create_vectorstore(documents)
            if success:
                self.rag_initialized = True
                logger.info(f"RAG initialized with {len(documents)} document chunks")
                return True
            else:
                logger.error("Failed to create vector store")
                return False

        except Exception as e:
            logger.error(f"Error initializing RAG: {str(e)}")
            return False

    async def review_code_with_rag(
        self,
        code: str,
        language: str = "python",
        model_id: str = None,
        num_guidelines: int = 3,
    ) -> ReviewResult:
        """
        Review code using RAG-enhanced prompts with relevant guidelines.

        Args:
            code: Code to review
            language: Programming language
            model_id: LLM model to use
            num_guidelines: Number of relevant guidelines to retrieve

        Returns:
            Enhanced ReviewResult with RAG context
        """
        try:
            # Ensure RAG is initialized
            if not self.rag_initialized:
                if not await self.initialize_rag():
                    logger.warning("RAG not available, falling back to traditional review")
                    return await self.review_code_async(code, language, "zero_shot", model_id)

            # Create search query based on code content and language
            search_query = self._create_search_query(code, language)

            # Retrieve relevant guidelines
            relevant_docs = await self.vector_store.similarity_search(search_query, k=num_guidelines)

            if not relevant_docs:
                logger.warning("No relevant guidelines found, falling back to traditional review")
                return await self.review_code_async(code, language, "zero_shot", model_id)

            # Build context from retrieved documents
            context = self._build_context(relevant_docs)

            # Create RAG-enhanced prompt
            enhanced_prompt = self.rag_prompt.format(context=context, code=code, language=language)

            # Get model and perform review
            model = self.model_registry.create_model(model_id or "gpt-4")

            messages = [
                SystemMessage(content="You are an expert code reviewer with access to comprehensive coding guidelines."),
                HumanMessage(content=enhanced_prompt),
            ]

            response = await model.ainvoke(messages)

            # Parse and enhance the result
            result = self._parse_rag_review_result(response.content, model_id, relevant_docs)

            logger.info(f"RAG review completed using {len(relevant_docs)} guidelines")
            return result

        except Exception as e:
            logger.error(f"Error in RAG review: {str(e)}")
            # Fallback to traditional review
            return await self.review_code_async(code, language, "zero_shot", model_id)

    def _create_search_query(self, code: str, language: str) -> str:
        """
        Create an effective search query based on code content.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Search query string
        """
        # Extract key terms and patterns from code
        query_terms = [language]

        # Add common patterns found in code
        if "password" in code.lower() or "secret" in code.lower():
            query_terms.append("security authentication")

        if "for" in code and "range" in code:
            query_terms.append("performance optimization loops")

        if "def " in code or "class " in code:
            query_terms.append("function naming conventions")

        if "try:" in code or "except" in code:
            query_terms.append("error handling")

        if "import " in code:
            query_terms.append("imports best practices")

        if "SELECT" in code.upper() or "INSERT" in code.upper():
            query_terms.append("SQL injection security")

        # Create comprehensive search query
        search_query = f"{language} code review best practices " + " ".join(query_terms)

        return search_query

    def _build_context(self, documents: List) -> str:
        """
        Build context string from retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, doc in enumerate(documents, 1):
            # Get document metadata
            metadata = doc.metadata
            category = metadata.get("category", "general")
            title = metadata.get("title", "Guidelines")

            # Format document content
            context_part = f"## Guideline {i}: {title} ({category})\n{doc.page_content}\n"
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def _parse_rag_review_result(self, response_content: str, model_id: str, relevant_docs: List) -> ReviewResult:
        """
        Parse RAG-enhanced review result with additional metadata.

        Args:
            response_content: LLM response content
            model_id: Model used for review
            relevant_docs: Documents used for context

        Returns:
            Enhanced ReviewResult
        """
        try:
            # Parse JSON response
            review_data = json.loads(response_content)

            # Create base result
            result = ReviewResult(
                rating=review_data.get("rating", "Fair"),
                issues=review_data.get("issues", []),
                suggestions=review_data.get("suggestions", []),
                reasoning=review_data.get("reasoning", ""),
                model_used=model_id,
                technique_used="rag",
                timestamp=datetime.now().isoformat(),
            )

            # Add RAG-specific metadata
            result.guidelines_used = review_data.get("guidelines_used", [])
            result.rag_context_quality = review_data.get("rag_context_quality", "medium")
            result.num_guidelines = len(relevant_docs)
            result.guideline_categories = list(set(doc.metadata.get("category", "general") for doc in relevant_docs))

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse RAG review JSON: {str(e)}")

            # Fallback parsing
            return ReviewResult(
                rating="Fair",
                issues=[
                    {
                        "description": "Failed to parse detailed review",
                        "severity": "low",
                    }
                ],
                suggestions=[{"description": "Review response format"}],
                reasoning="Error parsing enhanced review response",
                model_used=model_id,
                technique_used="rag",
                timestamp=datetime.now().isoformat(),
            )

    async def compare_rag_vs_traditional(self, code: str, language: str = "python", model_id: str = None) -> Dict[str, Any]:
        """
        Compare RAG-enhanced vs traditional review for the same code.

        Args:
            code: Code to review
            language: Programming language
            model_id: Model to use for comparison

        Returns:
            Comparison results
        """
        try:
            # Perform both types of reviews
            traditional_result = await self.review_code_async(code, language, "zero_shot", model_id)
            rag_result = await self.review_code_with_rag(code, language, model_id)

            # Calculate comparison metrics
            comparison = {
                "traditional_review": traditional_result.__dict__,
                "rag_enhanced_review": rag_result.__dict__,
                "comparison": {
                    "guidelines_referenced": getattr(rag_result, "num_guidelines", 0),
                    "context_quality": getattr(rag_result, "rag_context_quality", "none"),
                    "additional_issues_found": len(rag_result.issues) - len(traditional_result.issues),
                    "additional_suggestions": len(rag_result.suggestions) - len(traditional_result.suggestions),
                    "guideline_categories": getattr(rag_result, "guideline_categories", []),
                },
            }

            logger.info("RAG vs Traditional comparison completed")
            return comparison

        except Exception as e:
            logger.error(f"Error in comparison: {str(e)}")
            return {"error": str(e)}

    async def search_guidelines(self, query: str, category: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the guidelines database.

        Args:
            query: Search query
            category: Optional category filter
            k: Number of results to return

        Returns:
            List of matching guidelines with metadata
        """
        try:
            if not self.rag_initialized:
                await self.initialize_rag()

            if category:
                docs = await self.vector_store.search_by_category(query, category, k)
            else:
                docs = await self.vector_store.similarity_search(query, k)

            results = []
            for doc in docs:
                results.append(
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "category": doc.metadata.get("category", "general"),
                        "title": doc.metadata.get("title", "Guidelines"),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error searching guidelines: {str(e)}")
            return []

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Knowledge base statistics
        """
        try:
            stats = self.vector_store.get_collection_stats()
            categories = self.document_loader.get_categories()

            return {
                "vector_store_stats": stats,
                "available_categories": categories,
                "rag_initialized": self.rag_initialized,
            }

        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {str(e)}")
            return {"error": str(e)}

    async def refresh_knowledge_base(self) -> bool:
        """
        Refresh the knowledge base by reloading documents.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Refreshing knowledge base...")

            # Load updated documents
            documents = await self.document_loader.load_and_chunk()
            if not documents:
                logger.warning("No documents found for refresh")
                return False

            # Update vector store
            success = await self.vector_store.update_vectorstore(documents)
            if success:
                self.rag_initialized = True
                logger.info(f"Knowledge base refreshed with {len(documents)} document chunks")
                return True
            else:
                logger.error("Failed to refresh knowledge base")
                return False

        except Exception as e:
            logger.error(f"Error refreshing knowledge base: {str(e)}")
            return False
