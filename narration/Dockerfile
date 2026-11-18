# Narration's RunPod worker, on an NVIDIA GPU. Build from the repo root:
#   docker build --platform linux/amd64 -f narration/Dockerfile -t tta-narration .
#
# Layers go from what changes least to what changes most: system packages,
# Python dependencies (read from both pyproject.toml files), the model, then
# our code. A code change rebuilds and ships only the last, few-KB layers;
# CI and RunPod reuse the rest.
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg sox && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY script/pyproject.toml script/pyproject.toml
COPY narration/pyproject.toml narration/pyproject.toml
RUN python -c "\
import tomllib; \
script = tomllib.load(open('script/pyproject.toml', 'rb'))['project']; \
narration = tomllib.load(open('narration/pyproject.toml', 'rb'))['project']; \
ours = [d for d in narration['dependencies'] if not d.startswith('tta_script')]; \
print('\n'.join(dict.fromkeys(script['dependencies'] + ours + narration['optional-dependencies']['cuda'])))" > requirements.txt \
 && pip install --no-cache-dir -r requirements.txt

# The weights go in the image so a cold worker doesn't download 4 GB first.
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-Base')"

COPY script/tta_script tta_script
COPY narration/tta_narration tta_narration
ENV PYTHONPATH=/app

CMD ["python", "-u", "-m", "tta_narration.worker"]
