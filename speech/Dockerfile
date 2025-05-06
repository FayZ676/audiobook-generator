FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget

RUN wget -P tta_speech/vocos https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin

COPY types/ /app/types
COPY aws/ /app/aws
COPY speech/ /app/speech
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/speech

CMD ["python", "-u", "speech/tta_speech/rp_handler.py"]
