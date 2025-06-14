# 🤖 Enhanced Smart Code Reviewer

**AI-Powered Code Analysis with RAG (Retrieval-Augmented Generation)**

A sophisticated code review system demonstrating LLM integration, RAG implementation, and multi-model support using OpenAI, Anthropic, Google, HuggingFace, and Ollama.

## 🚀 Quick Start

```bash
# Docker (Recommended)
git clone https://github.com/Danor93/Smart-Code-Reviewer.git
cd smart-code-reviewer
cp .env.example .env  # Add your API keys
./docker-run.sh run   # Start at http://localhost:8080

# Test RAG functionality
curl http://localhost:8080/rag/knowledge-base/stats
```

## ✨ Key Features

### 🧠 **RAG-Enhanced Reviews**

- **Knowledge-Aware Analysis** - Reviews using industry best practices
- **Vector Search** - Semantic similarity through coding guidelines
- **Contextual Suggestions** - Recommendations based on established standards
- **Comparative Analytics** - Side-by-side RAG vs traditional analysis

### 🤖 **AI Agent System**

- **Autonomous Code Review** - Self-directing AI agent with ReAct pattern
- **Multi-Tool Coordination** - RAG search, traditional review, guidelines lookup
- **LangGraph Workflow** - Complex state machine orchestration
- **Intelligent Reasoning** - Multi-step decision making and iteration
- **Professional Reports** - Comprehensive analysis with executive summaries

### 🤖 **Multi-Model Support**

- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude 3.5 Sonnet)
- **Google** (Gemini Pro)
- **HuggingFace** (Open-source models)
- **Ollama** (Local models)

### 🎯 **Advanced Techniques**

- **Zero-Shot** - Direct instruction
- **Few-Shot** - Learning from examples
- **Chain-of-Thought** - Step-by-step reasoning
- **RAG** - Knowledge-augmented generation

## 📊 What It Detects

- 🔒 **Security Vulnerabilities** (SQL injection, hardcoded secrets)
- ⚡ **Performance Issues** (inefficient algorithms, memory leaks)
- 📚 **Best Practices** (code style, documentation)
- 🏗️ **Architecture** (design patterns, maintainability)

## 🌐 API Endpoints

```bash
# Traditional review
curl "http://localhost:8080/review/vulnerable_code.py?model=gpt-4"

# RAG-enhanced review
curl -X POST http://localhost:8080/rag/review-custom \
  -H "Content-Type: application/json" \
  -d '{"code": "password = \"admin123\"", "language": "python"}'

# 🤖 NEW: Autonomous AI Agent Review
curl -X POST http://localhost:8080/agent/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def divide(a, b): return a / b", "language": "python", "user_request": "Focus on error handling"}'

# Agent capabilities and info
curl http://localhost:8080/agent/info

# Agent review of example file
curl http://localhost:8080/agent/review/vulnerable_code.py

# Compare approaches
curl -X POST http://localhost:8080/rag/compare \
  -H "Content-Type: application/json" \
  -d '{"code": "def test(): pass", "language": "python"}'
```

## 🧪 Testing & Quality Assurance

**Comprehensive test suite with 50+ tests and automated CI/CD pipeline:**

```bash
# Run all tests
make test

# Run specific test types
python tests/run_tests.py --unit        # Unit tests (50 tests)
python tests/run_tests.py --api         # API endpoint tests
python tests/run_tests.py --integration # Integration tests
python tests/run_tests.py --coverage    # Coverage report

# Code quality checks
make lint    # Black, isort, flake8
make format  # Auto-format code
```

**Test Coverage:**

- ✅ **Unit Tests** - Core functionality (90%+ coverage)
- ✅ **API Tests** - All endpoints tested
- ✅ **Integration Tests** - RAG & Agent workflows
- ✅ **Security Scans** - Bandit security analysis
- ✅ **Code Quality** - Black, isort, flake8 linting
- ✅ **GitHub Actions** - Automated CI/CD pipeline

## 📖 Documentation

