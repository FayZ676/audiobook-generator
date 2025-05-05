FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY voices/ /app/voices
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/voices

CMD ["uvicorn", "tta_voices.main:app"]
