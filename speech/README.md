# Speech Generation Service

### Setup

1. Download VOCOS `config.yaml` and `pytorch_model.bin` model file from https://huggingface.co/charactr/vocos-mel-24khz/tree/main and store in `tta_speech/vocos` directory.

2. Set environment variables for `VOICES_AUDIOS_BUCKET` and `PROJECTS_BUCKET`. Refer to `cloudformation.yaml` file in root for details on these buckets.

3. Ensure AWS credentials are configured as environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`) for S3 access during container build and runtime.
