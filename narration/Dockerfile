# Narration's RunPod worker, on an NVIDIA GPU. Build from the repo root:
#   docker build --platform linux/amd64 -f narration/Dockerfile -t tta-narration .
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg sox && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY script/pyproject.toml script/pyproject.toml
COPY script/tta_script script/tta_script
COPY narration/pyproject.toml narration/pyproject.toml
COPY narration/tta_narration narration/tta_narration
RUN pip install --no-cache-dir ./script "./narration[cuda]"

# The weights go in the image so a cold worker doesn't download 4 GB first.
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-Base')"

CMD ["python", "-u", "-m", "tta_narration.worker"]
