FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY speech/ /app/speech
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/speech

CMD ["uvicorn", "tta_speech.main:app"]
