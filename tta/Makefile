# Installs the project dependencies
install:
	pip install -e .

lint:
	pylint --rcfile=../.pylintrc tta

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests
