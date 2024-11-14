# Installs the project dependencies
install:
	pip install -e .

lint:
	pylint --rcfile=../.pylintrc src

test:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80 tests
