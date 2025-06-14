"""
Data models for code review system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ReviewResult:
    """Enhanced result from code review with model metadata and RAG capabilities"""

    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    rating: str
    reasoning: str
    model_used: str
    technique_used: str
    timestamp: str

    # Traditional fields for backward compatibility
    provider: Optional[str] = None
    execution_time: Optional[float] = None
    technique: Optional[str] = None  # Deprecated, use technique_used

    # RAG-specific fields
    guidelines_used: Optional[List[str]] = field(default_factory=list)
    rag_context_quality: Optional[str] = None
    num_guidelines: Optional[int] = None
    guideline_categories: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization to handle backward compatibility"""
        if self.technique is not None and self.technique_used is None:
            self.technique_used = self.technique


@dataclass
class ModelConfig:
    """Configuration for a specific model"""

    provider: str
    model_name: str
    temperature: float
    max_tokens: int
    description: str
    env_var: Optional[str] = None


@dataclass
class RAGContext:
    """Context information for RAG-enhanced reviews"""

    relevant_documents: List[Dict[str, Any]]
    search_query: str
    context_quality: str
    categories_used: List[str]
    total_context_length: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "relevant_documents": self.relevant_documents,
            "search_query": self.search_query,
            "context_quality": self.context_quality,
            "categories_used": self.categories_used,
            "total_context_length": self.total_context_length,
        }


@dataclass
class ComparisonResult:
    """Result from comparing RAG vs traditional reviews"""

    traditional_review: ReviewResult
    rag_enhanced_review: ReviewResult
    improvement_metrics: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "traditional_review": self.traditional_review.__dict__,
            "rag_enhanced_review": self.rag_enhanced_review.__dict__,
            "improvement_metrics": self.improvement_metrics,
            "timestamp": self.timestamp,
        }
