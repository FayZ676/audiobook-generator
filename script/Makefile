install:
	python -m venv .venv
	(source .venv/bin/activate || . .venv/bin/activate) && \
	pip install -e ../types -e ../aws -e . && \
	python -m spacy download en_core_web_trf

run:
	@chmod +x ./run.sh
	@./run.sh

lint:
	.venv/bin/python -m pylint --rcfile=../.pylintrc tta_script tests

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests

docker_build:
	docker build --platform linux/amd64 -t script_generator -f Dockerfile ..

docker_run:
	docker run -it -p 8001:8000 --platform linux/amd64 --env-file ../.env script_generator
