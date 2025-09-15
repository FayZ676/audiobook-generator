download_vocos_model:
	test -f tta_f5/vocos/pytorch_model.bin || wget -P tta_f5/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

download_checkpoint:
	test -f tta_f5/checkpoints/model_1250000.safetensors || wget -P tta_f5/checkpoints https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/model_1250000.safetensors

install: download_vocos_model download_checkpoint
	test -d .venv || python -m venv .venv
	source .venv/bin/activate && \
	cd ../types && pip install -r requirements.txt && pip install -e . \
	&& cd ../f5 && pip install -r requirements.txt && pip install -e .

test:
	source .venv/bin/activate && \
	python tests/test_infer.py