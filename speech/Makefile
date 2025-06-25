download_vocos_model:
	@echo "DEPRECATED: Use 'make upload_model_to_s3' instead"
	@echo "Direct download from HuggingFace is no longer recommended for security reasons"
	wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

init: 

install:
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
