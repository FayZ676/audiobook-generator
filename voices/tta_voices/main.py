import json

from fastapi import FastAPI, UploadFile

from tta_types.types import Voice

from tta_voices.aws import S3Client


app = FastAPI()


s3_client = S3Client()


@app.get("/voices")
def get_voices():
    voices_metadata = s3_client.get_files("voices-metadata-bucket")
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content_bytes = s3_client.get_file(
            "voices-metadata-bucket", str(voice_metadata_key)
        )
        voice_data = json.loads(file_content_bytes.decode("utf-8"))
        voices.append(Voice(**voice_data))
    return voices


@app.get("/voices/{voice_id}")
def get_voice(voice_name: str):
    file_content_bytes = s3_client.get_file(
        "voices-metadata-bucket", f"{voice_name}.json"
    )
    voice = json.loads(file_content_bytes.decode("utf-8"))
    return Voice(**voice)


@app.post("/voices")
def add_voice(
    name: str, age: str, gender: str, audio_transcript: str, audio_file: UploadFile
):
    if not audio_file.filename:
        raise ValueError("Audio file with name is required")

    path = s3_client.upload_fileobj(
        "voices-audios-bucket", audio_file.filename, audio_file.file
    )
    s3_client.upload_fileobj(
        "voices-metadata-bucket",
        f"{name}.json",
        Voice(
            name=name,
            age=age,
            gender=gender,
            audio_path=path,
            audio_transcript=audio_transcript,
        ).to_json_fileobject(),
    )
    return
