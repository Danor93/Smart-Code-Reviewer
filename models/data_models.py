"""
Data models for code review system
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ReviewResult:
    """Enhanced result from code review with model metadata"""

    issues: List[str]
    suggestions: List[str]
    rating: str
    reasoning: str
    model_used: str
    provider: str
    execution_time: float
    technique: str


@dataclass
class ModelConfig:
    """Configuration for a specific model"""

    provider: str
    model_name: str
    temperature: float
    max_tokens: int
    description: str
    env_var: Optional[str] = None
