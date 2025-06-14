"""
Unit tests for Flask API endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch

from models.data_models import ReviewResult


@pytest.mark.api
class TestApiEndpoints:
    """Test suite for Flask API endpoints"""

    def test_home_endpoint(self, flask_test_client):
        """Test the home/health check endpoint"""
        response = flask_test_client.get("/")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["service"] == "Enhanced Smart Code Reviewer API"
        assert data["status"] == "running"
        assert "endpoints" in data
        assert "available_models" in data
        assert "available_files" in data

    def test_models_endpoint(self, flask_test_client, mock_model_registry):
        """Test the models endpoint"""
        with patch("app.reviewer.model_registry", mock_model_registry):
            response = flask_test_client.get("/models")

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "models" in data
            assert data["count"] == 3

    def test_models_endpoint_error(self, flask_test_client):
        """Test the models endpoint error handling"""
        with patch(
            "app.reviewer.model_registry.get_available_models",
            side_effect=Exception("Test error"),
        ):
            response = flask_test_client.get("/models")

            assert response.status_code == 500
            data = json.loads(response.data)

            assert data["success"] is False
            assert "error" in data

    def test_files_endpoint(self, flask_test_client):
        """Test the files endpoint"""
        with patch("app.get_available_files", return_value=["test.py"]):
            with patch("app.read_file_content", return_value="def test(): pass"):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 100
                    mock_stat.return_value.st_mtime = 1234567890

                    response = flask_test_client.get("/files")

                    assert response.status_code == 200
                    data = json.loads(response.data)

                    assert data["success"] is True
                    assert len(data["files"]) == 1
                    assert data["files"][0]["filename"] == "test.py"

    def test_files_endpoint_error(self, flask_test_client):
        """Test the files endpoint error handling"""
        with patch("app.get_available_files", side_effect=Exception("Test error")):
            response = flask_test_client.get("/files")

            assert response.status_code == 500
            data = json.loads(response.data)

            assert data["success"] is False
            assert "error" in data

    def test_review_custom_endpoint(self, flask_test_client, sample_review_result):
        """Test the custom code review endpoint"""
        with patch("app.reviewer.review_code_async", return_value=sample_review_result):
            test_data = {
                "code": "def test(): pass",
                "language": "python",
                "technique": "zero_shot",
            }

            response = flask_test_client.post(
                "/review-custom",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "rating" in data
            assert data["rating"] == 3
            assert len(data["issues"]) == 3

    def test_review_custom_endpoint_missing_code(self, flask_test_client):
        """Test custom review endpoint with missing code"""
        test_data = {"language": "python", "technique": "zero_shot"}

        response = flask_test_client.post(
            "/review-custom",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)

        assert data["success"] is False
        assert "error" in data

    def test_review_custom_endpoint_error(self, flask_test_client):
        """Test custom review endpoint error handling"""
        with patch(
            "app.reviewer.review_code_async", side_effect=Exception("Review error")
        ):
            test_data = {"code": "def test(): pass", "language": "python"}

            response = flask_test_client.post(
                "/review-custom",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 500
            data = json.loads(response.data)

            assert data["success"] is False
            assert "error" in data

    def test_review_file_endpoint(self, flask_test_client, sample_review_result):
        """Test file review endpoint"""
        with patch("app.get_available_files", return_value=["test.py"]):
            with patch("app.read_file_content", return_value="def test(): pass"):
                with patch(
                    "app.reviewer.review_code", return_value=sample_review_result
                ):
                    response = flask_test_client.get("/review/test.py?model=gpt-4")

                    assert response.status_code == 200
                    data = json.loads(response.data)

                    assert data["success"] is True
                    assert "rating" in data
                    assert data["filename"] == "test.py"

    def test_review_file_not_found(self, flask_test_client):
        """Test file review endpoint with non-existent file"""
        with patch("app.get_available_files", return_value=["other.py"]):
            response = flask_test_client.get("/review/nonexistent.py")

            assert response.status_code == 404
            data = json.loads(response.data)

            assert data["success"] is False
            assert "error" in data

    def test_rag_review_custom_endpoint(self, flask_test_client, sample_review_result):
        """Test RAG custom review endpoint"""
        with patch(
            "app.rag_reviewer.review_code_with_rag", return_value=sample_review_result
        ):
            test_data = {"code": "def test(): pass", "language": "python"}

            response = flask_test_client.post(
                "/rag/review-custom",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "rating" in data

    def test_rag_compare_endpoint(self, flask_test_client):
        """Test RAG comparison endpoint"""
        mock_comparison = {
            "traditional_review": {"rating": 3, "issues": ["Issue 1"]},
            "rag_review": {"rating": 4, "issues": ["Issue 1", "Issue 2"]},
            "comparison": {
                "rating_improvement": 1,
                "additional_issues_found": 1,
                "additional_suggestions": 2,
                "guidelines_referenced": 3,
            },
        }

        with patch(
            "app.rag_reviewer.compare_rag_vs_traditional", return_value=mock_comparison
        ):
            test_data = {"code": "def test(): pass", "language": "python"}

            response = flask_test_client.post(
                "/rag/compare",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "comparison" in data

    def test_rag_search_guidelines_endpoint(self, flask_test_client):
        """Test RAG search guidelines endpoint"""
        mock_results = [
            {
                "content": "Use proper error handling",
                "title": "Error Handling Guide",
                "category": "best_practices",
            }
        ]

        with patch("app.rag_reviewer.search_guidelines", return_value=mock_results):
            test_data = {"query": "error handling", "k": 5}

            response = flask_test_client.post(
                "/rag/search-guidelines",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert len(data["results"]) == 1

    def test_rag_knowledge_base_stats_endpoint(self, flask_test_client):
        """Test RAG knowledge base stats endpoint"""
        mock_stats = {
            "rag_initialized": True,
            "vector_store_stats": {"total_documents": 100},
            "available_categories": ["security", "performance"],
        }

        with patch(
            "app.rag_reviewer.get_knowledge_base_stats", return_value=mock_stats
        ):
            response = flask_test_client.get("/rag/knowledge-base/stats")

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "stats" in data

    def test_agent_info_endpoint(self, flask_test_client):
        """Test agent info endpoint"""
        mock_info = {
            "model": "gpt-4",
            "capabilities": ["code_review", "rag_search"],
            "available_tools": ["traditional_review", "rag_review"],
        }

        with patch("app.code_agent.get_agent_info", return_value=mock_info):
            response = flask_test_client.get("/agent/info")

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "agent_info" in data

    def test_agent_review_custom_endpoint(self, flask_test_client):
        """Test agent custom review endpoint"""
        mock_result = {
            "rating": 4,
            "summary": "Code review completed",
            "detailed_analysis": "Analysis details",
            "recommendations": ["Recommendation 1"],
        }

        with patch("app.code_agent.review_code", return_value=mock_result):
            test_data = {
                "code": "def test(): pass",
                "language": "python",
                "user_request": "Focus on security",
            }

            response = flask_test_client.post(
                "/agent/review",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "agent_review" in data

    def test_404_error_handler(self, flask_test_client):
        """Test 404 error handler"""
        response = flask_test_client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        data = json.loads(response.data)

        assert data["success"] is False
        assert "error" in data
        assert "available_endpoints" in data

    def test_500_error_handler(self, flask_test_client):
        """Test 500 error handler"""
        with patch(
            "app.reviewer.model_registry.get_available_models",
            side_effect=Exception("Internal error"),
        ):
            response = flask_test_client.get("/models")

            assert response.status_code == 500
            data = json.loads(response.data)

            assert data["success"] is False
            assert "error" in data


@pytest.mark.api
@pytest.mark.integration
class TestApiIntegration:
    """Integration tests for API endpoints"""

    def test_full_review_workflow(self, flask_test_client, sample_review_result):
        """Test complete review workflow"""
        # 1. Get available models
        with patch(
            "app.reviewer.model_registry.get_available_models",
            return_value={"gpt-4": "GPT-4"},
        ):
            models_response = flask_test_client.get("/models")
            assert models_response.status_code == 200

        # 2. Review code with traditional method
        with patch("app.reviewer.review_code", return_value=sample_review_result):
            review_data = {
                "code": "def test(): pass",
                "language": "python",
                "model": "gpt-4",
            }

            review_response = flask_test_client.post(
                "/review-custom",
                data=json.dumps(review_data),
                content_type="application/json",
            )
            assert review_response.status_code == 200

        # 3. Compare with RAG
        mock_comparison = {
            "traditional_review": {"rating": 3},
            "rag_review": {"rating": 4},
            "comparison": {"rating_improvement": 1},
        }

        with patch(
            "app.rag_reviewer.compare_rag_vs_traditional", return_value=mock_comparison
        ):
            compare_response = flask_test_client.post(
                "/rag/compare",
                data=json.dumps({"code": "def test(): pass", "language": "python"}),
                content_type="application/json",
            )
            assert compare_response.status_code == 200

    def test_cors_headers(self, flask_test_client):
        """Test CORS headers are properly set"""
        response = flask_test_client.options("/")

        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers
