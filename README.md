# 🤖 Enhanced Smart Code Reviewer

**Advanced LLM-Powered Code Analysis with Multi-Model Support**

A sophisticated code review system demonstrating LLM integration, prompt engineering techniques, and modular software architecture using multiple AI providers including OpenAI, Anthropic, Google, HuggingFace, and Ollama.

## 🎯 Learning Objectives

This project demonstrates key concepts for AI developer interviews:

- **LLM Architecture Understanding**: Practical application of transformer-based models
- **Prompt Engineering Mastery**: Implementation of multiple prompting techniques
- **API Integration**: Real-world usage of Claude and GPT APIs
- **Structured Output**: JSON parsing and error handling
- **Comparative Analysis**: Side-by-side evaluation of different approaches

## 🚀 Features

### Prompt Engineering Techniques Implemented

1. **Zero-Shot Prompting** - Direct task instruction without examples
2. **Few-Shot Prompting** - Learning from provided examples
3. **Chain-of-Thought (CoT)** - Step-by-step reasoning process
4. **Self-Consistency** - Multiple perspective synthesis

### AI Model Support

- ✅ **OpenAI** (GPT-4, GPT-4-Turbo, GPT-3.5-Turbo)
- ✅ **Anthropic Claude** (Claude 3.5 Sonnet, Claude 3 Haiku)
- ✅ **Google Gemini** (Gemini Pro, Gemini Flash)
- ✅ **HuggingFace Hub** (Open-source models)
- ✅ **Ollama** (Local model support - Mistral, Llama, etc.)
- 🔄 **Multi-Model Comparison** with performance metrics

### Code Review Capabilities

- 🔍 **Security Analysis** - Identifies vulnerabilities and hardcoded secrets
- ⚡ **Performance Review** - Spots optimization opportunities
- 📚 **Best Practices** - Suggests code improvements
- 🎯 **Quality Rating** - Structured assessment scoring

## 📦 Installation

### Quick Start

```bash
# Docker (Recommended)
git clone https://github.com/Danor93/Smart-Code-Reviewer.git
cd smart-code-reviewer
cp .env.example .env  # Add your API keys
./docker-run.sh run   # Start Flask API at http://localhost:8080
```

### Detailed Installation Instructions

📖 **For complete installation instructions, troubleshooting, and deployment options, see [INSTALL.md](INSTALL.md)**

### Prerequisites

- **Docker & Docker Compose** (for containerized deployment)
- **Python 3.8+** (for local installation)
- **At least one API key** from supported providers (OpenAI, Anthropic, Google, HuggingFace)
- **Optional**: Ollama for local models

### API Usage Examples

```bash
# Review a specific file
curl "http://localhost:8080/review/vulnerable_code.py?technique=zero_shot&model=gpt-4"

# Review custom code
curl -X POST http://localhost:8080/review-custom \
  -H "Content-Type: application/json" \
  -d '{"code": "def test(): pass", "technique": "zero_shot", "model": "gpt-4"}'
```

## 💡 Usage Examples

### Python API Usage

```python
from reviewers import EnhancedCodeReviewer

# Initialize the reviewer
reviewer = EnhancedCodeReviewer()

# Review with zero-shot prompting
result = await reviewer.review_code_async(
    code="def add(a, b): return a + b",
    language="python",
    technique="zero_shot",
    model_id="gpt-4"
)

print(f"Rating: {result.rating}")
print(f"Issues: {result.issues}")
print(f"Suggestions: {result.suggestions}")
```

### REST API Usage

```python
import requests

# Review code via REST API
response = requests.post('http://localhost:8080/review-custom', json={
    'code': 'def calculate_password_strength(password): return "weak"',
    'technique': 'zero_shot',
    'model': 'gpt-4'
})

result = response.json()
print(f"Rating: {result['rating']}")
print(f"Issues found: {len(result['issues'])}")
```

## 🏗️ Architecture

### Modular Design

The codebase follows a clean, modular architecture:

- **`models/`**: Data structures and type definitions
- **`providers/`**: LLM provider abstractions and model registry
- **`prompts/`**: Prompt engineering templates and techniques
- **`reviewers/`**: Core business logic for code analysis

### Key Design Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Extensibility**: Easy to add new models, prompts, or providers
- **Async Support**: Concurrent execution for better performance
- **Configuration-Driven**: YAML-based model configuration
- **Type Safety**: Proper type hints throughout the codebase
- **Isolated Dependencies**: Virtual environment ensures consistent package versions

### LangChain Integration

This project leverages LangChain's powerful framework to achieve seamless multi-provider LLM integration. Here's how specific LangChain features enable our enhanced code reviewer:

#### **1. Unified Provider Abstraction**

```python
# Single interface for multiple providers
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# All models share the same interface
model = ChatOpenAI(model="gpt-4")  # or ChatAnthropic, ChatGoogleGenerativeAI
response = await model.ainvoke(messages)
```

#### **2. Structured Message Handling**

```python
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are an expert code reviewer..."),
    HumanMessage(content="Analyze this code...")
]
```

**Benefits**: Consistent message formatting across all providers, eliminating provider-specific API differences.

#### **3. Async Execution Support**

```python
# Concurrent execution across multiple models
tasks = [model.ainvoke(messages) for model in models]
results = await asyncio.gather(*tasks)
```

