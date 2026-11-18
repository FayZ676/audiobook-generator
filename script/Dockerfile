# The script step's RunPod worker. Runs on CPU: its time goes to model API calls.
# Set ANTHROPIC_API_KEY and OPENAI_API_KEY on the RunPod endpoint.
FROM python:3.12-slim

WORKDIR /app

# Dependencies first, read from pyproject.toml, and the code last, so a code
# change rebuilds and ships only the final, few-KB layer.
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']))" > requirements.txt \
 && pip install --no-cache-dir -r requirements.txt

COPY tta_script ./tta_script
ENV PYTHONPATH=/app

CMD ["python", "-u", "-m", "tta_script.worker"]
