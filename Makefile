# Initializes the project by creating a virtual environment and installing the project dependencies.
init:
	python -m venv venv
	source venv/bin/activate && \
	pip install -e .

test_all:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80 src/tests
