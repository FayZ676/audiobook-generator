install:
	pip install -e .

lint:
	pylint --rcfile=../.pylintrc tta-service

run:
	uvicorn ttaservice.main:app --reload --port 8000