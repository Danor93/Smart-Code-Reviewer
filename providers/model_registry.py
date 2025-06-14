"""
Model registry and provider management for LangChain integration
"""

import logging
import os
from typing import Dict, Optional

import requests
import yaml
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import HuggingFaceHub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

# LangChain imports
from langchain_openai import ChatOpenAI

from models.data_models import ModelConfig

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Dynamic model registry with LangChain integration"""

    def __init__(self, config_path: str = "models_config.yaml"):
        self.config_path = config_path
        self.models: Dict[str, ModelConfig] = {}
        self.providers: Dict[str, Dict] = {}
        self.load_config()

    def load_config(self):
        """Load model configurations from YAML file"""
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)

            # Load model configs
            for model_id, model_data in config.get("models", {}).items():
                self.models[model_id] = ModelConfig(**model_data)

            # Load provider configs
            self.providers = config.get("providers", {})

            logger.info(f"Loaded {len(self.models)} models from config")

        except FileNotFoundError:
            logger.error(f"Config file {self.config_path} not found")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models with descriptions"""
        return {model_id: config.description for model_id, config in self.models.items() if self._is_model_available(model_id)}

    def _is_model_available(self, model_id: str) -> bool:
        """Check if model is available (API key exists or Ollama model exists)"""
        if model_id not in self.models:
            return False

        config = self.models[model_id]

        # Special case for Ollama models - check if model exists locally
        if config.provider == "ollama":
            return self._is_ollama_model_available(config.model_name)

        provider_config = self.providers.get(config.provider, {})
        env_var = config.env_var or provider_config.get("env_var")

        if env_var:
            return bool(os.getenv(env_var))
        return True

    def _is_ollama_model_available(self, model_name: str) -> bool:
        """Check if Ollama model is available locally"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"] == model_name for model in models)
        except (requests.RequestException, KeyError):
            pass
        return False

    def create_model(self, model_id: str):
        """Dynamically create a LangChain model instance"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found in registry")

        config = self.models[model_id]
        provider_config = self.providers.get(config.provider, {})

        # Check API key
        env_var = config.env_var or provider_config.get("env_var")
        if env_var and not os.getenv(env_var):
            raise ValueError(f"API key {env_var} not found for model {model_id}")

        # Create model based on provider
        if config.provider == "openai":
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        elif config.provider == "anthropic":
            return ChatAnthropic(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

        elif config.provider == "google":
            return ChatGoogleGenerativeAI(
                model=config.model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )

        elif config.provider == "huggingface":
            return HuggingFaceHub(
                repo_id=config.model_name,
                model_kwargs={
                    "temperature": config.temperature,
                    "max_length": config.max_tokens,
                },
                huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"),
            )

        elif config.provider == "ollama":
            provider_config = self.providers.get("ollama", {})
            return ChatOllama(
                model=config.model_name,
                temperature=config.temperature,
                num_predict=config.max_tokens,
                base_url=provider_config.get("base_url", "http://localhost:11434"),
            )

        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
