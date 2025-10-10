.PHONY: install test format lint typecheck

install:
	pip install --upgrade pip
	pip install --verbose -r requirements.txt -r requirements-local.txt

test: install
	PYTHONPATH=. python -m pytest

format: install
	black .
	isort .

lint: install
	ruff check .

typecheck: install
	mypy .