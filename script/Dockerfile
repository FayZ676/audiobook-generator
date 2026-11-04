FROM python:3.12-slim

WORKDIR /app

COPY types/ /app/types
COPY aws/ /app/aws
COPY script/ /app/script
RUN pip install /app/types
RUN pip install /app/aws
RUN pip install /app/script

CMD ["python", "-u", "script/tta_script/rp_handler.py"]
