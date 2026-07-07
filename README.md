# SmartNotes API 🌸

A production-grade REST API for personal note management, built with FastAPI, PostgreSQL, and JWT authentication. Fully containerized with Docker.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose) |
| Password Hashing | passlib + bcrypt |
| Containerization | Docker + Docker Compose |
| Settings Management | pydantic-settings |

---

## Features

- **JWT Authentication** — register, login, token-based access
- **User-owned notes** — users can only access their own data
- **Full CRUD** — create, read, update, delete notes
- **Tag filtering** — filter notes by tag
- **Dockerized** — runs with a single command, no local setup required
- **Auto table creation** — SQLAlchemy creates all tables on startup

---

## Project Structure

```
notes-api/
├── app/
│   ├── config/
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   └── settings.py       # Pydantic settings + .env loading
│   ├── models/
│   │   ├── user.py           # User table
│   │   └── note.py           # Note table (with owner FK)
│   ├── routers/
│   │   ├── auth.py           # /auth/register, /auth/login
│   │   └── notes.py          # /notes CRUD routes
│   ├── schemas/
│   │   ├── user.py           # UserCreate, UserResponse, Token
│   │   └── note.py           # NoteCreate, NoteUpdate, NoteResponse
│   ├── services/
│   │   └── auth.py           # JWT logic, password hashing
│   ├── dependencies.py       # get_current_user dependency
│   └── main.py               # App entrypoint
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Run with Docker

```bash
git clone https://github.com/Nour-Faker/notes-api.git
cd notes-api
docker compose up --build
```

API is live at `http://localhost:8000`

Interactive docs at `http://localhost:8000/docs`

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/smartnotes
SECRET_KEY=your-secret-key-change-in-production
```

---

## API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create a new user |
| POST | `/api/v1/auth/login` | Login and receive JWT token |

### Notes (requires Bearer token)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/notes/` | Create a note |
| GET | `/api/v1/notes/` | Get all your notes (optional `?tag=`) |
| GET | `/api/v1/notes/{id}` | Get a single note |
| PATCH | `/api/v1/notes/{id}` | Update a note |
| DELETE | `/api/v1/notes/{id}` | Delete a note |

### Example — Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "nour@test.com", "username": "nour", "password": "password123"}'
```

### Example — Create a Note

```bash
curl -X POST http://localhost:8000/api/v1/notes/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first note", "content": "Hello world", "tag": "personal"}'
```

---

## Architecture Decisions

**Why JWT over sessions?** JWTs are stateless — the server doesn't store session data. This makes the API horizontally scalable: any server instance can verify any token without shared state.

**Why separate `dependencies.py`?** Mixing FastAPI dependencies into service files creates circular imports. Services stay pure Python; the dependency injection layer lives separately.

**Why `bcrypt==4.0.1` pinned?** bcrypt 4.1+ removed the `__about__` attribute that passlib reads for version detection. Pinning avoids a runtime crash on password hashing.

---

## Roadmap

- [ ] Alembic database migrations
- [ ] Pagination on GET /notes
- [ ] Full-text search
- [ ] pytest test suite
- [ ] CI/CD with GitHub Actions

---

## Author

**Nour** — Computer Engineering student at ENICarthage, Tunisia  
Building toward AI engineering.

---

## License

MIT
