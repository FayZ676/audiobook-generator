install:
	python -m venv .venv
	source .venv/bin/activate && \
	pip install \
	-r requirements_dev.txt \
	-e .

lint:
	.venv/bin/python -m pylint --rcfile=../.pylintrc tta_script tests evals

types:
	.venv/bin/python -m mypy tta_script tests

test:
	pytest --cov=tta_script --cov-report=term-missing --cov-fail-under=80 tests
