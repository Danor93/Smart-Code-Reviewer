"""
Unit tests for ModelRegistry
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from providers.model_registry import ModelRegistry
from models.data_models import ModelConfig


class TestModelRegistry:
    """Test suite for ModelRegistry class"""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            "models": {
                "gpt-4": {
                    "provider": "openai",
                    "model_name": "gpt-4",
                    "description": "OpenAI GPT-4",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "env_var": "OPENAI_API_KEY",
                },
                "claude-3-sonnet": {
                    "provider": "anthropic",
                    "model_name": "claude-3-sonnet-20240229",
                    "description": "Anthropic Claude 3 Sonnet",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "env_var": "ANTHROPIC_API_KEY",
                },
            },
            "providers": {
                "openai": {"env_var": "OPENAI_API_KEY"},
                "anthropic": {"env_var": "ANTHROPIC_API_KEY"},
            },
        }

    @pytest.fixture
    def temp_config_file(self, sample_config, temp_dir):
        """Create a temporary config file"""
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(sample_config, f)
        return str(config_file)

    def test_init_with_valid_config(self, temp_config_file):
        """Test initialization with valid config file"""
        registry = ModelRegistry(config_path=temp_config_file)

        assert len(registry.models) == 2
        assert "gpt-4" in registry.models
        assert "claude-3-sonnet" in registry.models
        assert len(registry.providers) == 2

    def test_init_with_missing_config(self):
        """Test initialization with missing config file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            registry = ModelRegistry(config_path="nonexistent.yaml")
            assert len(registry.models) == 0
            assert len(registry.providers) == 0

    def test_init_with_invalid_yaml(self):
        """Test initialization with invalid YAML"""
        with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError):
                registry = ModelRegistry(config_path="invalid.yaml")
                assert len(registry.models) == 0

    def test_get_available_models_with_api_keys(self, temp_config_file):
        """Test getting available models when API keys are present"""
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "test-key", "ANTHROPIC_API_KEY": "test-key"},
        ):
            registry = ModelRegistry(config_path=temp_config_file)
            available = registry.get_available_models()

            assert len(available) == 2
            assert "gpt-4" in available
            assert "claude-3-sonnet" in available
            assert available["gpt-4"] == "OpenAI GPT-4"

    def test_get_available_models_without_api_keys(self, temp_config_file):
        """Test getting available models when API keys are missing"""
        with patch.dict("os.environ", {}, clear=True):
            registry = ModelRegistry(config_path=temp_config_file)
            available = registry.get_available_models()

            assert len(available) == 0

    def test_is_model_available_with_api_key(self, temp_config_file):
        """Test model availability check when API key exists"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            registry = ModelRegistry(config_path=temp_config_file)
            assert registry._is_model_available("gpt-4") is True

    def test_is_model_available_without_api_key(self, temp_config_file):
        """Test model availability check when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            registry = ModelRegistry(config_path=temp_config_file)
            assert registry._is_model_available("gpt-4") is False

    def test_is_model_available_nonexistent_model(self, temp_config_file):
        """Test model availability check for non-existent model"""
        registry = ModelRegistry(config_path=temp_config_file)
        assert registry._is_model_available("nonexistent-model") is False

    @patch("requests.get")
    def test_is_ollama_model_available_success(self, mock_get, temp_config_file):
        """Test Ollama model availability check - success case"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama2:latest"}]}
        mock_get.return_value = mock_response

        registry = ModelRegistry(config_path=temp_config_file)
        assert registry._is_ollama_model_available("llama2:latest") is True

    @patch("requests.get")
    def test_is_ollama_model_available_not_found(self, mock_get, temp_config_file):
        """Test Ollama model availability check - model not found"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "other-model:latest"}]}
        mock_get.return_value = mock_response

        registry = ModelRegistry(config_path=temp_config_file)
        assert registry._is_ollama_model_available("llama2:latest") is False

    @patch("requests.get")
    def test_is_ollama_model_available_connection_error(
        self, mock_get, temp_config_file
    ):
        """Test Ollama model availability check - connection error"""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")

        registry = ModelRegistry(config_path=temp_config_file)
        assert registry._is_ollama_model_available("llama2:latest") is False

    def test_create_model_openai(self, temp_config_file):
        """Test creating OpenAI model"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("providers.model_registry.ChatOpenAI") as mock_chat_openai:
                registry = ModelRegistry(config_path=temp_config_file)
                model = registry.create_model("gpt-4")

                mock_chat_openai.assert_called_once_with(
                    model="gpt-4", temperature=0.7, max_tokens=2048, api_key="test-key"
                )

    def test_create_model_anthropic(self, temp_config_file):
        """Test creating Anthropic model"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("providers.model_registry.ChatAnthropic") as mock_chat_anthropic:
                registry = ModelRegistry(config_path=temp_config_file)
                model = registry.create_model("claude-3-sonnet")

                mock_chat_anthropic.assert_called_once_with(
                    model="claude-3-sonnet-20240229",
                    temperature=0.7,
                    max_tokens=4096,
                    api_key="test-key",
                )

    def test_create_model_nonexistent(self, temp_config_file):
        """Test creating non-existent model raises error"""
        registry = ModelRegistry(config_path=temp_config_file)

        with pytest.raises(ValueError, match="Model nonexistent not found"):
            registry.create_model("nonexistent")

    def test_create_model_missing_api_key(self, temp_config_file):
        """Test creating model without API key raises error"""
        with patch.dict("os.environ", {}, clear=True):
            registry = ModelRegistry(config_path=temp_config_file)

            with pytest.raises(ValueError, match="API key.*not found"):
                registry.create_model("gpt-4")

    def test_create_model_unsupported_provider(self, temp_config_file, sample_config):
        """Test creating model with unsupported provider"""
        # Add unsupported provider to config
        sample_config["models"]["test-model"] = {
            "provider": "unsupported",
            "model_name": "test",
            "description": "Test model",
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        config_file = temp_config_file
        with open(config_file, "w") as f:
            yaml.dump(sample_config, f)

        registry = ModelRegistry(config_path=config_file)

        with pytest.raises(ValueError, match="Unsupported provider: unsupported"):
            registry.create_model("test-model")


@pytest.mark.unit
class TestModelConfig:
    """Test suite for ModelConfig data model"""

    def test_model_config_creation(self):
        """Test ModelConfig creation with valid data"""
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            description="OpenAI GPT-4",
            temperature=0.7,
            max_tokens=2048,
            env_var="OPENAI_API_KEY",
        )

        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.description == "OpenAI GPT-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.env_var == "OPENAI_API_KEY"

    def test_model_config_defaults(self):
        """Test ModelConfig with default env_var value"""
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2048,
            description="OpenAI GPT-4",
        )

        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.env_var is None  # Default value
