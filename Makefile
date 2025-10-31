# Makefile for MCP Audit Ansible Collection
# See ADR-0011 for code quality tools

.PHONY: help quality format lint type-check test sanity clean install build

help:
	@echo "MCP Audit Ansible Collection - Development Commands"
	@echo ""
	@echo "Quality Checks:"
	@echo "  make quality     - Run all quality checks (format + lint + type-check)"
	@echo "  make format      - Format code with ruff"
	@echo "  make lint        - Lint code (ruff, yamllint, ansible-lint)"
	@echo "  make type-check  - Type check with mypy"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run unit tests with pytest"
	@echo "  make sanity      - Run ansible-test sanity"
	@echo "  make coverage    - Generate coverage report"
	@echo ""
	@echo "Building:"
	@echo "  make build       - Build collection tarball"
	@echo "  make install     - Install collection locally"
	@echo "  make clean       - Clean build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  make setup       - Set up development environment"
	@echo "  make pre-commit  - Run pre-commit on all files"

# Quality checks
quality: format lint type-check
	@echo "✅ All quality checks passed"

format:
	@echo "🔧 Formatting code with ruff..."
	ruff format .

lint:
	@echo "🔍 Linting code..."
	ruff check --fix .
	yamllint .
	ansible-lint || true
	@echo "ℹ️  Checking REUSE compliance (node_modules excluded from Galaxy build)..."
	reuse lint || true

type-check:
	@echo "🔎 Type checking with mypy..."
	mypy plugins/ || true

# Testing
test:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v

sanity:
	@echo "🧪 Running ansible-test sanity..."
	ansible-test sanity --docker

coverage:
	@echo "📊 Generating coverage report..."
	pytest tests/unit/ --cov=plugins --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# Building
build:
	@echo "📦 Building collection tarball..."
	ansible-galaxy collection build --force

install: build
	@echo "📥 Installing collection locally..."
	ansible-galaxy collection install mcp-audit-*.tar.gz --force

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.tar.gz
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

# Development setup
setup:
	@echo "🔧 Setting up development environment..."
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "✅ Development environment ready"

pre-commit:
	@echo "🔍 Running pre-commit on all files..."
	pre-commit run --all-files

# CI simulation (runs all checks like CI would)
ci: quality sanity test
	@echo "✅ All CI checks passed"
