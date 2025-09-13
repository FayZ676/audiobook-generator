FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget && rm -rf /var/lib/apt/lists/*

COPY types/ /app/types
COPY aws/ /app/aws
COPY f5/ /app/f5
COPY speech/ /app/speech
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/f5
RUN pip install /app/speech

RUN mkdir -p /app/f5/tta_f5/checkpoints
RUN mkdir -p /app/f5/tta_f5/vocos
RUN wget -O /app/f5/tta_f5/checkpoints/model_1250000.safetensors "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_v1_Base/model_1250000.safetensors"
RUN wget -O /app/f5/tta_f5/vocos/pytorch_model.bin "https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin"

CMD ["python", "-u", "speech/tta_speech/rp_handler.py"]