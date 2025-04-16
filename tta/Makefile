# Installs the project dependencies
install:
	pip install -e ../tta-speech -e .

lint:
	pylint --rcfile=../.pylintrc tta tests

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests
