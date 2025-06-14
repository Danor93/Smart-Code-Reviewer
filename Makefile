.PHONY: help install test test-unit test-api test-integration test-all test-coverage clean format lint docker-build docker-run

# Default target
help:
	@echo "Smart Code Reviewer - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Development:"
	@echo "  install          Install dependencies"
	@echo "  format           Format code with black and isort"
	@echo "  lint             Run linting and type checking"
	@echo "  clean            Clean cache and build artifacts"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-api         Run API tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage    Generate coverage report"
	@echo "  test-check       Check test environment"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run with Docker Compose"
	@echo "  docker-stop      Stop Docker containers"
	@echo ""

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Testing commands
test:
	python tests/run_tests.py --all

test-unit:
	python tests/run_tests.py --unit

test-api:
	python tests/run_tests.py --api

test-integration:
	python tests/run_tests.py --integration

test-coverage:
	python tests/run_tests.py --coverage

test-check:
	python tests/run_tests.py --check

# Code quality
format:
	black .
	isort .

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	bandit -r . -x tests/,venv/,examples/

# Cleanup
clean:
	python tests/run_tests.py --clean
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Docker commands
docker-build:
	docker build -t smart-code-reviewer:latest .

docker-run:
	./docker-run.sh run

docker-stop:
	docker-compose down

# Development server
dev:
	python app.py

# Quick development cycle
dev-test: format lint test-unit
	@echo "✅ Development cycle completed successfully!" 