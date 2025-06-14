#!/usr/bin/env python3
"""
Test script for RAG functionality in Smart Code Reviewer
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from reviewers.rag_code_reviewer import RAGCodeReviewer

# Load environment variables
load_dotenv()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.rag
async def test_rag_reviewer():
    """Test the RAG-enhanced code reviewer"""

    print("🧠 Testing RAG-Enhanced Code Reviewer")
    print("=" * 50)

    # Initialize the RAG reviewer
    rag_reviewer = RAGCodeReviewer()

    # Test 1: Check knowledge base stats
    print("\n📊 Knowledge Base Statistics:")
    stats = rag_reviewer.get_knowledge_base_stats()
    print(f"Available categories: {stats.get('available_categories', [])}")
    print(f"RAG initialized: {stats.get('rag_initialized', False)}")

    assert isinstance(stats, dict), "Knowledge base stats should be a dictionary"

    # Test 2: Initialize RAG if not already done
    print("\n🔧 Initializing RAG...")
    success = await rag_reviewer.initialize_rag()
    print(f"RAG initialization: {'✅ Success' if success else '❌ Failed'}")

    if not success:
        pytest.skip("RAG initialization failed. Check if knowledge base exists and OpenAI API key is set.")

    # Updated stats after initialization
    stats = rag_reviewer.get_knowledge_base_stats()
    print(f"\n📈 Updated Knowledge Base Stats:")
    print(f"Vector store stats: {stats.get('vector_store_stats', {})}")

    assert stats.get("rag_initialized", False), "RAG should be initialized after successful initialization"

    # Test 3: Search guidelines
    print("\n🔍 Testing guideline search...")
    search_results = await rag_reviewer.search_guidelines("Python security best practices", k=3)
    print(f"Found {len(search_results)} relevant guidelines")
    for i, result in enumerate(search_results, 1):
        print(f"  {i}. {result.get('title', 'Unknown')} ({result.get('category', 'general')})")

    assert isinstance(search_results, list), "Search results should be a list"
    assert len(search_results) <= 3, "Should return at most 3 results as requested"

    # Test 4: RAG-enhanced code review
    print("\n🧪 Testing RAG-enhanced code review...")

    # Sample vulnerable code
    test_code = """
def login(username, password):
    # Hardcoded admin password - security issue
    if username == "admin" and password == "admin123":
        return True
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = execute_query(query)
    return result is not None
"""

    # Perform RAG review
    result = await rag_reviewer.review_code_with_rag(test_code, "python")

    print(f"✅ RAG Review completed!")
    print(f"Rating: {result.rating}")
    print(f"Model used: {result.model_used}")
    print(f"Guidelines used: {getattr(result, 'num_guidelines', 0)}")
    print(f"Issues found: {len(result.issues)}")
    print(f"Suggestions: {len(result.suggestions)}")

    if hasattr(result, "guideline_categories"):
        print(f"Categories referenced: {getattr(result, 'guideline_categories', [])}")

    # Show first issue and suggestion as examples
    if result.issues:
        print(f"\n📋 Example Issue: {result.issues[0]}")
    if result.suggestions:
        print(f"\n💡 Example Suggestion: {result.suggestions[0]}")

    # Assertions for RAG review
    assert hasattr(result, "rating"), "Result should have a rating"
    assert hasattr(result, "model_used"), "Result should specify model used"
    assert hasattr(result, "issues"), "Result should have issues list"
    assert hasattr(result, "suggestions"), "Result should have suggestions list"
    assert isinstance(result.issues, list), "Issues should be a list"
    assert isinstance(result.suggestions, list), "Suggestions should be a list"

    # Test 5: Compare RAG vs Traditional
    print("\n⚖️  Testing RAG vs Traditional comparison...")
    comparison = await rag_reviewer.compare_rag_vs_traditional(test_code, "python")

    assert "error" not in comparison, f"Comparison should not have errors: {comparison.get('error', '')}"

    print("✅ Comparison completed!")
    metrics = comparison.get("comparison", {})
    print(f"Guidelines referenced: {metrics.get('guidelines_referenced', 0)}")
    print(f"Additional issues found: {metrics.get('additional_issues_found', 0)}")
    print(f"Additional suggestions: {metrics.get('additional_suggestions', 0)}")

    assert isinstance(comparison, dict), "Comparison result should be a dictionary"
    assert "comparison" in comparison, "Comparison should contain comparison metrics"


# Keep the main function for standalone execution
async def main():
    """Run the test standalone"""
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set your OPENAI_API_KEY environment variable")
        print("You can add it to your .env file or export it in your shell")
        return False

    # Run the test
    await test_rag_reviewer()
    print("\n🎉 All RAG tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
