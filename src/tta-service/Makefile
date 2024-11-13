# Initialize the virtual environment and install dependencies
init:
    python -m venv venv
    . venv/bin/activate && pip install -e .

# Run the FastAPI application
run:
    . venv/bin/activate && uvicorn main:app --reload --port 8002

# Run tests
test:
    . venv/bin/activate && pytest --cov=src --cov-report=term-missing tests/

# Setup Git hooks
setup_git_hook:
    echo '#!/bin/sh\nmake test' > .git/hooks/pre-push
    chmod +x .git/hooks/pre-push

# Complete setup
setup:
    make init
    make setup_git_hook
