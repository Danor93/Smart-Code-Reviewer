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

### Prerequisites

- Python 3.8+
- At least one API key from supported providers (OpenAI, Anthropic, Google, HuggingFace)
- Optional: Ollama installed for local models

### Quick Setup

1. **Clone and Navigate**

   ```bash
   git clone git@github.com:Danor93/Smart-Code-Reviewer.git
   #or
   git clone https://github.com/Danor93/Smart-Code-Reviewer.git
   cd smart-code-reviewer
   ```

2. **Create and Activate Virtual Environment**

   **Why Virtual Environment?** Isolates project dependencies from your system Python, preventing conflicts and ensuring reproducible builds.

   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate

   # Verify activation (you should see (venv) in your terminal prompt)
   which python  # Should point to venv/bin/python
   ```

3. **Install Dependencies**

   ```bash
   # Upgrade pip to latest version
   pip install --upgrade pip

   # Install all project dependencies
   pip install -r requirements.txt

   # Verify installation
   pip list | grep langchain  # Should show LangChain packages
   ```

4. **Setup Environment Variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
   ```

5. **Run the Enhanced Code Reviewer**

   ```bash
   python enhanced_code_reviewer.py

   # Or review a specific file
   python enhanced_code_reviewer.py path/to/your/code.py

   # Or review all Python files in a directory
   python enhanced_code_reviewer.py /path/to/directory/
   ```

6. **When Finished (Optional)**

   ```bash
   # Deactivate virtual environment
   deactivate

   # Remove virtual environment (if you want to clean up)
   rm -rf venv/
   ```

## 🔑 Getting API Keys

You need at least one API key to use the system. The code reviewer will automatically detect which models are available based on your API keys.

### OpenAI API (Recommended)

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up for an account
3. Go to API Keys section
4. Generate a new secret key
5. **Free tier**: $5 in free credits for new users

### Anthropic Claude API

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. **Free tier**: $5 in free credits

### Google AI API

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign up and get API access
3. Generate an API key
4. **Free tier**: Generous free usage limits

### HuggingFace API

1. Visit [HuggingFace](https://huggingface.co/)
2. Create an account
3. Go to Settings → Access Tokens
4. Create a new token
5. **Free tier**: Access to many open-source models

### Ollama (Local Models)

1. Install [Ollama](https://ollama.ai/)
2. Pull models: `ollama pull mistral`
3. **Completely free**: Run models locally

## 💡 Usage Examples

### Basic Code Review

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
print(f"Model Used: {result.model_used}")
print(f"Execution Time: {result.execution_time:.2f}s")
```

### Technique Comparison

```python
# Compare different prompting techniques
techniques = ["zero_shot", "few_shot", "cot"]
for technique in techniques:
    result = await reviewer.review_code_async(code, "python", technique, "gpt-4")
    print(f"{technique}: {result.rating} - {len(result.issues)} issues")
```

### Multi-Model Comparison

```python
# Compare multiple AI models simultaneously
comparison = await reviewer.compare_models_async(code, "python", "zero_shot")
for model_id, result in comparison.items():
    print(f"{model_id}: {result.rating} ({result.execution_time:.2f}s)")
```

### Synchronous Usage

```python
# If you prefer synchronous calls
result = reviewer.review_code(code, "python", "zero_shot", "gpt-4")
print(f"Rating: {result.rating}")
```

## 🔧 Troubleshooting

### Virtual Environment Issues

**Problem**: `python3 -m venv venv` fails

```bash
# Solution: Install python3-venv package
sudo apt-get install python3-venv  # Ubuntu/Debian
brew install python3               # macOS
```

**Problem**: Virtual environment not activating

```bash
# Check if you're in the right directory
pwd  # Should show smart-code-reviewer directory
ls   # Should show venv/ folder

# Try absolute path
source /full/path/to/smart-code-reviewer/venv/bin/activate
```

**Problem**: `pip install` fails with permissions error

```bash
# Make sure virtual environment is activated first
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: LangChain import errors

```bash
# Verify installation
pip list | grep langchain
# If missing, reinstall
pip install --force-reinstall langchain langchain-openai langchain-anthropic
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
├── enhanced_code_reviewer.py   # Main application entry point
├── models_config.yaml          # AI model configurations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
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
