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
        return False

    try:
        from reviewers import RAGCodeReviewer

        print("✅ RAGCodeReviewer import successful")
    except ImportError as e:
        print(f"❌ RAGCodeReviewer import failed: {e}")
        return False

    try:
        from rag.document_loader import DocumentLoader
        from rag.vector_store import VectorStore

        print("✅ RAG components import successful")
    except ImportError as e:
        print(f"❌ RAG components import failed: {e}")
        return False

    try:
        from models.data_models import ReviewResult, RAGContext, ComparisonResult

        print("✅ Data models import successful")
    except ImportError as e:
        print(f"❌ Data models import failed: {e}")
        return False

    try:
        from app import app

        print("✅ Flask app import successful")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 Testing Smart Code Reviewer Imports")
    print("=" * 40)

    success = test_basic_imports()

    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n❌ Some imports failed!")
        sys.exit(1)
