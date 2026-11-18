# The script step's RunPod worker. Runs on CPU: its time goes to model API calls.
# Set ANTHROPIC_API_KEY and OPENAI_API_KEY on the RunPod endpoint.
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY tta_script ./tta_script
RUN pip install --no-cache-dir .

CMD ["python", "-u", "-m", "tta_script.worker"]
