install:
	python -m venv .venv
	source .venv/bin/activate && \
	pip install \
	-r ../types/requirements.txt \
	-r requirements_dev.txt \
	-e ../types \
	-e .

lint:
	.venv/bin/python -m pylint --rcfile=../.pylintrc tta_script tests

types:
	.venv/bin/python -m mypy tta_script tests

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests
