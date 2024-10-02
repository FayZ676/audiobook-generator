# Initializes the project by creating a virtual environment and installing the project dependencies.
init:
	python -m venv venv
	source venv/bin/activate && \
	pip install -e .

# Runs linting on the entire application
lint_all:
	pylint src

test_all:
	pylint src
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80 src/tests

# Sets up a pre-push Git hook that runs the test_all command
setup_git_hook:
	echo '#!/bin/sh\nmake test_all' > .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "Pre-push hook has been set up successfully."
