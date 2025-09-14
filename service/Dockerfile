FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY types/requirements.txt /app/types/requirements.txt
COPY aws/requirements.txt /app/aws/requirements.txt
RUN pip install -r /app/types/requirements.txt
RUN pip install -r /app/aws/requirements.txt

COPY types/ /app/types
COPY aws/ /app/aws
COPY service/ /app/service
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/service

# 10000 is default port used by Render
CMD ["uvicorn", "service.tta_service.main:app", "--host", "0.0.0.0", "--port", "10000"]
