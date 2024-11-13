from fastapi import FastAPI, UploadFile, File

from tta.character import identify_characters
from tta.script import convert_text_to_script

app = FastAPI()


@app.post("/book/preprocess")
async def preprocess(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    characters = identify_characters(text=text)
    script = convert_text_to_script(text=text, characters=characters)
    return {"script": script, "characters": characters}
