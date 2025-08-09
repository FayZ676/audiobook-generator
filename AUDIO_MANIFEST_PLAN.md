# Per-Segment Audio + Manifest: Implementation Plan

## Goals

- Generate and store audio per script segment with stable IDs.
- Expose a manifest with keys for final narration and each segment.
- Serve presigned URLs via service endpoints for: all audio, final narration, and a single segment.
- Keep request/response contracts simple and self-descriptive.

## Storage Layout (S3)

- Final narration: {user_id}/{chapter_name}/audio/narration.mp3
- Segments: {user_id}/{chapter_name}/audio/segments/{segment_id}.mp3
- Manifest: {user_id}/{chapter_name}/audio/manifest.json

Notes:

- segment_id must be stable and unique in the script store.
- Order will be preserved in manifest via `index`.

## Data Contracts

### types/tta_types/types.py

- Update SpeechRequestSegment

  - Before: { text: str, voice_name: str }
  - After: { id: str, text: str, voice_name: str }

- Optionally add types for manifest interchange (kept internal to service for now for simplicity). If shared types are desired later, define:
  - SegmentAudio: { id: str, index: int, key: str }
  - AudioManifest: { narration: { key: str }, segments: SegmentAudio[] }

### Script JSON

- Each stored script segment must include `id` (string), `text`, and `speaker_alias`.
- Update adapter in `types/tta_types/script.py` to emit SpeechRequestSegment with `id`.

### Speech Webhook (no breaking change required)

- Keep Response as-is for now: { filename, request_word_count } where filename points to final narration key (now /audio/narration.mp3).
- Optionally add `manifest_key` later if we want the service to avoid recomputing path.

## Speech Worker Changes (speech/tta_speech/rp_handler.py)

1. Consume `SpeechRequestSegment` with `id`.
2. Synthesize each segment sequentially.
3. Upload per-segment mp3 to `{user_id}/{chapter_name}/audio/segments/{segment_id}.mp3`.
4. Build in-memory manifest:
   - narration.key = `{user_id}/{chapter_name}/audio/narration.mp3`
   - segments[] = { id, index, key }
5. Upload combined final mp3 to `audio/narration.mp3`.
6. Upload `audio/manifest.json`.
7. Send single completion webhook (unchanged fields), with `filename` set to final narration key.

Edge handling:

- If a segment synthesis fails, fail the job; do not upload partial manifest. (Future improvement: partial results with status.)

## Service API Changes (service/tta_service/routers)

1. Update existing final narration endpoint

- GET /narration/{user_id}/{chapter_name}
  - Now points to `{user_id}/{chapter_name}/audio/narration.mp3`.
  - Returns presigned URL string or 404-like None when missing.

2. New: Get everything (manifest with presigned URLs)

- GET /narration/{user_id}/{chapter_name}/audio
  - Read `{user_id}/{chapter_name}/audio/manifest.json` from S3.
  - For each key in manifest, attach `url = presigned_url(bucket, key)`.
  - Response shape:
    {
    narration: { key: string, url: string },
    segments: Array<{ id: string, index: number, key: string, url: string }>
    }
  - TTL = 1 hour.
  - 404/None if manifest not found.

3. New: Get single segment audio

- GET /narration/{user_id}/{chapter_name}/segments/{segment_id}
  - Load manifest; find segment by `id`.
  - Return { key, url } or 404 if missing.

## Adapter Changes (types/tta_types/script.py)

- Update `ScriptData.to_speech_segments()` to map:
  - id = segment.get("id")
  - text = segment.get("text")
  - voice_name mapped from speaker_alias → voice.name (unchanged logic)

## Client Changes (client)

- Fetch manifest via GET /narration/{user_id}/{chapter_name}/audio.
- Match UI script segments to manifest by segment `id`.
- Use the existing `AudioPlayer` component to play individual segment audio using the presigned URL for each segment.
- Final narration player fetch remains via GET /narration/{user_id}/{chapter_name}.

## Validation

- In speech, service, script: `make lint`.
- In client: `npm run build`.

## Rollout / Migration

- No backward compatibility for old paths; re-run narration to generate new `audio/` layout.
- Existing chapters with old `segments/` path will not be served by new endpoints.

## Tasks

1. Update types:
   - Add `id: str` to SpeechRequestSegment.
2. Update script adapter to emit `id`.
3. Update speech worker:
   - Save per-segment audio at `audio/segments/{id}.mp3`.
   - Produce and upload `audio/manifest.json`.
   - Move final to `audio/narration.mp3`.
4. Update service endpoints:
   - Adjust final narration pathing.
   - Add `GET /narration/{user_id}/{chapter_name}/audio`.
   - Add `GET /narration/{user_id}/{chapter_name}/segments/{segment_id}`.
5. Client wiring to use manifest for per-segment audio and integrate `AudioPlayer` for playback.
6. Verify with lint and build commands.

## Open Questions / Future Enhancements

- Include `duration_ms` per segment in manifest for better UI? (Optional)
- Add retries/partial success semantics for long chapters.
- Include `version` and `generated_at` in manifest for cache control and audit.
- Consider background normalization post-process (currently disabled).
- Integrate webhook for real time UI updates as speech segments are generated and saved.
- Don't fail job if individual segment fails.
