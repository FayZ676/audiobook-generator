from fastapi import FastAPI, UploadFile, File, HTTPException
from tta.character import identify_characters
from tta.script import convert_text_to_script
import logging

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

@app.post("/book/preprocess")
async def preprocess(file: UploadFile = File(...)):
    try:
        # Read content from the uploaded file
        content = await file.read()
        text = content.decode('utf-8')  # You can use errors='replace' if UTF-8 fails
        logger.debug(f"Decoded text length: {len(text)}")

        # Process the text
        script = convert_text_to_script(text=text)
        logger.debug("Script generated successfully")

        characters = identify_characters(text=text)
        logger.debug(f"Characters identified: {characters}")

        return {"script": script, "characters": characters}
    except UnicodeDecodeError:
        logger.error(f"File content could not be decoded")
        raise HTTPException(status_code=400, detail="Failed to decode file content as UTF-8.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")
