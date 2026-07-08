from fastapi import FastAPI
from app.config.database import engine, Base
from app.models import user, note
from app.routers import auth, notes

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

app = FastAPI(title="SmartNotes API 🌸")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0"}