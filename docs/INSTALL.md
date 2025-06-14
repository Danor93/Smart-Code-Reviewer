# 📦 Installation Guide

**Complete setup instructions for the Enhanced Smart Code Reviewer**

This guide covers multiple installation methods and deployment options for the Smart Code Reviewer system.

## 🎯 Quick Start Options

- **🐳 [Docker Installation](#docker-installation-recommended)** - Easiest and most consistent
- **🐍 [Local Python Installation](#local-python-installation)** - Direct development setup
- **🌐 [Flask API Service](#flask-api-service)** - Web service deployment
- **🔑 [API Keys Setup](#getting-api-keys)** - Configure AI model access

## Prerequisites

- **Docker & Docker Compose** (for containerized deployment)
- **Python 3.8+** (for local installation)
- **At least one API key** from supported providers (OpenAI, Anthropic, Google, HuggingFace)
- **Optional**: Ollama installed for local models

## Docker Installation (Recommended) 🐳

**Docker provides a consistent, isolated environment and is the easiest way to get started.**

### 1. Install Docker

```bash
# On macOS with Homebrew:
brew install docker docker-compose

# On Ubuntu:
sudo apt-get update
sudo apt-get install docker.io docker-compose

# On Windows: Install Docker Desktop from https://docker.com
```

### 2. Clone and Setup

```bash
git clone https://github.com/Danor93/Smart-Code-Reviewer.git
cd smart-code-reviewer

# Create environment file
cp .env.example .env
# Edit .env with your API keys
nano .env
```

### 3. Run Flask API Service

```bash
# Method 1: Using the convenience script (recommended)
./docker-run.sh build          # Build the Docker image
./docker-run.sh run            # Start Flask API at http://localhost:8080

# Method 2: Using Docker Compose directly
docker-compose up --build

# Method 3: Using plain Docker
docker build -t smart-code-reviewer .
docker run -p 8080:5000 --env-file .env smart-code-reviewer
```

### 4. Legacy CLI Mode (Optional)

```bash
# Review a specific file (legacy mode)
./docker-run.sh file examples/vulnerable_code.py

# Review all Python files in a directory (legacy mode)
./docker-run.sh directory examples/

# Interactive CLI mode
./docker-run.sh interactive
```

### 5. Available Docker Commands

```bash
./docker-run.sh build          # Build the Docker image
./docker-run.sh run            # Start Flask API service
./docker-run.sh interactive    # Run in interactive mode
./docker-run.sh stop           # Stop all containers
./docker-run.sh clean          # Clean up containers and images
./docker-run.sh logs           # Show container logs
./docker-run.sh help           # Show all available commands
```

## Local Python Installation

### 1. Clone and Navigate

```bash
git clone https://github.com/Danor93/Smart-Code-Reviewer.git
cd smart-code-reviewer
```

### 2. Create and Activate Virtual Environment

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

### 3. Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep langchain  # Should show LangChain packages
pip list | grep langgraph  # Should show LangGraph package (NEW for agents)

# Key agent dependencies (automatically installed via requirements.txt)
# langgraph>=0.2.55          # State machine orchestration for AI agents
# langchain-core>=0.3.29     # Core LangChain functionality
# langchain-experimental>=0.3.30  # Experimental agent features
# pydantic>=2.0.0            # Data validation for agent state
```

### 4. Setup Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor
```

### 5. Run the Application

#### Option A: Legacy CLI Mode

```bash
# Run with default example
python enhanced_code_reviewer.py

# Review a specific file
python enhanced_code_reviewer.py path/to/your/code.py

# Review all Python files in a directory
python enhanced_code_reviewer.py /path/to/directory/
```

#### Option B: Flask API Service

```bash
# Start the Flask API server
python app.py

# Server will be available at http://localhost:5000
```

### 6. When Finished

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment (if you want to clean up)
rm -rf venv/
```

## Flask API Service

The Smart Code Reviewer includes a REST API service for web-based interactions.

### Starting the Service

**Docker (Recommended):**

```bash
./docker-run.sh run
# API available at http://localhost:8080
```

**Local Python:**

```bash
python app.py
# API available at http://localhost:5000
```

### API Endpoints

| Endpoint                   | Method | Description                              |
| -------------------------- | ------ | ---------------------------------------- |
| `/`                        | GET    | API information and health check         |
| `/models`                  | GET    | List available AI models                 |
| `/files`                   | GET    | List available example files             |
| `/review/<filename>`       | GET    | Review specific file from examples       |
| `/review-all`              | GET    | Review all files in examples directory   |
| `/review-custom`           | POST   | Review custom code                       |
| **🤖 AI Agent Endpoints**  |        | **NEW: Autonomous Agent System**         |
| `/agent/info`              | GET    | Get agent capabilities and configuration |
| `/agent/review`            | POST   | Autonomous agent code review             |
| `/agent/review/<filename>` | GET    | Agent review of example file             |

### API Usage Examples

```bash
# Get API info
curl http://localhost:8080/

# List available models
curl http://localhost:8080/models

# List available files
curl http://localhost:8080/files

# Review specific file
curl "http://localhost:8080/review/vulnerable_code.py?technique=zero_shot&model=gpt-4"

# Review all files
curl "http://localhost:8080/review-all?technique=zero_shot&model=gpt-4"

# Review custom code (POST)
curl -X POST http://localhost:8080/review-custom \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def test(): pass",
    "technique": "zero_shot",
    "model": "gpt-4",
    "language": "python"
  }'

# 🤖 NEW: AI Agent Endpoints
# Get agent capabilities
curl http://localhost:8080/agent/info

# Autonomous agent review (POST)
curl -X POST http://localhost:8080/agent/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def divide(a, b): return a / b",
    "language": "python",
    "user_request": "Check for potential runtime errors"
  }'

# Agent review of example file
curl http://localhost:8080/agent/review/vulnerable_code.py
```

## Getting API Keys

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

### Environment Variables Setup

Create a `.env` file in the project root:

```bash
# AI Provider API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
HUGGINGFACE_API_TOKEN=your-huggingface-token-here

# Local Model Configuration
OLLAMA_API_URL=http://localhost:11434

# Optional Configuration
LOG_LEVEL=INFO
DEFAULT_MODEL=gpt-4
DEFAULT_TECHNIQUE=zero_shot
MAX_TOKENS=1000
TEMPERATURE=0.1

# 🤖 NEW: AI Agent Configuration
MAX_AGENT_ITERATIONS=5      # Maximum reasoning iterations for agent
AGENT_DEFAULT_MODEL=gpt-4   # Default model for agent workflows
AGENT_TIMEOUT=300          # Agent timeout in seconds
```

## Usage Examples

### Basic Code Review (Python API)

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

### RAG-Enhanced Review

```python
from reviewers import RAGCodeReviewer

# Initialize RAG reviewer
rag_reviewer = RAGCodeReviewer()

# Perform RAG-enhanced review
result = await rag_reviewer.review_code_with_rag(
    code="password = 'admin123'",
    language="python"
)

print(f"Rating: {result.rating}")
print(f"Guidelines used: {result.num_guidelines}")
print(f"Categories: {result.guideline_categories}")
```

### Technique Comparison

```python
# Compare different prompting techniques
techniques = ["zero_shot", "few_shot", "cot"]
for technique in techniques:
    result = await reviewer.review_code_async(code, "python", technique, "gpt-4")
    print(f"{technique}: {result.rating} - {len(result.issues)} issues")
```

### RAG vs Traditional Comparison

```python
# Compare RAG vs traditional approaches
comparison = await rag_reviewer.compare_rag_vs_traditional(code, "python")
metrics = comparison.get("comparison", {})
print(f"Additional issues found: {metrics.get('additional_issues_found', 0)}")
print(f"Guidelines referenced: {metrics.get('guidelines_referenced', 0)}")
```

### Multi-Model Comparison

```python
# Compare multiple AI models simultaneously
comparison = await reviewer.compare_models_async(code, "python", "zero_shot")
for model_id, result in comparison.items():
    print(f"{model_id}: {result.rating} ({result.execution_time:.2f}s)")
```

### 🤖 AI Agent Usage (NEW!)

```python
from agents import CodeReviewAgent, CodeReviewRequest

# Initialize autonomous agent
agent = CodeReviewAgent(model_id="gpt-4")

# Create review request
request = CodeReviewRequest(
    code="def divide(a, b): return a / b",
    language="python",
    user_request="Focus on error handling and potential runtime issues"
)

# Run autonomous review (agent will reason, use tools, and synthesize)
result = await agent.review_code(request)

print(f"Agent completed {result['agent_analysis']['iterations']} reasoning iterations")
print(f"Tools used: {result['agent_analysis']['tools_used']}")
print(f"Review: {result['review_results']}")
```

### REST API Usage

```python
import requests

# Traditional review
response = requests.post('http://localhost:8080/review-custom', json={
    'code': 'def calculate_password_strength(password): return "weak"',
    'technique': 'zero_shot',
    'model': 'gpt-4',
    'language': 'python'
})

# RAG-enhanced review
response = requests.post('http://localhost:8080/rag/review-custom', json={
    'code': 'password = "admin123"',
    'language': 'python'
})

# 🤖 NEW: Autonomous agent review
response = requests.post('http://localhost:8080/agent/review', json={
    'code': 'def unsafe_eval(user_input): exec(user_input)',
    'language': 'python',
    'user_request': 'Security analysis please'
})

# Get agent capabilities
response = requests.get('http://localhost:8080/agent/info')

# Search guidelines
response = requests.post('http://localhost:8080/rag/search-guidelines', json={
    'query': 'password security',
    'k': 3
})

result = response.json()
print(f"Rating: {result['rating']}")
print(f"Issues found: {len(result['issues'])}")
```

## 🔧 Troubleshooting

### Docker Issues

**Problem**: Docker build fails with permission errors

```bash
# Solution: Fix Docker permissions
sudo usermod -aG docker $USER
# Log out and log back in, or restart terminal

# Alternative: Use sudo for Docker commands
sudo docker build -t smart-code-reviewer .
```

**Problem**: Port 5000/8080 already in use

```bash
# Check what's using the port
lsof -i :8080

# Change port in docker-compose.yml
ports:
  - "8081:5000"  # Use different host port
```

**Problem**: Container can't access API keys

```bash
# Verify .env file exists and has correct format
cat .env
# Should show: OPENAI_API_KEY=your-key-here

# Check container environment
docker run --rm --env-file .env smart-code-reviewer env | grep API
```

**Problem**: Volume mounting issues on Windows

```bash
# Use absolute paths for Windows
docker run -v C:\path\to\code:/app/code-to-review smart-code-reviewer

# Or use Docker Desktop with WSL2
```

### Python Installation Issues

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

### 🤖 AI Agent Issues (NEW!)

**Problem**: Agent import errors

```bash
# Verify agent dependencies
pip list | grep langgraph
pip list | grep pydantic

# Test agent imports
python -c "from agents import CodeReviewAgent; print('✅ Agent imports work')"

# If missing, reinstall agent dependencies
pip install --force-reinstall langgraph langchain-core langchain-experimental
```

**Problem**: Agent workflow timeout or infinite loops

```bash
# Check agent configuration in .env
grep AGENT .env

# Set reasonable limits
export MAX_AGENT_ITERATIONS=3
export AGENT_TIMEOUT=120

# Test with simpler code first
curl -X POST http://localhost:8080/agent/review \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"hello\")", "language": "python", "user_request": "quick review"}'
```

**Problem**: Agent tools not working

```bash
# Test individual tools
python -c "
from agents.tools import rag_code_review
result = rag_code_review.invoke({'code': 'def test(): pass', 'language': 'python', 'focus': 'general'})
print('✅ RAG tool works')
"

# Check RAG system status
curl http://localhost:8080/rag/knowledge-base/stats
```

### API Issues

**Problem**: "No models available" error

```bash
# Check your API keys in .env file
cat .env | grep API

# Test API key manually
curl -H "Authorization: Bearer YOUR-OPENAI-KEY" https://api.openai.com/v1/models
```

**Problem**: Flask service not starting

```bash
# Check if port is available
lsof -i :5000

# Check logs
./docker-run.sh logs

# Run in debug mode
export FLASK_DEBUG=true
python app.py
```

**Problem**: Slow response times

```bash
# Use faster models for testing
curl "http://localhost:8080/review/secure_code.py?model=gpt-3.5-turbo"

# Check model availability
curl http://localhost:8080/models
```

## 📊 Performance Tips

1. **Use GPT-3.5-Turbo** for faster responses during development
2. **Enable Docker BuildKit** for faster builds: `export DOCKER_BUILDKIT=1`
3. **Use local models** with Ollama for no API costs
4. **Cache Docker layers** by not changing requirements.txt frequently
5. **Run multiple workers** in production: edit `docker-compose.yml` to scale

## 🔒 Security Considerations

1. **Never commit .env files** to version control
2. **Use environment variables** in production deployments
3. **Limit API rate limits** to avoid unexpected charges
4. **Use HTTPS** when deploying the Flask API publicly
5. **Implement authentication** for production API deployments

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite with 50+ tests covering all major functionality.

#### Quick Test Commands

```bash
# Run all tests
make test

# Or using the test runner directly
python tests/run_tests.py --all

# Check test environment
python tests/run_tests.py --check
```

#### Specific Test Types

```bash
# Unit tests (50+ tests) - Fast, isolated tests
python tests/run_tests.py --unit

# API tests - Test all REST endpoints
python tests/run_tests.py --api

# Integration tests - Test RAG and Agent workflows
python tests/run_tests.py --integration

# Fast tests only (exclude slow tests)
python tests/run_tests.py --fast

# Run specific test file
python tests/run_tests.py --test tests/unit/test_api.py
```

#### Coverage Reports

```bash
# Generate coverage report
python tests/run_tests.py --coverage

# Check current coverage
python tests/check_coverage.py

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

#### Code Quality Checks

```bash
# Run all linting tools
make lint

# Individual tools
black --check .          # Code formatting
isort --check-only .     # Import sorting
flake8 .                 # Code linting
bandit -r . -x tests/,venv/,examples/  # Security scan

# Auto-format code
make format
# Or manually:
black .
isort .
```

#### Test Structure

```
tests/
├── unit/                        # Unit tests (50+ tests)
│   ├── test_api.py              # API endpoint tests (20 tests)
│   ├── test_data_models.py      # Data model tests (12 tests)
│   └── test_model_registry.py   # Model registry tests (18 tests)
├── integration/                 # Integration tests
│   ├── test_agent.py            # AI Agent workflow tests
│   └── test_rag.py              # RAG functionality tests
├── run_tests.py                 # Test runner with coverage
├── check_coverage.py            # Coverage analysis tool
└── test_imports.py              # Import verification
```

#### GitHub Actions CI/CD

The project includes automated testing via GitHub Actions:

```yaml
# .github/workflows/tests.yml
- Unit tests on Python 3.9, 3.10, 3.11
- API endpoint testing
- Integration test suite
- Code quality checks (Black, isort, flake8)
- Security scanning (Bandit)
- Coverage reporting
```

#### Test Coverage Goals

- ✅ **Unit Tests**: 90%+ coverage on core modules
- ✅ **API Tests**: 100% endpoint coverage
- ✅ **Integration Tests**: RAG and Agent workflows
- ✅ **Security**: Clean security scan (examples excluded)
- ✅ **Code Quality**: All linting tools pass

### Basic import tests

```bash
python tests/test_imports.py
```

### RAG functionality tests

```bash
python tests/integration/test_rag.py
```

### 🤖 AI Agent functionality tests

```bash
python tests/integration/test_agent.py
```

### Test specific components manually

```bash
python -c "from reviewers import EnhancedCodeReviewer; print('✅ Basic imports work')"
python -c "from reviewers import RAGCodeReviewer; print('✅ RAG imports work')"
python -c "from agents import CodeReviewAgent; print('✅ Agent imports work')"
```

### Docker Testing

```bash
# Build and test container
docker build -t smart-code-reviewer:test .
docker run --rm -d --name test-container -p 8080:5000 \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  smart-code-reviewer:test

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/rag/knowledge-base/stats

# 🤖 Test agent endpoints
curl http://localhost:8080/agent/info
curl -X POST http://localhost:8080/agent/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def test(): pass", "language": "python", "user_request": "general review"}'

# Clean up
docker stop test-container
```

### Test Scenarios

The system includes comprehensive test cases covering:

1. **Security Vulnerabilities**

   - Hardcoded passwords
   - SQL injection vulnerabilities
   - Insecure cryptographic practices

2. **Performance Issues**

   - Inefficient algorithms (O(n²) complexity)
   - Memory leaks
   - Blocking I/O operations

3. **Best Practices**

   - Missing type hints
   - Lack of documentation
   - Error handling gaps

4. **AI Agent Workflows**
   - Multi-step reasoning
   - Tool coordination
   - Error recovery

## 🚀 Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (nginx) in front of the Flask app
2. **Add SSL/TLS certificates** for HTTPS
3. **Implement rate limiting** and authentication
4. **Use a production WSGI server** (already using Gunicorn)
5. **Add monitoring and logging** solutions
6. **Scale with Docker Swarm** or Kubernetes

---

For more information, see the main [README.md](README.md) file.
