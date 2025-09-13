install:
	cd ../f5 && make download_vocos_model download_checkpoint
	python -m venv .venv
	source .venv/bin/activate && \
	pip install -r requirements.txt && \
	pip install -e ../aws \
	-e ../types \
	-e ../f5 \
	-e .

docker_build:
	cd .. && docker build --platform linux/amd64 -f speech/Dockerfile -t tta_speech .

docker_run:
	docker run --rm -it -p 8001:8001 --platform linux/amd64 --env-file .env.local tta_speech

docker_inspect:
	docker run --rm -it --platform linux/amd64 --env-file .env.local tta_speech /bin/bash

run:
	@chmod +x ./run.sh
	@./run.sh

lint:
	(source .venv/bin/activate || . .venv/bin/activate) && \
	pylint --rcfile=../.pylintrc tta_speech

test:
	@set -a && source .env.local && set +a && cd tta_speech && python rp_handler.py
