download_vocos_model:
	@echo "DEPRECATED: Use 'make upload_model_to_s3' instead"
	@echo "Direct download from HuggingFace is no longer recommended for security reasons"
	wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

upload_model_to_s3:
	@echo "Uploading VOCOS model to S3..."
	python upload_model_to_s3.py

test_download:
	@echo "Testing download script..."
	python test_download.py

init: 
	@echo "Note: Model file will be downloaded from S3 during Docker build"
	@echo "Run 'make upload_model_to_s3' first to upload the model file to S3"

install:
	pip install -e ../aws -e ../types -e .

run:
	@chmod +x ./run.sh
	@./run.sh

test:
	cd tta_speech && python rp_handler.py
