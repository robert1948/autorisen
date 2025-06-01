# backend/Makefile

.PHONY: install run test lint format clean

install:
	pip install -e .[dev]

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests

lint:
	flake8 src tests

format:
	black src tests

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
