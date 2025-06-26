download_vocos_model:
	wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

download_checkpoint:
	wget -P tta_speech/checkpoints https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/model_1250000.safetensors

init: 

install:
	python -m venv .venv
	source .venv/bin/activate && \
	pip install -e ../aws -e ../types -e .

docker_build:
	cd .. && docker build --platform linux/amd64 -f speech/Dockerfile -t tta_speech .

docker_run:
	docker run --rm -it -p 5000:5000 --platform linux/amd64 --env-file .env.local tta_speech

run:
	@chmod +x ./run.sh
	@./run.sh

test:
	@set -a && source .env.local && set +a && cd tta_speech && python rp_handler.py
