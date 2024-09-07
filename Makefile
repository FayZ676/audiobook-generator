# Initializes the project by creating a virtual environment and installing the project dependencies.
init:
	python -m venv venv
	source venv/bin/activate && \
	pip install -e .
