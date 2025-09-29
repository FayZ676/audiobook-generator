import logging

from tta_script.dialogue.extract import (
    get_dialogues,
    dialogue_to_script,
    get_text_segments,
)
from tta_script.character.extract import get_characters
from tta_script.text_utils import normalize_quotes
from tta_script.speakers import get_speakers
from tta_script.file_utils import upload_script_result

from tta_types.types import WebhookResponse, WebhookRequest, Response, ScriptRequest

import requests
import runpod


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    request_data = ScriptRequest.model_validate(request.data)

    try:

        if len(request_data.voices) == 0:
            raise ValueError("No voices available")

        text = normalize_quotes(request_data.text_content)
        previous_speakers = set(request_data.previous_speakers)
        previous_characters = {s.character for s in previous_speakers}
        new_characters = get_characters(text, previous_characters)
        speakers = get_speakers(
            characters=previous_characters | new_characters,
            voices=request_data.voices,
            narrator_voice=request_data.voices[
                0
            ],  # TODO: We shouldn't need this to be a distinct param. We should use whatever is abailable in voices.
            previous_speakers=previous_speakers,
        )
        text_segments = get_text_segments(text=text)
        dialogue = get_dialogues(text_segments=text_segments, speakers=speakers)
        script = dialogue_to_script(dialogue=dialogue)
        script_filename = upload_script_result(
            request.user_id, script, request_data.chapter_name
        )
        status = "complete"
        message = ""
        data = Response(filename=script_filename, request_word_count=len(text.split()))
    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("Exception occurred during script processing: %s", str(e))
        status = "failed"
        message = str(e)
        data = Response(filename="", request_word_count=0)

    requests.post(
        request.callback,
        json=WebhookResponse(
            user_id=request.user_id,
            event=request.event,
            status=status,
            message=message,
            data=data,
        ).model_dump(),
        timeout=120,
    )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
