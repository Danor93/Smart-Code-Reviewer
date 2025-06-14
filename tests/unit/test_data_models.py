"""
Unit tests for data models
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.data_models import ComparisonResult, ModelConfig, RAGContext, ReviewResult


@pytest.mark.unit
class TestReviewResult:
    """Test suite for ReviewResult data model"""

    def test_review_result_creation(self):
        """Test ReviewResult creation with valid data"""
        result = ReviewResult(
            issues=[
                {"type": "error", "message": "Issue 1"},
                {"type": "warning", "message": "Issue 2"},
            ],
            suggestions=[{"type": "improvement", "message": "Suggestion 1"}],
            rating="3/5",
            reasoning="The code has some issues.",
            model_used="gpt-4",
            technique_used="zero_shot",
            timestamp="2023-01-01T00:00:00Z",
            provider="openai",
            execution_time=1.5,
        )

        assert result.rating == "3/5"
        assert result.model_used == "gpt-4"
        assert result.provider == "openai"
        assert result.technique_used == "zero_shot"
        assert result.execution_time == 1.5
        assert len(result.issues) == 2
        assert len(result.suggestions) == 1
        assert result.reasoning == "The code has some issues."

    def test_review_result_required_fields(self):
        """Test ReviewResult with only required fields"""
        result = ReviewResult(
            issues=[],
            suggestions=[],
            rating="5/5",
            reasoning="Perfect code",
            model_used="gpt-4",
            technique_used="zero_shot",
            timestamp="2023-01-01T00:00:00Z",
        )

        assert len(result.issues) == 0
        assert len(result.suggestions) == 0
        assert result.rating == "5/5"
        assert result.provider is None

    def test_review_result_backward_compatibility(self):
        """Test ReviewResult backward compatibility with technique field"""
        result = ReviewResult(
            issues=[],
            suggestions=[],
            rating="4/5",
            reasoning="Good code",
            model_used="gpt-4",
            technique_used="few_shot",
            timestamp="2023-01-01T00:00:00Z",
            technique="few_shot",  # Deprecated field
        )

        assert result.technique_used == "few_shot"
        assert result.technique == "few_shot"

    def test_review_result_rag_fields(self):
        """Test ReviewResult with RAG-specific fields"""
        result = ReviewResult(
            issues=[],
            suggestions=[],
            rating="4/5",
            reasoning="RAG-enhanced review",
            model_used="gpt-4",
            technique_used="rag",
            timestamp="2023-01-01T00:00:00Z",
            guidelines_used=["PEP-8", "Security Guidelines"],
            rag_context_quality="high",
            num_guidelines=2,
            guideline_categories=["style", "security"],
        )

        assert len(result.guidelines_used) == 2
        assert result.rag_context_quality == "high"
        assert result.num_guidelines == 2
        assert len(result.guideline_categories) == 2


@pytest.mark.unit
class TestRAGContext:
    """Test suite for RAGContext data model"""

    def test_rag_context_creation(self):
        """Test RAGContext creation with valid data"""
        context = RAGContext(
            relevant_documents=[
                {"title": "Security Guidelines", "content": "Security best practices"},
                {"title": "Performance Tips", "content": "Performance optimization"},
            ],
            search_query="Python security best practices",
            context_quality="high",
            categories_used=["security", "performance"],
            total_context_length=1500,
        )

        assert len(context.relevant_documents) == 2
        assert context.search_query == "Python security best practices"
        assert context.context_quality == "high"
        assert len(context.categories_used) == 2
        assert context.total_context_length == 1500

    def test_rag_context_to_dict(self):
        """Test RAGContext serialization to dict"""
        context = RAGContext(
            relevant_documents=[{"title": "Test", "content": "Test content"}],
            search_query="test query",
            context_quality="medium",
            categories_used=["test"],
            total_context_length=100,
        )

        data = context.to_dict()

        assert data["search_query"] == "test query"
        assert data["context_quality"] == "medium"
        assert len(data["relevant_documents"]) == 1
        assert data["total_context_length"] == 100

    def test_rag_context_empty_documents(self):
        """Test RAGContext with empty documents"""
        context = RAGContext(
            relevant_documents=[],
            search_query="empty search",
            context_quality="low",
            categories_used=[],
            total_context_length=0,
        )

        assert len(context.relevant_documents) == 0
        assert len(context.categories_used) == 0
        assert context.total_context_length == 0


@pytest.mark.unit
class TestComparisonResult:
    """Test suite for ComparisonResult data model"""

    def test_comparison_result_creation(self):
        """Test ComparisonResult creation with valid data"""
        traditional_result = ReviewResult(
            issues=[{"type": "error", "message": "Issue 1"}],
            suggestions=[{"type": "improvement", "message": "Suggestion 1"}],
            rating="3/5",
            reasoning="Traditional review",
            model_used="gpt-4",
            technique_used="zero_shot",
            timestamp="2023-01-01T00:00:00Z",
        )

        rag_result = ReviewResult(
            issues=[
                {"type": "error", "message": "Issue 1"},
                {"type": "warning", "message": "Issue 2"},
            ],
            suggestions=[
                {"type": "improvement", "message": "Suggestion 1"},
                {"type": "enhancement", "message": "Suggestion 2"},
            ],
            rating="4/5",
            reasoning="RAG-enhanced review",
            model_used="gpt-4",
            technique_used="rag",
            timestamp="2023-01-01T00:00:00Z",
        )

        comparison = ComparisonResult(
            traditional_review=traditional_result,
            rag_enhanced_review=rag_result,
            improvement_metrics={
                "rating_improvement": 1,
                "additional_issues_found": 1,
                "additional_suggestions": 1,
                "guidelines_referenced": 5,
            },
            timestamp="2023-01-01T00:00:00Z",
        )

        assert comparison.traditional_review.rating == "3/5"
        assert comparison.rag_enhanced_review.rating == "4/5"
        assert comparison.improvement_metrics["rating_improvement"] == 1
        assert comparison.improvement_metrics["additional_issues_found"] == 1

    def test_comparison_result_to_dict(self):
        """Test ComparisonResult serialization to dict"""
        traditional_result = ReviewResult(
            issues=[],
            suggestions=[],
            rating="3/5",
            reasoning="Traditional",
            model_used="gpt-4",
            technique_used="zero_shot",
            timestamp="2023-01-01T00:00:00Z",
        )

        rag_result = ReviewResult(
            issues=[],
            suggestions=[],
            rating="4/5",
            reasoning="RAG",
            model_used="gpt-4",
            technique_used="rag",
            timestamp="2023-01-01T00:00:00Z",
        )

        comparison = ComparisonResult(
            traditional_review=traditional_result,
            rag_enhanced_review=rag_result,
            improvement_metrics={"test_metric": 123},
            timestamp="2023-01-01T00:00:00Z",
        )

        data = comparison.to_dict()

        assert "traditional_review" in data
        assert "rag_enhanced_review" in data
        assert "improvement_metrics" in data
        assert "timestamp" in data
        assert data["improvement_metrics"]["test_metric"] == 123


@pytest.mark.unit
class TestModelConfig:
    """Test suite for ModelConfig data model"""

    def test_model_config_creation(self):
        """Test ModelConfig creation with valid data"""
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2048,
            description="OpenAI GPT-4",
            env_var="OPENAI_API_KEY",
        )

        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.description == "OpenAI GPT-4"
        assert config.env_var == "OPENAI_API_KEY"

    def test_model_config_without_env_var(self):
        """Test ModelConfig without env_var (optional field)"""
        config = ModelConfig(
            provider="anthropic",
            model_name="claude-3-sonnet",
            temperature=0.5,
            max_tokens=4096,
            description="Anthropic Claude 3 Sonnet",
        )

        assert config.provider == "anthropic"
        assert config.model_name == "claude-3-sonnet"
        assert config.temperature == 0.5
        assert config.max_tokens == 4096
        assert config.description == "Anthropic Claude 3 Sonnet"
        assert config.env_var is None

    def test_model_config_different_providers(self):
        """Test ModelConfig with different providers"""
        configs = [
            ModelConfig("openai", "gpt-4", 0.7, 2048, "OpenAI GPT-4"),
            ModelConfig("anthropic", "claude-3", 0.5, 4096, "Anthropic Claude 3"),
            ModelConfig("google", "gemini-pro", 0.3, 8192, "Google Gemini Pro"),
            ModelConfig("ollama", "llama2", 0.8, 1024, "Local Llama 2"),
        ]

        assert len(configs) == 4
        assert configs[0].provider == "openai"
        assert configs[1].provider == "anthropic"
        assert configs[2].provider == "google"
        assert configs[3].provider == "ollama"
