import logging

from tta_script.dialogue.extract import get_script
from tta_script.character.extract import get_new_characters
from tta_script.text_utils import normalize_quotes
from tta_script.speakers import get_speakers

from tta_types.types import WebhookResponse, WebhookRequest, Response, ScriptRequest
from tta_data.client import TTADataClient

import requests
import runpod


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    request_data = ScriptRequest.model_validate(request.data)

    text = normalize_quotes(request_data.text_content)
    previous_speakers = set(request_data.previous_speakers)

    try:
        voices = request_data.voices
        if len(voices) == 0:
            raise ValueError("No voices available")

        previous_characters = {s.character for s in previous_speakers}
        new_characters = get_new_characters(text, previous_characters)
        speakers = get_speakers(
            characters=previous_characters | new_characters,
            voices=voices,
            narrator_voice=voices[0],
            previous_speakers=previous_speakers,
        )
        script_filename = TTADataClient().upload_script(
            user_id=request.user_id,
            script=get_script(text, speakers),
            chapter_name=request_data.chapter_name,
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
