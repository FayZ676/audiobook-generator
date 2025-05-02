FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install wget ffmpeg

COPY types/ /app/types
COPY aws/ /app/aws
COPY script/ /app/script
RUN pip install -e /app/types
RUN pip install -e /app/aws
RUN pip install /app/script
RUN python -m spacy download en_core_web_trf

CMD ["python", "tta_script/main.py"]
