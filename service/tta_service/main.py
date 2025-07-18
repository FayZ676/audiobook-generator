from fastapi import FastAPI

from tta_service.routers import script, narration, voices, job, webhook


app = FastAPI()

app.include_router(script.router)
app.include_router(narration.router)
app.include_router(voices.router)
app.include_router(job.router)
app.include_router(webhook.router)
