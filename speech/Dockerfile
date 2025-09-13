FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget && rm -rf /var/lib/apt/lists/*

COPY f5/requirements.txt /app/f5/requirements.txt
COPY types/requirements.txt /app/types/requirements.txt  
COPY aws/requirements.txt /app/aws/requirements.txt
COPY speech/requirements.txt /app/speech/requirements.txt

RUN pip install -r /app/f5/requirements.txt
RUN pip install -r /app/types/requirements.txt
RUN pip install -r /app/aws/requirements.txt
RUN pip install -r /app/speech/requirements.txt

RUN mkdir -p /usr/local/lib/python3.12/site-packages/tta_f5/checkpoints /usr/local/lib/python3.12/site-packages/tta_f5/vocos && \
    wget -O /usr/local/lib/python3.12/site-packages/tta_f5/checkpoints/model_1250000.safetensors "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/model_1250000.safetensors" && \
    wget -O /usr/local/lib/python3.12/site-packages/tta_f5/vocos/pytorch_model.bin "https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin" && \
    wget -O /usr/local/lib/python3.12/site-packages/tta_f5/vocos/config.yaml "https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/config.yaml"

COPY f5/ /app/f5
RUN pip install /app/f5

COPY types/ /app/types
RUN pip install /app/types

COPY aws/ /app/aws
RUN pip install /app/aws

COPY speech/ /app/speech
RUN pip install /app/speech

CMD ["python", "-u", "speech/tta_speech/rp_handler.py"]