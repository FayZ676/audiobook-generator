from fastapi import FastAPI

from tta_service.routers import script, narration, voices, job, events


app = FastAPI()

app.include_router(script.router)
app.include_router(narration.router)
app.include_router(voices.router)
app.include_router(job.router)
app.include_router(events.router)
