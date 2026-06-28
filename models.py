from sqlalchemy import Column, Integer, String
from database import Base

class Note(Base):
    __tablename__ = "notes"

    id      = Column(Integer, primary_key=True, index=True)
    title   = Column(String, nullable=False)
    content = Column(String, nullable=False)
    tag     = Column(String, nullable=True)