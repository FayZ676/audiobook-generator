from fastapi import FastAPI, UploadFile

from tta_types.types import Voice

from tta_voices.aws import S3Client


app = FastAPI()


s3_client = S3Client()


# @app.get("/voices")
# def get_voices():
#     voices = s3_client.get_items("VoicesTable")
#     return [Voice(**voice) for voice in voices]


# @app.get("/voices/{voice_id}")
# def get_voice(voice_id: str):
#     voice = s3_client.get_item("VoicesTable", {"voice_id": voice_id})
#     return Voice(**voice)


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
