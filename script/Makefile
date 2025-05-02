install:
	pip install -e ../types -e ../aws -e .

run:
	uvicorn tta_script.main:app --reload

lint:
	pylint --rcfile=../.pylintrc tta_script tests

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests

docker_build:
	docker build --platform linux/amd64 -t audiobook_generator -f generator/Dockerfile ..

docker_run:
	docker run --platform linux/amd64 --env-file .env audiobook_generator