**Benefits**: Dramatically faster model comparisons (3-5x speedup) by running multiple AI models simultaneously.

#### **4. Provider-Specific Optimizations**

- **OpenAI**: Automatic token counting and rate limiting
- **Anthropic**: Constitutional AI safety features
- **Google**: Gemini-specific parameter handling
- **HuggingFace**: Open-source model compatibility
- **Ollama**: Local model management and streaming

#### **5. Error Handling & Fallbacks**

```python
try:
    response = await model.ainvoke(messages)
except Exception as e:
    # LangChain provides consistent error types
    logger.error(f"Model {model_id} failed: {e}")
    return fallback_response
```

#### **6. Dynamic Model Loading**

```python
def create_model(self, model_id: str):
    if provider == "openai":
        return ChatOpenAI(model=config.model_name, **config.params)
    elif provider == "anthropic":
        return ChatAnthropic(model=config.model_name, **config.params)
    # ... supports 5+ providers seamlessly
```

**Key Achievement**: Without LangChain, we would need separate implementations for each provider's API, message formats, and error handling. LangChain's abstraction allows us to support 5+ AI providers with a single, maintainable codebase.

## 📊 Project Structure

```
smart-code-reviewer/
├── models/                      # Data models and structures
│   ├── __init__.py
│   └── data_models.py          # ReviewResult, ModelConfig classes
├── providers/                   # LLM provider integrations
│   ├── __init__.py
│   └── model_registry.py       # ModelRegistry with LangChain
├── prompts/                     # Prompt engineering templates
│   ├── __init__.py
│   └── templates.py            # Zero-shot, Few-shot, CoT prompts
├── reviewers/                   # Core review logic
│   ├── __init__.py
│   └── code_reviewer.py        # EnhancedCodeReviewer class
├── examples/                    # Sample code files for testing
│   ├── secure_code.py          # Good code examples
│   ├── vulnerable_code.py      # Security vulnerabilities
│   ├── performance_code.py     # Performance issues
│   ├── ml_pipeline.py          # Machine learning code
│   ├── async_web_crawler.py    # Async programming
│   ├── blockchain_simulation.py # Complex algorithms
│   └── complex_microservice.py # Microservice architecture
├── logs/                        # Application logs (created at runtime)
├── results/                     # Review results output directory
├── code-to-review/             # Directory for code files to review
├── app.py                      # Flask REST API service
├── enhanced_code_reviewer.py   # Command-line application entry point
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Multi-container Docker setup with Ollama
├── docker-run.sh              # Docker management script
├── .dockerignore              # Docker build context exclusions
├── models_config.yaml          # AI model configurations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your API keys (not in git)
├── .gitignore                 # Git ignore patterns
├── INSTALL.md                 # Detailed installation guide
└── README.md                  # This documentation
```

## 🧪 Testing the System

The project includes several test cases to demonstrate different scenarios:

### 1. Security Vulnerabilities

```python
test_code = '''
password = "admin123"  # Hardcoded password
sql_query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
'''
```

### 2. Performance Issues

```python
test_code = '''
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):        # O(n²) algorithm
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j]:
                duplicates.append(lst[i])
    return duplicates
'''
```

### 3. Best Practices

```python
test_code = '''
def calculate(x, y):  # Missing type hints and docstring
    return x * 2 + y  # No error handling
'''
```

## 📈 Interview Preparation

### Key Concepts Demonstrated

1. **Transformer Architecture**

   - Multi-head attention mechanisms
   - Token embeddings and positional encoding
   - Encoder-decoder vs decoder-only models

2. **Prompt Engineering**

   - Zero-shot vs few-shot trade-offs
   - Chain-of-thought reasoning benefits
   - Temperature and token parameter tuning

3. **Production Considerations**
   - Error handling and fallback strategies
   - API rate limiting and cost optimization
   - Structured output parsing

### Interview Questions You Can Answer

- _"How do you implement different prompting techniques?"_
- _"What are the trade-offs between Claude and GPT APIs?"_
- _"How do you handle unreliable LLM outputs in production?"_
- _"Explain the attention mechanism in transformers."_

## 🔧 Configuration

### Model Configuration

The system uses `models_config.yaml` for model settings:

```yaml
models:
  gpt-4:
    provider: openai
    model_name: gpt-4
    temperature: 0.1
    max_tokens: 1000
    description: "OpenAI GPT-4 - Most capable model"

  claude-3-5-sonnet:
    provider: anthropic
    model_name: claude-3-5-sonnet-20241022
    temperature: 0.1
    max_tokens: 1000
    description: "Anthropic Claude 3.5 Sonnet - Latest Claude model"
```

### Customization Options

- **Prompts**: Modify templates in `prompts/templates.py`
- **Models**: Add new providers in `providers/model_registry.py`
- **Languages**: Extend language support in prompts
- **Scoring**: Customize review algorithms in `reviewers/code_reviewer.py`
- **Configuration**: Update model settings in `models_config.yaml`

## 📚 Learning Resources

### 2025 Best Practices

- [Anthropic Claude 4 Documentation](https://docs.anthropic.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## 🎓 Next Steps

**Day 2**: RAG & Vector Databases

- Document chunking and embedding strategies
- Vector similarity search implementation
- Building a document Q&A system

**Day 3**: LangChain & AI Agents

- Agent architectures and tool usage
- Multi-step reasoning workflows
- Production deployment patterns
