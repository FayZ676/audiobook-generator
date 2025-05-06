# Speech Generation Service

### Setup

1. Download VOCOS `config.yaml` and `pytorch_model.bin` model file from https://huggingface.co/charactr/vocos-mel-24khz/tree/main and store in `tta_speech/vocos` directory.
2. Set environment variables for `SPEECH_RESULTS_BUCKET` and `VOICES_AUDIOS_BUCKET`. Refer to `cloudformation.yaml` file in root for details on these buckets.
