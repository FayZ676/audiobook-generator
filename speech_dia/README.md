# Dia TTS POC

This directory contains a Proof of Concept (POC) implementation using the [Dia TTS model](https://github.com/nari-labs/dia) from nari-labs as a potential replacement for the current F5-TTS speech generation system.

## Overview

Dia is a 1.6B parameter text-to-speech model that directly generates realistic dialogue from transcripts. It uses speaker tags `[S1]` and `[S2]` for dialogue generation and can produce nonverbal communications like laughter, coughing, etc.

## Files

- `dia_tts.py` - Main implementation with interface matching the existing TTS system
- `test_dia_poc.py` - Simple test to verify the POC works
- `requirements.txt` - Dependencies needed for Dia TTS
- `README.md` - This file

## Interface

The POC provides two main functions:

### `generate_speech(request: SpeechRequest) -> bytes`
Main interface function that takes a `SpeechRequest` and returns MP3 audio data.

### `infer_dia(request: SpeechRequest) -> tuple[bytes, Optional[int]]`
Compatibility function that matches the existing TTS interface signature.

## Key Differences from F5-TTS

1. **Speaker Format**: Dia uses `[S1]` and `[S2]` speaker tags instead of voice names
2. **Model Size**: Dia is 1.6B parameters vs F5-TTS 
3. **Voice Cloning**: Dia supports voice cloning through audio prompts
4. **Dialogue Focus**: Dia is specifically designed for dialogue generation
5. **Nonverbals**: Built-in support for `(laughs)`, `(coughs)`, etc.

## Voice Mapping

Since Dia uses only `[S1]` and `[S2]` speaker tags, the POC maps multiple voice names to alternating speakers:
- First unique voice name → `[S1]` 
- Second unique voice name → `[S2]`
- Additional voices cycle between `[S1]` and `[S2]`

## Installation & Setup

1. Install Dia TTS:
```bash
pip install git+https://github.com/nari-labs/dia.git
```

2. Set HuggingFace token (required for model download):
```bash
export HF_TOKEN="your_hf_token_here"
```

3. Run the test:
```bash
cd speech_dia
python test_dia_poc.py
```

## Hardware Requirements

- GPU recommended (RTX 4090 achieves ~2x realtime with float16)
- ~10GB VRAM for float16 precision
- CPU support may be added in future Dia releases

## Evaluation vs F5-TTS

### Advantages of Dia:
- Purpose-built for dialogue generation
- Supports nonverbal expressions natively
- More natural conversational flow
- Active development and community

### Considerations:
- Limited to 2 speakers (S1/S2) without voice cloning
- Larger model size and memory requirements  
- Different voice mapping approach needed
- Relatively new compared to F5-TTS

## Next Steps

If this POC proves successful, the next steps would be:
1. Performance benchmarking vs F5-TTS
2. Quality comparison with human evaluation
3. Integration testing with the full audiobook pipeline
4. Voice cloning implementation for multi-character support
5. Production deployment considerations (GPU infrastructure, model caching, etc.)