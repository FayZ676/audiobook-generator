import os

import requests
import runpod

from tta_speech.voice_manager import VoiceManager
from tta_speech.speech_synthesizer import SpeechSynthesizer
from tta_speech.storage_manager import StorageManager
from tta_speech.request_processor import SpeechRequestProcessor
from tta_speech.text_utils import compute_word_count

from tta_types.types import (
    WebhookRequest,
    SpeechRequest,
    WebhookResponse,
    Response,
    JobStatus,
)
from tta_aws.s3 import S3Client


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")
VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")


class SpeechSynthesisHandler:
    """Main handler for speech synthesis webhook requests."""

    def __init__(self):
        self.s3_client = S3Client()
        self.voice_manager = VoiceManager(self.s3_client, VOICES_BUCKET)
        self.speech_synthesizer = SpeechSynthesizer(self.voice_manager)
        self.storage_manager = StorageManager(self.s3_client, PROJECTS_BUCKET)
        self.request_processor = SpeechRequestProcessor(
            voice_manager=self.voice_manager,
            speech_synthesizer=self.speech_synthesizer,
            storage_manager=self.storage_manager,
        )

    def handle_request(self, event: dict) -> None:
        """Handle incoming webhook request."""
        request = WebhookRequest.model_validate(event["input"])
        request_data = SpeechRequest.model_validate(request.data)
        total_word_count = compute_word_count(request_data.text)
        data = Response(filename="", request_word_count=total_word_count)
        status: JobStatus = "failed"

        try:
            data = self.request_processor.process_request(request_data, request.user_id)
            status = "complete"
        except (ValueError, FileNotFoundError, requests.RequestException) as e:
            # TODO: Use logging here instead of printing.
            print(f"Error processing request: {e}")
        finally:
            self._send_webhook_response(request, status, data)

    def _send_webhook_response(
        self, request: WebhookRequest, status: JobStatus, data: Response
    ) -> None:
        """Send webhook response to callback URL."""
        try:
            response = WebhookResponse(
                user_id=request.user_id,
                event=request.event,
                status=status,
                message="",
                data=data,
            )
            requests.post(
                url=request.callback,
                json=response.model_dump(),
                timeout=120,
            )
        except requests.RequestException as e:
            print(f"Error sending webhook response: {e}")


def handler(event: dict) -> None:
    """RunPod serverless handler function."""
    SpeechSynthesisHandler().handle_request(event)


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
