from fastapi import FastAPI, Response, UploadFile, File

from tta_script.narration import get_narration_from_text

app = FastAPI()


@app.post("/narration")
async def preprocess(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    narration = get_narration_from_text(text=text)
    return Response(
        content=narration,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={file.filename}.mp3"},
    )
