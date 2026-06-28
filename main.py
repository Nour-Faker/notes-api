from fastapi import FastAPI, HTTPException, Depends,UploadFile,File
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
from database import engine, SessionLocal

# creates the tables in notes.db if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")

# --- Dependency: gives each request its own DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}

ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_SIZE_BYTES = 1 * 1024 * 1024  # 1MB

@app.post("/upload", status_code=201)
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files allowed")

    content = await file.read()

    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Max 1MB")

    if ext == ".txt":                                        
        preview = content.decode("utf-8", errors="ignore")[:200]
    else:
        preview = "PDF preview not supported yet"

    return {                                                 
        "filename": file.filename,
        "size_bytes": len(content),
        "content_type": file.content_type,
        "preview": preview
    }

@app.post("/notes", response_model=schemas.NoteResponse, status_code=201)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        tag=note.tag
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)  # reload from DB to get the generated id
    return db_note

@app.get("/notes", response_model=List[schemas.NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).all()

@app.get("/notes/search", response_model=List[schemas.NoteResponse])
def search_notes(tag: str, db: Session = Depends(get_db)):
    notes = db.query(models.Note).filter(models.Note.tag == tag).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found for this tag")
    return notes
    

@app.get("/notes/{note_id}", response_model=schemas.NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None

@app.put("/notes/{note_id}",response_model=schemas.NoteResponse)
def set_note(note_id:int,note_update:schemas.NoteCreate,db:Session=Depends(get_db)):
    note=db.query(models.Note).filter(models.Note.id==note_id).first()

    if note is None:
        raise HTTPException(status_code=404,detail="Note not found")
    
    note.title=note_update.title
    note.content=note_update.content
    note.tag = note_update.tag
    db.commit()
    db.refresh(note)
    return note




