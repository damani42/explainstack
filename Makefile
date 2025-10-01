.PHONY: install install-dev run lint format test test-cov docs clean tox pre-commit

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	cd /Users/mbollo/explainstack && ./venv/bin/chainlit run explainstack/app.py -w

# Tox commands
tox:
	tox

tox-lint:
	tox -e lint

tox-format:
	tox -e format

tox-format-fix:
	tox -e format-fix

tox-security:
	tox -e security

tox-coverage:
	tox -e coverage

tox-docs:
	tox -e docs

tox-all:
	tox -e all

# Pre-commit hooks
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Individual linting commands
lint:
	flake8 explainstack/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy explainstack/ --ignore-missing-imports
	bandit -r explainstack/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

format:
	black explainstack/ tests/ --line-length=100
	isort explainstack/ tests/ --profile=black --line-length=100

format-check:
	black --check --diff explainstack/ tests/ --line-length=100
	isort --check-only --diff explainstack/ tests/ --profile=black --line-length=100

# Testing commands
test:
	python run_tests.py

test-cov:
	pytest --cov=explainstack --cov-report=html --cov-report=term-missing --cov-report=xml

test-unit:
	pytest tests/ -m "not integration" -v

test-integration:
	pytest tests/ -m integration -v

test-performance:
	pytest tests/ -m performance -v --benchmark-only

test-specific:
	pytest tests/$(TEST) -v

# Documentation
docs:
	cd docs && mkdocs serve

docs-build:
	cd docs && mkdocs build

# Security checks
security:
	bandit -r explainstack/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	semgrep --config=auto explainstack/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf bandit-report.json
	rm -rf safety-report.json
	rm -rf site/

# Development workflow
dev-setup: install-dev pre-commit
	@echo "Development environment setup complete!"

ci: tox-all
	@echo "All CI checks passed!"

# Help
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  dev-setup        Setup development environment"
	@echo "  run              Run the application"
	@echo "  test             Run tests"
	@echo "  test-cov         Run tests with coverage"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests"
	@echo "  lint             Run linting checks"
	@echo "  format           Format code"
	@echo "  format-check     Check code formatting"
	@echo "  security         Run security checks"
	@echo "  docs             Serve documentation"
	@echo "  docs-build       Build documentation"
	@echo "  clean            Clean up build artifacts"
	@echo "  tox              Run all tox environments"
	@echo "  tox-lint         Run linting with tox"
	@echo "  tox-format       Run format check with tox"
	@echo "  tox-security     Run security checks with tox"
	@echo "  tox-coverage     Run coverage with tox"
	@echo "  tox-docs         Build docs with tox"
	@echo "  tox-all          Run all quality checks with tox"
	@echo "  pre-commit       Install and run pre-commit hooks"
	@echo "  ci               Run all CI checks"
	@echo "  help             Show this help message"
