.PHONY: install test lint format clean build run-cli run-web

# Installation
install:
	poetry install

install-dev:
	poetry install --with dev
	poetry run pre-commit install

# Testing
test:
	poetry run pytest tests/ -v

test-coverage:
	poetry run pytest tests/ --cov=src --cov-report=html

# Code quality
lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/

format:
	poetry run black src/ tests/
	poetry run isort src/ tests/

format-check:
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

# Running
run-cli:
	poetry run youtube-summarizer

run-web:
	poetry run streamlit run src/streamlit_app.py

# Building
build:
	poetry build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Docker
docker-build:
	docker build -t youtube-summarizer .

docker-run:
	docker run -p 8501:8501 youtube-summarizer

# Help
help:
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  install-dev    Install with dev dependencies"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage"
	@echo "  lint          Run linting"
	@echo "  format        Format code"
	@echo "  run-cli       Run CLI tool"
	@echo "  run-web       Run Streamlit web app"
	@echo "  build         Build package"
	@echo "  clean         Clean build artifacts"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"