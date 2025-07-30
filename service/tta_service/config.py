import os
import pusher
from tta_aws.s3 import S3Client


VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")
SPEECH_RESULTS_BUCKET = os.environ.get("SPEECH_RESULTS_BUCKET", "")
JOB_STATUS_BUCKET = os.environ.get("JOB_STATUS_BUCKET", "")
LOGS_BUCKET = os.environ.get("LOGS_BUCKET", "")
PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")

SERVICE_API_URL = os.environ.get("SERVICE_API_URL", "")

SPEECH_SERVICE_API_KEY = os.environ.get("SPEECH_SERVICE_API_KEY", "")
SPEECH_API_URL = os.environ.get("SPEECH_API_URL", "")

SCRIPT_SERVICE_API_KEY = os.environ.get("SCRIPT_SERVICE_API_KEY", "")
SCRIPT_API_URL = os.environ.get("SCRIPT_API_URL", "")

PUSHER_APP_ID = os.environ.get("PUSHER_APP_ID", "")
PUSHER_KEY = os.environ.get("PUSHER_KEY", "")
PUSHER_SECRET = os.environ.get("PUSHER_SECRET", "")
PUSHER_CLUSTER = os.environ.get("PUSHER_CLUSTER", "")

# NOTE: Refer to https://github.com/FayZ676/audiobook-generator/issues/163 for calculations.
SCRIPT_COST_PER_WORD = 0.00009
SPEECH_COST_PER_WORD = 0.00042

USAGE_LIMIT = 20.0

s3_client = S3Client()

pusher_client = pusher.Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
    cluster=PUSHER_CLUSTER,
    ssl=True,
)
