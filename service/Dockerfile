FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY service/ /app/service
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/service

# 10000 is default port used by Render
CMD ["uvicorn", "service.tta_service.main:app", "--host", "0.0.0.0", "--port", "10000"]
