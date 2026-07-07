from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NoteCreate(BaseModel):
    title: str
    content: str
    tag: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tag: Optional[str]
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True