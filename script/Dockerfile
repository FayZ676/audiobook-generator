FROM python:3.12-slim

WORKDIR /app

RUN pip install spacy==3.8.4 && python -m spacy download en_core_web_trf

COPY types/ /app/types
COPY aws/ /app/aws
COPY script/ /app/script
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/script

CMD ["uvicorn", "script.main:app"]
