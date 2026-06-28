# Notes API

A RESTful CRUD API built with FastAPI and SQLite.
Built as part of my backend engineering learning path toward AI engineering.

## Tech Stack

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Run Locally

```bash
git clone https://github.com/Nour-Faker/notes-api.git
cd notes-api
python -m venv venv
source venv/Scripts/activate
pip install fastapi uvicorn sqlalchemy
uvicorn main:app --reload
```

Open http://localhost:8000/docs for the interactive API explorer.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Server health check |
| POST | /notes | Create a new note |
| GET | /notes | Get all notes |
| GET | /notes/{id} | Get a single note |
| PUT | /notes/{id} | Update a note |
| DELETE | /notes/{id} | Delete a note |
| GET | /notes/search?tag= | Search notes by tag |

## What I Learned

- FastAPI route design and Pydantic validation
- SQLAlchemy ORM with SQLite persistence
- Dependency injection with `Depends()`
- Proper HTTP status codes (201, 204, 404)
- Production-style project structure