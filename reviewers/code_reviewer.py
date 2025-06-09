"""
Enhanced code reviewer with LangChain and multi-model support
"""

import json
import time
import asyncio
import logging
from typing import Dict

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage

from models.data_models import ReviewResult
from providers.model_registry import ModelRegistry
from prompts.templates import EnhancedPromptTemplates

logger = logging.getLogger(__name__)


class EnhancedCodeReviewer:
    """Enhanced code reviewer with LangChain and multi-model support"""

    def __init__(self, config_path: str = "models_config.yaml"):
        self.model_registry = ModelRegistry(config_path)
        self.templates = EnhancedPromptTemplates()

    async def review_code_async(
        self,
        code: str,
        language: str = "python",
        technique: str = "zero_shot",
        model_id: str = "gpt-4",
    ) -> ReviewResult:
        """Async code review with specified model and technique"""
        start_time = time.time()

        try:
            # Get model configuration
            if model_id not in self.model_registry.models:
                available = list(self.model_registry.get_available_models().keys())
                raise ValueError(
                    f"Model {model_id} not available. Available: {available}"
                )

            model_config = self.model_registry.models[model_id]

            # Create model instance
            model = self.model_registry.create_model(model_id)

            # Select prompt template
            if technique == "zero_shot":
                prompt = self.templates.ZERO_SHOT_REVIEW.format(
                    language=language, code=code
                )
            elif technique == "few_shot":
                prompt = self.templates.FEW_SHOT_REVIEW.format(
                    language=language, code=code
                )
            elif technique == "cot":
                prompt = self.templates.COT_REVIEW.format(language=language, code=code)
            else:
                raise ValueError(f"Unknown technique: {technique}")

            # Create messages
            messages = [
                SystemMessage(content=self.templates.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            # Get response
            if hasattr(model, "ainvoke"):
                response = await model.ainvoke(messages)
            else:
                response = model.invoke(messages)

            # Extract response content
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            # Parse response
            result = self._parse_response(response_text)

            execution_time = time.time() - start_time

            return ReviewResult(
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
                rating=result.get("rating", "Unknown"),
                reasoning=result.get("reasoning", "No reasoning provided"),
                model_used=model_id,
                technique_used=technique,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                provider=model_config.provider,
                execution_time=execution_time,
                technique=technique,  # For backward compatibility
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ReviewResult(
                issues=[f"Error during review: {str(e)}"],
                suggestions=["Check model configuration and API keys"],
                rating="Error",
                reasoning=f"Failed to complete review: {str(e)}",
                model_used=model_id,
                technique_used=technique,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                provider="unknown",
                execution_time=execution_time,
                technique=technique,  # For backward compatibility
            )

    def review_code(self, *args, **kwargs) -> ReviewResult:
        """Synchronous wrapper for async review"""
        return asyncio.run(self.review_code_async(*args, **kwargs))

    def _parse_response(self, response: str) -> Dict:
        """Enhanced response parsing with multiple fallback methods"""
        try:
            # Method 1: Look for JSON block in code format
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end != -1:
                    json_str = response[start:end].strip()
                    return json.loads(json_str)

            # Method 2: Find first { to last }
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

            # Method 3: Try the whole response if it looks like JSON
            if response.strip().startswith("{"):
                return json.loads(response.strip())

            # Fallback: create structure from response
            return {
                "issues": ["Could not parse structured response"],
                "suggestions": ["Improve response format"],
                "rating": "Error",
                "reasoning": f"Parsing failed. Raw response: {response[:200]}...",
            }

        except json.JSONDecodeError as e:
            return {
                "issues": ["JSON parsing error"],
                "suggestions": ["Check response format"],
                "rating": "Error",
                "reasoning": f"JSON error: {e}. Response: {response[:200]}...",
            }

    async def compare_models_async(
        self, code: str, language: str = "python", technique: str = "zero_shot"
    ) -> Dict[str, ReviewResult]:
        """Compare multiple models on the same code"""
        available_models = self.model_registry.get_available_models()

        if not available_models:
            logger.warning("No models available for comparison")
            return {}

        # Create tasks for all available models
        tasks = []
        model_ids = []

        for model_id in available_models.keys():
            task = self.review_code_async(code, language, technique, model_id)
            tasks.append(task)
            model_ids.append(model_id)

        # Execute all reviews concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        comparison = {}
        for model_id, result in zip(model_ids, results):
            if isinstance(result, Exception):
                comparison[model_id] = ReviewResult(
                    issues=[f"Error: {result}"],
                    suggestions=["Check model configuration"],
                    rating="Error",
                    reasoning=str(result),
                    model_used=model_id,
                    technique_used=technique,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    provider="unknown",
                    execution_time=0.0,
                    technique=technique,  # For backward compatibility
                )
            else:
                comparison[model_id] = result

        return comparison

    def compare_models(self, *args, **kwargs) -> Dict[str, ReviewResult]:
        """Synchronous wrapper for async model comparison"""
        return asyncio.run(self.compare_models_async(*args, **kwargs))
