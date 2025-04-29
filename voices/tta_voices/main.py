from fastapi import FastAPI

from tta_types.types import Voice


app = FastAPI()


@app.get("/voices")
def get_voices():
    return [Voice("Bob", "middle-aged", "male", "foo", "bar")]


@app.get("/voices/{voice_id}")
def get_voice(voice_id: str):
    # TODO: Find voice
    return Voice("Bob", "middle-aged", "male", "foo", "bar")


@app.post("/voices")
def add_voice(voice: Voice):
    # TODO: Check that voice exists first.
    return