- **📚 [Complete Documentation](docs/)** - All project documentation
- **🏗️ [System Design](docs/SYSTEM_DESIGN.md)** - Architecture and design patterns
- **📦 [Installation Guide](docs/INSTALL.md)** - Complete setup instructions
- **🐳 [Docker Setup](docs/INSTALL.md#docker-installation-recommended)** - Containerized deployment
- **🔧 [Troubleshooting](docs/INSTALL.md#troubleshooting)** - Common issues and solutions
- **🔑 [API Keys](docs/INSTALL.md#getting-api-keys)** - Provider setup guide

## 🏗️ Project Structure

```tree
smart-code-reviewer/
├── docs/                            # 📚 Project Documentation
│   ├── README.md                    # Documentation index
│   ├── SYSTEM_DESIGN.md             # System architecture and design
│   └── INSTALL.md                   # Installation and setup guide
├── agents/                          # 🤖 AI Agent System
│   ├── code_review_agent.py         # Autonomous LangGraph agent with ReAct pattern
│   ├── tools.py                     # Agent tools
│   └── README.md                    # Comprehensive agent documentation
├── models/                          # Data models and structures
│   └── data_models.py               # ReviewResult, RAGContext, ComparisonResult
├── providers/                       # LLM provider integrations
│   └── model_registry.py            # ModelRegistry with LangChain
├── prompts/                         # Prompt engineering templates
│   └── templates.py                 # Zero-shot, Few-shot, CoT prompts
├── reviewers/                       # Core review logic
│   ├── code_reviewer.py             # EnhancedCodeReviewer class
│   └── rag_code_reviewer.py         # RAGCodeReviewer with vector search
├── rag/                             # RAG implementation
│   ├── document_loader.py           # Document chunking and loading
│   └── vector_store.py              # ChromaDB vector operations
├── rag-knowledge-base/              # Coding guidelines and best practices
│   ├── coding-standards/
│   │   └── python-pep8.md           # PEP 8 style guidelines
│   ├── security-guidelines/
│   │   └── owasp-top10.md           # OWASP security practices
│   ├── performance-tips/
│   │   └── python-optimization.md   # Performance best practices
│   └── documentation/
│       └── code-review-checklist.md # Comprehensive review checklist
├── examples/                        # Sample code files for testing
│   ├── secure_code.py               # Good code examples
│   ├── vulnerable_code.py           # Security vulnerabilities
│   ├── performance_code.py          # Performance issues
│   ├── ml_pipeline.py               # Machine learning code
│   ├── async_web_crawler.py         # Async programming
│   ├── blockchain_simulation.py     # Complex algorithms
│   └── complex_microservice.py      # Microservice architecture
├── tests/                           # 🧪 Comprehensive Test Suite
│   ├── unit/                        # Unit tests (50+ tests)
│   │   ├── test_api.py              # API endpoint tests
│   │   ├── test_data_models.py      # Data model tests
│   │   └── test_model_registry.py   # Model registry tests
│   ├── integration/                 # Integration tests
│   │   ├── test_agent.py            # AI Agent workflow tests
│   │   └── test_rag.py              # RAG functionality tests
│   ├── run_tests.py                 # Test runner with coverage
│   ├── check_coverage.py            # Coverage analysis tool
│   └── test_imports.py              # Import verification
├── .github/workflows/               # CI/CD Pipeline
│   └── tests.yml                    # Automated testing workflow
├── logs/                            # Application logs (created at runtime)
├── results/                         # Review results output directory
├── chroma_db/                       # ChromaDB vector database (created at runtime)
├── code-to-review/                  # Directory for user code files
├── app.py                           # Flask REST API service
├── enhanced_code_reviewer.py        # Command-line application entry point
├── models_config.yaml               # AI model configurations
├── requirements.txt                 # Python dependencies
├── pytest.ini                      # Pytest configuration
├── .flake8                          # Flake8 linting configuration
├── pyproject.toml                   # Black & isort configuration
├── Makefile                         # Build and test automation
├── Dockerfile                       # Docker container configuration
├── docker-compose.yml               # Multi-container Docker setup
├── docker-run.sh                    # Docker management script
├── .dockerignore                    # Docker build context exclusions
├── .env.example                     # Environment variables template
├── .env                             # Your API keys (not in git)
├── .gitignore                       # Git ignore patterns
├── INSTALL.md                       # Detailed installation guide
└── README.md                        # This documentation
```
