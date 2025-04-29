from fastapi import FastAPI

from tta_types.types import Voice


app = FastAPI()


@app.get("/voices")
def get_voices():
    # TODO: Get all voices from dynamo db.
    return [Voice("Bob", "middle-aged", "male", "foo", "bar")]


@app.get("/voices/{voice_id}")
def get_voice(voice_id: str):
    # TODO: Get voice from dynamo db.
    return Voice("Bob", "middle-aged", "male", "foo", "bar")


@app.post("/voices")
def add_voice(name: str, age: str, gender: str, audio: bytes, transcript: str):
    # TODO: Upload audio to s3.
    # TODO: Create voice type.
    # TODO: Add voice to dynamo db.
    return
