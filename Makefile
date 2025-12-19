# English to Python Translator - Development Commands

.PHONY: help install test lint format type-check clean run setup

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup:  ## Setup development environment
	python setup_env.py

install:  ## Install dependencies
	pip install -r requirements.txt

test:  ## Run all tests
	pytest

test-unit:  ## Run unit tests only
	pytest -m unit

test-property:  ## Run property-based tests only
	pytest -m property

test-integration:  ## Run integration tests only
	pytest -m integration

test-coverage:  ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 src tests

format:  ## Format code with black
	black src tests

format-check:  ## Check code formatting
	black --check src tests

type-check:  ## Run type checking
	mypy src

check-all:  ## Run all checks (lint, format, type)
	make lint
	make format-check
	make type-check

clean:  ## Clean up generated files
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

run:  ## Run the application
	python main.py

dev:  ## Run in development mode (with checks)
	make check-all
	make test
	make run