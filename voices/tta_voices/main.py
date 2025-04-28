from fastapi import FastAPI


app = FastAPI()


@app.get("/voices")
def get_voices():
    """
    Get a list of available voices.
    """
    return {"voices": ["voice1", "voice2", "voice3"]}


@app.get("/voices/{voice_id}")
def get_voice(voice_id: str):
    """
    Get details of a specific voice.
    """
    return {"voice_id": voice_id, "details": "Details about the voice"}


@app.post("/voices")
def add_voice(voice: dict):
    """
    Add a new voice.
    """
    return {"message": "Voice added", "voice": voice}


@app.put("/voices/{voice_id}")
def update_voice(voice_id: str, voice: dict):
    """
    Update an existing voice.
    """
    return {"message": "Voice updated", "voice_id": voice_id, "voice": voice}


@app.delete("/voices/{voice_id}")
def delete_voice(voice_id: str):
    """
    Delete a specific voice.
    """
    return {"message": "Voice deleted", "voice_id": voice_id}
