#!/usr/bin/env python3
"""
Simple import test for Smart Code Reviewer components
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))


def test_basic_imports():
    """Test that all major components can be imported"""
    try:
        from reviewers import EnhancedCodeReviewer

        print("✅ EnhancedCodeReviewer import successful")
    except ImportError as e:
        print(f"❌ EnhancedCodeReviewer import failed: {e}")
        assert False, f"EnhancedCodeReviewer import failed: {e}"

    try:
        from reviewers import RAGCodeReviewer

        print("✅ RAGCodeReviewer import successful")
    except ImportError as e:
        print(f"❌ RAGCodeReviewer import failed: {e}")
        assert False, f"RAGCodeReviewer import failed: {e}"

    try:
        from rag.document_loader import DocumentLoader
        from rag.vector_store import VectorStore

        print("✅ RAG components import successful")
    except ImportError as e:
        print(f"❌ RAG components import failed: {e}")
        assert False, f"RAG components import failed: {e}"

    try:
        from models.data_models import ComparisonResult, RAGContext, ReviewResult

        print("✅ Data models import successful")
    except ImportError as e:
        print(f"❌ Data models import failed: {e}")
        assert False, f"Data models import failed: {e}"

    try:
        from app import app

        print("✅ Flask app import successful")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        assert False, f"Flask app import failed: {e}"

    # If we get here, all imports succeeded
    assert True


if __name__ == "__main__":
    print("🧪 Testing Smart Code Reviewer Imports")
    print("=" * 40)

    test_basic_imports()
    print("\n🎉 All imports successful!")
