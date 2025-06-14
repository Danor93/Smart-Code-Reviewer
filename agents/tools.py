"""
Agent Tools for Code Review Tasks.

This module provides tools that AI agents can use to perform various
code review operations, including RAG searches, traditional reviews,
and guideline lookups.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from langchain.tools import Tool
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from reviewers.code_reviewer import EnhancedCodeReviewer
from reviewers.rag_code_reviewer import RAGCodeReviewer

logger = logging.getLogger(__name__)

# Global instances for tool functions
_rag_reviewer = None
_traditional_reviewer = None


def get_rag_reviewer():
    """Get or create RAG reviewer instance."""
    global _rag_reviewer
    if _rag_reviewer is None:
        _rag_reviewer = RAGCodeReviewer()
    return _rag_reviewer


def get_traditional_reviewer():
    """Get or create traditional reviewer instance."""
    global _traditional_reviewer
    if _traditional_reviewer is None:
        _traditional_reviewer = EnhancedCodeReviewer()
    return _traditional_reviewer


class CodeInput(BaseModel):
    """Input schema for code-related tools."""

    code: str = Field(description="The code to analyze")
    language: str = Field(default="python", description="Programming language")
    model_id: str = Field(default="gpt-4", description="LLM model to use")


class SearchInput(BaseModel):
    """Input schema for search tools."""

    query: str = Field(description="Search query")
    category: Optional[str] = Field(default=None, description="Category filter")
    k: int = Field(default=3, description="Number of results to return")


@tool("rag_code_review", args_schema=CodeInput)
def rag_code_review(code: str, language: str = "python", model_id: str = "gpt-4") -> str:
    """
    Perform RAG-enhanced code review using coding guidelines and best practices.

    This tool uses retrieval-augmented generation to provide context-aware
    code reviews based on industry standards and best practices.

    Args:
        code: The code to review
        language: Programming language (default: python)
        model_id: LLM model to use (default: gpt-4)

    Returns:
        JSON string with detailed code review results
    """
    try:
        reviewer = get_rag_reviewer()

        # Run the async RAG review
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(reviewer.review_code_with_rag(code, language, model_id))

            return json.dumps(
                {
                    "review_type": "rag_enhanced",
                    "rating": result.rating,
                    "issues": [issue.to_dict() for issue in result.issues],
                    "suggestions": [suggestion.to_dict() for suggestion in result.suggestions],
                    "reasoning": result.reasoning,
                    "rag_context": result.rag_context,
                    "model_used": result.model_used,
                    "timestamp": result.timestamp.isoformat(),
                },
                indent=2,
            )
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error in RAG code review: {str(e)}")
        return json.dumps({"error": f"RAG review failed: {str(e)}", "fallback_available": True})


@tool("traditional_code_review", args_schema=CodeInput)
def traditional_code_review(code: str, language: str = "python", model_id: str = "gpt-4") -> str:
    """
    Perform traditional code review without RAG enhancement.

    This tool provides standard code review using LLM capabilities
    without additional context from coding guidelines.

    Args:
        code: The code to review
        language: Programming language (default: python)
        model_id: LLM model to use (default: gpt-4)

    Returns:
        JSON string with code review results
    """
    try:
        reviewer = get_traditional_reviewer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(reviewer.review_code_async(code, language, "zero_shot", model_id))

            return json.dumps(
                {
                    "review_type": "traditional",
                    "rating": result.rating,
                    "issues": [issue.to_dict() for issue in result.issues],
                    "suggestions": [suggestion.to_dict() for suggestion in result.suggestions],
                    "reasoning": result.reasoning,
                    "model_used": result.model_used,
                    "timestamp": result.timestamp.isoformat(),
                },
                indent=2,
            )
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error in traditional code review: {str(e)}")
        return json.dumps({"error": f"Traditional review failed: {str(e)}"})


@tool("search_guidelines", args_schema=SearchInput)
def search_guidelines(query: str, category: Optional[str] = None, k: int = 3) -> str:
    """
    Search the coding guidelines knowledge base for relevant information.

    This tool searches through coding standards, security guidelines,
    performance tips, and best practices documentation.

    Args:
        query: Search query describing what guidelines to find
        category: Optional category filter (security, performance, style, etc.)
        k: Number of guideline documents to return (default: 3)

    Returns:
        JSON string with relevant guidelines and their content
    """
    try:
        reviewer = get_rag_reviewer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(reviewer.search_guidelines(query, category, k))

            return json.dumps(
                {
                    "query": query,
                    "category": category,
                    "results_count": len(results),
                    "guidelines": results,
                },
                indent=2,
            )
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error searching guidelines: {str(e)}")
        return json.dumps({"error": f"Guidelines search failed: {str(e)}", "query": query})


@tool("compare_review_approaches")
def compare_review_approaches(code: str, language: str = "python", model_id: str = "gpt-4") -> str:
    """
    Compare RAG-enhanced vs traditional code review approaches.

    This tool performs both types of reviews and provides a detailed
    comparison of their findings, highlighting the benefits of RAG.

    Args:
        code: The code to review
        language: Programming language (default: python)
        model_id: LLM model to use (default: gpt-4)

    Returns:
        JSON string with comparative analysis
    """
    try:
        reviewer = get_rag_reviewer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            comparison = loop.run_until_complete(reviewer.compare_rag_vs_traditional(code, language, model_id))

            return json.dumps(comparison, indent=2)
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error in comparison: {str(e)}")
        return json.dumps({"error": f"Comparison failed: {str(e)}"})


@tool("get_knowledge_base_stats")
def get_knowledge_base_stats() -> str:
    """
    Get statistics about the RAG knowledge base.

    This tool provides information about the loaded documents,
    vector store status, and available guidelines categories.

    Returns:
        JSON string with knowledge base statistics
    """
    try:
        reviewer = get_rag_reviewer()
        stats = reviewer.get_knowledge_base_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {str(e)}")
        return json.dumps({"error": f"Failed to get knowledge base stats: {str(e)}"})


class AgentTools:
    """Collection of tools for AI agents to perform code review tasks."""

    def __init__(self):
        """Initialize the agent tools."""
        logger.info("AgentTools initialized")

    def get_all_tools(self) -> List[Tool]:
        """
        Get all available tools for the agent.

        Returns:
            List of Tool objects that can be used by LangGraph agents
        """
        return [
            rag_code_review,
            traditional_code_review,
            search_guidelines,
            compare_review_approaches,
            get_knowledge_base_stats,
        ]

    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available tools.

        Returns:
            Dictionary mapping tool names to their descriptions
        """
        return {
            "rag_code_review": "RAG-enhanced code review with industry guidelines",
            "traditional_code_review": "Standard LLM-based code review",
            "search_guidelines": "Search coding guidelines and best practices",
            "compare_review_approaches": "Compare RAG vs traditional review methods",
            "get_knowledge_base_stats": "Get RAG knowledge base statistics",
        }
