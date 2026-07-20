![CI](https://github.com/Nour-Faker/notes-api/actions/workflows/ci.yml/badge.svg)
# SmartNotes API 🌸

A production-grade REST API for personal note management — built from scratch with FastAPI, PostgreSQL, JWT authentication, Docker, Alembic migrations, and a full pytest test suite.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [How the Code Flows](#how-the-code-flows)
- [Database Design](#database-design)
- [Authentication System](#authentication-system)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Design Decisions](#design-decisions)
- [Roadmap](#roadmap)

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Framework | FastAPI | Async-ready, auto-docs, Pydantic validation |
| Database | PostgreSQL 16 | Production-standard relational DB |
| ORM | SQLAlchemy 2.0 | Python-native DB queries, no raw SQL |
| Migrations | Alembic | Safe schema evolution without data loss |
| Auth | JWT (python-jose) | Stateless, scalable authentication |
| Password Hashing | passlib + bcrypt 4.0.1 | Industry-standard one-way hashing |
| Containerization | Docker + Docker Compose | Reproducible environment anywhere |
| Settings | pydantic-settings | Type-safe config with .env support |
| Testing | pytest + httpx | Isolated, fast, real HTTP request testing |

---

## Project Structure

```
notes-api/
│
├── app/                          # All application code lives here
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLAlchemy engine, session, Base
│   │   └── settings.py           # Pydantic settings loaded from .env
│   │
│   ├── models/                   # SQLAlchemy table definitions
│   │   ├── __init__.py
│   │   ├── user.py               # users table
│   │   └── note.py               # notes table (with owner FK)
│   │
│   ├── schemas/                  # Pydantic request/response shapes
│   │   ├── __init__.py
│   │   ├── user.py               # UserCreate, UserResponse, Token
│   │   └── note.py               # NoteCreate, NoteUpdate, NoteResponse
│   │
│   ├── routers/                  # Route handlers (controllers)
│   │   ├── __init__.py
│   │   ├── auth.py               # POST /auth/register, POST /auth/login
│   │   └── notes.py              # Full CRUD on /notes
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py               # Pure JWT + bcrypt logic (no FastAPI)
│   │
│   ├── dependencies.py           # get_current_user FastAPI dependency
│   └── main.py                   # App entrypoint, router registration
│
├── migrations/                   # Alembic migration files
│   ├── versions/
│   │   ├── 21f8f5ea5d0e_create_users_and_notes_tables.py
│   │   └── 538214d259fd_add_is_pinned_to_notes.py
│   ├── env.py                    # Alembic config (connects to your models)
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures (client, DB, auth headers)
│   ├── test_auth.py              # Tests for register + login
│   └── test_notes.py             # Tests for all note routes
│
├── .dockerignore
├── .env                          # Local secrets (never commit this)
├── .gitignore
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml            # Runs API + PostgreSQL together
├── Dockerfile                    # Builds the API image
└── requirements.txt              # Pinned dependencies
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT                           │
│         (Browser / curl / Swagger UI)               │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP Request
                       ▼
┌─────────────────────────────────────────────────────┐
│                  FASTAPI APP                        │
│                                                     │
│  ┌─────────────┐    ┌──────────────────────────┐   │
│  │   Routers   │───▶│     Dependencies         │   │
│  │  auth.py    │    │  get_current_user()      │   │
│  │  notes.py   │    │  get_db()                │   │
│  └──────┬──────┘    └──────────────────────────┘   │
│         │                                           │
│  ┌──────▼──────┐    ┌──────────────────────────┐   │
│  │  Schemas    │    │       Services            │   │
│  │ (Pydantic)  │    │  hash_password()          │   │
│  │ Validate in │    │  verify_password()        │   │
│  │ & shape out │    │  create_access_token()    │   │
│  └──────┬──────┘    │  decode_token()           │   │
│         │           └──────────────────────────┘   │
│  ┌──────▼──────┐                                   │
│  │   Models    │                                   │
│  │ (SQLAlchemy)│                                   │
│  └──────┬──────┘                                   │
└─────────┼───────────────────────────────────────────┘
          │ SQL
          ▼
┌─────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                    │
│         tables: users, notes                        │
└─────────────────────────────────────────────────────┘
```

**Layer responsibilities:**
- **Routers** — receive HTTP requests, call services, return responses
- **Schemas** — validate incoming data, shape outgoing data (never expose passwords)
- **Dependencies** — reusable FastAPI logic injected into routes (auth, DB session)
- **Services** — pure Python business logic, no FastAPI imports, fully testable
- **Models** — define database tables via SQLAlchemy ORM

---

## How the Code Flows

### Flow 1 — Register a new user

```
POST /api/v1/auth/register
Body: {"email": "nour@test.com", "username": "nour", "password": "password123"}

1. FastAPI receives request
2. Pydantic validates body against UserCreate schema
3. auth router checks: is email already taken? → 400 if yes
4. auth router checks: is username already taken? → 400 if yes
5. services/auth.py hashes the password with bcrypt
6. New User row inserted into PostgreSQL
7. UserResponse schema returned (id, email, username — NO password)
```

### Flow 2 — Login

```
POST /api/v1/auth/login
Form: username=nour, password=password123

1. FastAPI receives OAuth2PasswordRequestForm
2. Query DB for user by username → 401 if not found
3. services/auth.py verifies bcrypt hash → 401 if wrong
4. services/auth.py creates JWT token (sub=username, exp=+30min)
5. Return {"access_token": "eyJ...", "token_type": "bearer"}
```

### Flow 3 — Create a note (authenticated)

```
POST /api/v1/notes/
Headers: Authorization: Bearer eyJ...
Body: {"title": "My note", "content": "Hello", "tag": "work"}

1. FastAPI sees Depends(get_current_user) on the route
2. dependencies.py extracts token from Authorization header
3. decode_token() verifies JWT signature and expiry → 401 if invalid
4. Queries DB for user by username from token
5. Note created with owner_id = current_user.id
6. NoteResponse returned
```

### Flow 4 — Get notes (with optional tag filter)

```
GET /api/v1/notes/?tag=work
Headers: Authorization: Bearer eyJ...

1. get_current_user() resolves the authenticated user
2. Query: SELECT * FROM notes WHERE owner_id = :user_id AND tag = :tag
3. Returns only this user's notes — never another user's
```

---

## Database Design

```
┌─────────────────────────┐       ┌──────────────────────────────┐
│         users           │       │           notes              │
├─────────────────────────┤       ├──────────────────────────────┤
│ id          INT (PK)    │◄──┐   │ id          INT (PK)         │
│ email       VARCHAR     │   │   │ title       VARCHAR          │
│ username    VARCHAR     │   │   │ content     VARCHAR          │
│ hashed_pwd  VARCHAR     │   │   │ tag         VARCHAR nullable │
│ is_active   BOOLEAN     │   │   │ is_pinned   BOOLEAN          │
│ created_at  DATETIME    │   └───│ owner_id    INT (FK)         │
└─────────────────────────┘       │ created_at  DATETIME         │
                                  │ updated_at  DATETIME         │
                                  └──────────────────────────────┘
```

**Key constraint:** every note has an `owner_id` foreign key pointing to `users.id`.
The notes router always filters by `owner_id = current_user.id` — users can never see each other's notes.

---

## Authentication System

SmartNotes uses **JWT (JSON Web Token)** — the industry standard for stateless APIs.

### How JWT works

```
1. User logs in with correct credentials

2. Server creates a signed token:
   Header:  {"alg": "HS256", "typ": "JWT"}
   Payload: {"sub": "nour", "exp": 1234567890}
   Signed with SECRET_KEY

3. Client stores token and sends it on every request:
   Authorization: Bearer eyJhbGci...

4. Server verifies signature + expiry — no DB lookup needed
   Any server instance can verify any token (horizontally scalable)
```

### Why not sessions?

Sessions require a shared session store (Redis, DB) on the server. With JWTs, the token is self-verifying — perfect for distributed systems and microservices.

### Why bcrypt for passwords?

bcrypt is a one-way hashing algorithm designed to be deliberately slow, making brute-force attacks computationally expensive.

```
"password123"  →  bcrypt (slow, salted)  →  "$2b$12$Kix..."
```

Even if the database is leaked, passwords cannot be reversed.

---

## Getting Started

### Option 1 — Docker (recommended, zero setup)

```bash
git clone https://github.com/Nour-Faker/notes-api.git
cd notes-api

docker compose up --build
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- PostgreSQL runs inside Docker on port 5433

### Option 2 — Local Python

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

# Configure .env then:
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Environment variables (.env)

```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/smartnotes
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Running Tests

### Setup (one time)

```bash
psql -U postgres -c "CREATE DATABASE smartnotes_test;"
```

### Run tests

```bash
# All tests with verbose output
python -m pytest tests/ -v

# Specific file
python -m pytest tests/test_auth.py -v

# Specific test
python -m pytest tests/test_auth.py::test_login_success -v
```

### Test results

```
tests/test_auth.py::test_register_success           PASSED
tests/test_auth.py::test_register_duplicate_email   PASSED
tests/test_auth.py::test_login_success              PASSED
tests/test_auth.py::test_login_wrong_password       PASSED
tests/test_notes.py::test_create_note               PASSED
tests/test_notes.py::test_get_notes_empty           PASSED
tests/test_notes.py::test_get_notes_returns_only_own PASSED
tests/test_notes.py::test_delete_note               PASSED
tests/test_notes.py::test_cannot_access_without_token PASSED

9 passed in 3.58s
```

### How test isolation works

```python
# Every test gets a fresh database — no state leaks between tests
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)   # create tables
    yield                                    # test runs
    Base.metadata.drop_all(bind=engine)     # wipe everything
```

A separate `smartnotes_test` database is used — production data is never touched.

---

## Database Migrations

Alembic tracks every schema change like Git tracks code. Never modify production tables manually.

### Workflow

```bash
# 1. Edit a SQLAlchemy model (add/remove/change a column)

# 2. Generate migration automatically
python -m alembic revision --autogenerate -m "describe your change"

# 3. Review the generated file in migrations/versions/

# 4. Apply it
python -m alembic upgrade head
```

### Useful commands

```bash
python -m alembic current          # what version is the DB at?
python -m alembic history          # full migration timeline
python -m alembic downgrade -1     # roll back one migration
python -m alembic upgrade head     # apply all pending migrations
```

### Migration history

```
21f8f5ea5d0e  create users and notes tables    ← CREATE TABLE users, notes
538214d259fd  add is_pinned to notes           ← ALTER TABLE notes ADD COLUMN is_pinned
```

The second migration added a column to a live table — zero data loss, zero downtime.

---

## API Reference

### Auth

| Method | Endpoint | Body / Form | Response |
|---|---|---|---|
| POST | `/api/v1/auth/register` | JSON: email, username, password | 201 UserResponse |
| POST | `/api/v1/auth/login` | Form: username, password | 200 Token |

### Notes (all require `Authorization: Bearer <token>`)

| Method | Endpoint | Body | Response |
|---|---|---|---|
| POST | `/api/v1/notes/` | JSON: title, content, tag? | 201 NoteResponse |
| GET | `/api/v1/notes/` | Query: ?tag= | 200 List[NoteResponse] |
| GET | `/api/v1/notes/{id}` | — | 200 NoteResponse |
| PATCH | `/api/v1/notes/{id}` | JSON: title?, content?, tag? | 200 NoteResponse |
| DELETE | `/api/v1/notes/{id}` | — | 204 No Content |

### Full example

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "nour@test.com", "username": "nour", "password": "password123"}'

# Login → save the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=nour" -F "password=password123" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create a note
curl -X POST http://localhost:8000/api/v1/notes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first note", "content": "Hello world", "tag": "work"}'

# Get all notes tagged "work"
curl "http://localhost:8000/api/v1/notes/?tag=work" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Design Decisions

**Why separate `services/` from `routers/`?**
Services are pure Python — no FastAPI, no HTTP. They can be unit tested in isolation and reused across routes. Mixing logic into routers makes code hard to test and impossible to reuse.

**Why a dedicated `dependencies.py`?**
FastAPI dependencies using `Depends()` need to import from both `database.py` and `services/auth.py`. Placing them in either file creates a circular import. A separate layer breaks the cycle cleanly — this is standard FastAPI project structure.

**Why `bcrypt==4.0.1` pinned in requirements.txt?**
bcrypt 4.1+ removed the `__about__` attribute that passlib reads for version detection. Without pinning, a `pip install` on a fresh machine installs the latest bcrypt and crashes on any password operation. Pinning ensures reproducible builds.

**Why JWT over session cookies?**
Sessions require shared server-side state (a Redis store or DB table). JWT tokens are cryptographically self-verifying — any server instance can validate any token without coordination. This makes the API stateless and horizontally scalable by default.

**Why a separate test database?**
Tests run `create_all` and `drop_all` on every test — they constantly destroy data. Running against the development database would corrupt it. A dedicated `smartnotes_test` database guarantees perfect isolation.

**Why Docker Compose healthcheck?**
Without a healthcheck, the API container starts immediately and tries to connect to PostgreSQL before it's ready — causing a crash. The healthcheck (`pg_isready`) makes the API container wait until PostgreSQL actually accepts connections before starting.

---

## Roadmap

- [x] FastAPI project structure (routers, services, schemas, models)
- [x] PostgreSQL + SQLAlchemy ORM
- [x] JWT authentication from scratch
- [x] User-owned notes with authorization
- [x] Docker + docker-compose with healthchecks
- [x] Alembic database migrations
- [x] pytest test suite (9 tests, 100% pass)
- [ ] Pagination on GET /notes (`skip` + `limit`)
- [ ] Full-text search on title and content
- [ ] Fix deprecation warnings (utcnow, declarative_base, class Config)
- [ ] GitHub Actions CI — run tests on every push
- [ ] Production secrets management (no hardcoded values)

---

## Author

**Nour** — Computer Engineering student at ENICarthage, Tunisia
Building toward AI engineering, one production system at a time.

---

## License

MIT
