.PHONY: install install-dev run lint format test test-cov docs clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	chainlit run explainstack/app.py -w

lint:
	flake8 explainstack/
	mypy explainstack/

format:
	black explainstack/
	isort explainstack/

test:
	python run_tests.py

test-cov:
	pytest --cov=explainstack --cov-report=html --cov-report=term-missing

test-specific:
	pytest tests/$(TEST) -v

docs:
	cd docs && mkdocs serve

docs-build:
	cd docs && mkdocs build

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
