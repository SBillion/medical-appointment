.PHONY: install dev test test-unit test-integration test-cov lint format check clean hooks typecheck

install:
	uv sync
	uv run pre-commit install

hooks:
	uv run pre-commit install

dev:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

test-unit:
	uv run pytest tests/unit

test-integration:
	uv run pytest tests/integration

test-cov:
	uv run pytest --cov=src/app --cov-report=term-missing --cov-report=html

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/app

check: lint typecheck

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage