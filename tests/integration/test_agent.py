#!/usr/bin/env python3
"""
Test script for AI Agent functionality.

This script tests the CodeReviewAgent and its integration with the RAG system.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import pytest

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from agents import CodeReviewAgent, CodeReviewRequest
from agents.tools import AgentTools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test code samples
SIMPLE_PYTHON_CODE = """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""

VULNERABLE_PYTHON_CODE = """
import os
import sqlite3

def get_user_data(username):
    password = "hardcoded_password123"
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    return results

def authenticate(username, password):
    # Insecure comparison
    if password == "admin":
        return True
    return False
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_tools():
    """Test the agent tools functionality."""
    print("🔧 Testing Agent Tools...")

    tools = AgentTools()

    # Test RAG code review tool
    print("Testing RAG code review tool...")
    from agents.tools import rag_code_review

    result = rag_code_review.invoke({"code": SIMPLE_PYTHON_CODE, "language": "python", "model_id": "gpt-4"})
    print(f"✅ RAG review result: {len(result)} characters")
    assert len(result) > 0, "RAG code review should return non-empty result"

    # Test traditional code review tool
    print("Testing traditional code review tool...")
    from agents.tools import traditional_code_review

    result = traditional_code_review.invoke({"code": SIMPLE_PYTHON_CODE, "language": "python", "model_id": "gpt-4"})
    print(f"✅ Traditional review result: {len(result)} characters")
    assert len(result) > 0, "Traditional code review should return non-empty result"

    # Test guidelines search
    print("Testing guidelines search...")
    from agents.tools import search_guidelines

    result = search_guidelines.invoke({"query": "python security best practices", "k": 3})
    print(f"✅ Guidelines search result: {len(result)} characters")
    assert len(result) > 0, "Guidelines search should return non-empty result"

    # Test knowledge base stats
    print("Testing knowledge base stats...")
    from agents.tools import get_knowledge_base_stats

    result = get_knowledge_base_stats.invoke({})
    print(f"✅ Knowledge base stats: {len(result)} characters")
    assert len(result) > 0, "Knowledge base stats should return non-empty result"

    print("✅ All agent tools tested successfully!")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_code_review_agent():
    """Test the CodeReviewAgent functionality."""
    print("\n🤖 Testing Code Review Agent...")

    agent = CodeReviewAgent(model_id="gpt-4")

    # Test simple code review
    print("Testing simple code review...")
    request = CodeReviewRequest(
        code=SIMPLE_PYTHON_CODE,
        language="python",
        user_request="Review this simple Python function",
    )

    result = await agent.review_code(request)

    assert "error" not in result, f"Agent returned error: {result.get('error', 'Unknown error')}"

    print(f"✅ Agent review completed:")
    print(f"  - Iterations: {result['agent_analysis']['iterations']}")
    print(f"  - Tools used: {result['agent_analysis']['tools_used']}")
    print(f"  - Workflow complete: {result['metadata']['workflow_complete']}")

    assert result["agent_analysis"]["iterations"] > 0, "Agent should have at least one iteration"
    assert len(result["agent_analysis"]["tools_used"]) > 0, "Agent should use at least one tool"
    assert result["metadata"]["workflow_complete"] is True, "Workflow should be complete"

    # Test vulnerable code review
    print("\nTesting vulnerable code review...")
    request = CodeReviewRequest(
        code=VULNERABLE_PYTHON_CODE,
        language="python",
        user_request="Focus on security vulnerabilities in this code",
    )

    result = await agent.review_code(request)

    assert "error" not in result, f"Agent returned error: {result.get('error', 'Unknown error')}"

    print(f"✅ Vulnerable code review completed:")
    print(f"  - Iterations: {result['agent_analysis']['iterations']}")
    print(f"  - Tools used: {result['agent_analysis']['tools_used']}")

    assert result["agent_analysis"]["iterations"] > 0, "Agent should have at least one iteration"
    assert len(result["agent_analysis"]["tools_used"]) > 0, "Agent should use at least one tool"

    # Test agent info
    print("\nTesting agent info...")
    info = agent.get_agent_info()
    print(f"✅ Agent info retrieved:")
    print(f"  - Agent type: {info['agent_type']}")
    print(f"  - Model: {info['model_id']}")
    print(f"  - Available tools: {len(info['available_tools'])}")
    print(f"  - Capabilities: {len(info['capabilities'])}")

    assert info["agent_type"] == "CodeReviewAgent", "Agent type should be CodeReviewAgent"
    assert info["model_id"] == "gpt-4", "Model ID should be gpt-4"
    assert len(info["available_tools"]) > 0, "Agent should have available tools"
    assert len(info["capabilities"]) > 0, "Agent should have capabilities"

    print("✅ All agent tests passed!")


def test_imports():
    """Test that all imports work correctly."""
    print("📦 Testing imports...")

    from agents import CodeReviewAgent, CodeReviewRequest
    from agents.tools import AgentTools

    print("✅ All imports successful!")
    assert True  # If we get here, imports succeeded


# Keep the main function for standalone execution
async def main():
    """Run all tests."""
    print("🧪 Starting AI Agent Tests")
    print("=" * 50)

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")

    # Test imports
    test_imports()
    print("✅ Import tests passed.")

    # Test agent tools
    await test_agent_tools()
    print("✅ Agent tools tests passed.")

    # Test code review agent
    await test_code_review_agent()
    print("✅ Code review agent tests passed.")

    print("\n" + "=" * 50)
    print("🎉 All tests passed! Agent integration is working correctly.")
    print("\n📋 Next Steps:")
    print("1. Run the Flask app: python app.py")
    print("2. Test agent endpoints:")
    print("   - GET  /agent/info")
    print("   - POST /agent/review")
    print("   - GET  /agent/review/vulnerable_code.py")
    print("\n💡 Example curl commands:")
    print("curl http://localhost:8080/agent/info")
    print("curl -X POST http://localhost:8080/agent/review \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"code": "def hello(): print(\\"Hello\\")"}\'')


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
