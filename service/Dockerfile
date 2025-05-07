FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY service/ /app/service
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/service

CMD ["uvicorn", "service.tta_speech.main:app"]
