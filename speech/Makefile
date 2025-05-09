download_vocos_model:
	wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

init: download_vocos_model

install:
	pip install -e ../aws -e ../types -e .

run:
	python tta_speech/rp_handler.py --rp_serve_api --rp_api_port 8002

test:
	cd tta_speech && python rp_handler.py
