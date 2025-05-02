FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY script/ /app/script
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/script
RUN python -m spacy download en_core_web_trf

CMD ["uvicorn", "tta_script.main:app"]
