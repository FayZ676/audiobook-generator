from fastapi import FastAPI

from tta_types.types import Voice

from tta_voices.aws import DynamoDBClient, S3Client


app = FastAPI()


dynamo_db_client = DynamoDBClient()
s3_client = S3Client()


@app.get("/voices")
def get_voices():
    voices = dynamo_db_client.get_items("VoicesTable")
    return [Voice(**voice) for voice in voices]


@app.get("/voices/{voice_id}")
def get_voice(voice_id: str):
    voice = dynamo_db_client.get_item("VoicesTable", {"voice_id": voice_id})
    return Voice(**voice)


@app.post("/voices")
def add_voice(name: str, age: str, gender: str, audio: bytes, transcript: str):
    samples = s3_client.get_files("voices-audios-bucket")
    print(samples)
    return
