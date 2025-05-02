download_vocos_model:
	wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

init: download_vocos_model

install:
	pip install -e ../aws -e ../types -e .

run:
	uvicorn tta_speech.main:app --reload --port 8001
