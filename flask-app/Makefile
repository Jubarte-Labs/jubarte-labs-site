.PHONY: install test

install:
	pip install --upgrade pip
	pip install --verbose -r requirements.txt -r requirements-local.txt

test: install
	PYTHONPATH=. python -m pytest