"""
Pytest configuration and fixtures for Smart Code Reviewer tests
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test environment variables
TEST_ENV_VARS = {
    "OPENAI_API_KEY": "test-openai-key",
    "ANTHROPIC_API_KEY": "test-anthropic-key",
    "GOOGLE_API_KEY": "test-google-key",
    "HUGGINGFACE_API_TOKEN": "test-hf-token",
    "OLLAMA_API_URL": "http://localhost:11434",
    "FLASK_ENV": "testing",
    "FLASK_DEBUG": "false",
}


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    original_env = {}

    # Store original values and set test values
    for key, value in TEST_ENV_VARS.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing"""
    return """
def divide(a, b):
    return a / b

def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

password = "admin123"
"""


@pytest.fixture
def sample_vulnerable_code():
    """Sample vulnerable code for testing"""
    return """
import os
import subprocess

def login(username, password):
    # Hardcoded credentials
    if username == "admin" and password == "admin123":
        return True
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = execute_query(query)
    return result is not None

def execute_command(user_input):
    # Command injection vulnerability
    return subprocess.run(user_input, shell=True)

# Hardcoded API key
API_KEY = "sk-1234567890abcdef"
"""


@pytest.fixture
def mock_model_registry():
    """Mock model registry for testing"""
    mock_registry = Mock()
    mock_registry.get_available_models.return_value = {
        "gpt-4": "OpenAI GPT-4",
        "gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo",
        "claude-3-sonnet": "Anthropic Claude 3 Sonnet",
    }
    mock_registry.create_model.return_value = Mock()
    return mock_registry


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    mock_store = Mock()
    mock_store.similarity_search.return_value = [
        {
            "content": "Use proper error handling in your code",
            "title": "Error Handling Best Practices",
            "category": "best_practices",
        }
    ]
    mock_store.get_collection_stats.return_value = {
        "total_documents": 100,
        "categories": ["security", "performance", "style"],
    }
    return mock_store


@pytest.fixture
def mock_document_loader():
    """Mock document loader for testing"""
    mock_loader = Mock()
    mock_loader.load_documents.return_value = [
        {
            "content": "Security best practices document",
            "title": "Security Guidelines",
            "category": "security",
        }
    ]
    return mock_loader


@pytest.fixture
def sample_review_result():
    """Sample review result for testing"""
    from datetime import datetime

    from models.data_models import ReviewResult

    return ReviewResult(
        rating=3,
        model_used="gpt-4",
        provider="openai",
        technique="zero_shot",
        execution_time=1.5,
        issues=[
            "Potential division by zero in divide function",
            "SQL injection vulnerability in get_user_data function",
            "Hardcoded password found",
        ],
        suggestions=[
            "Add error handling for division by zero",
            "Use parameterized queries to prevent SQL injection",
            "Move credentials to environment variables",
        ],
        reasoning="The code has several security and robustness issues that need attention.",
        technique_used="traditional",
        timestamp=datetime.now(),
    )


@pytest.fixture
def flask_test_client():
    """Flask test client for API testing"""
    from app import app

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This code has security vulnerabilities and needs improvement.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
    }


@pytest.fixture
def mock_chromadb_collection():
    """Mock ChromaDB collection for testing"""
    mock_collection = Mock()
    mock_collection.count.return_value = 100
    mock_collection.query.return_value = {
        "documents": [["Security best practices document"]],
        "metadatas": [[{"title": "Security Guidelines", "category": "security"}]],
        "distances": [[0.1]],
    }
    return mock_collection
