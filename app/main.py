from fastapi import FastAPI
from app.config.database import engine, Base

# Import ALL models here so Base knows about them before create_all
from app.models import user, note  # ← this line is critical

from app.routers import auth, notes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartNotes API 🌸")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0"}