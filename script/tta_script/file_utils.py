import os
import io
import json
from typing import BinaryIO

from tta_types.script import Script
from tta_aws.s3 import S3Client


s3_client = S3Client()


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")


def upload_script_result(user_id: str, script_data: Script, chapter_name: str):
    script_file = _to_json_fileobject("script.json", script_data)
    project_script_path = f"{user_id}/{chapter_name}/script.json"
    s3_client.upload_fileobj(f"{PROJECTS_BUCKET}", project_script_path, script_file)
    return str(script_file.name)


def _to_json_fileobject(filename: str, script_data: Script) -> BinaryIO:
    json_data = script_data.model_dump()
    json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}"
    return file_obj
