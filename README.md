# 🌦️ Klima API

Backend API for **Klima**, a weather-resilience and environmental monitoring platform built with **FastAPI**.  
This service provides REST endpoints for air quality, sensor data, user management, and analytics.

---

## 🚀 Tech Stack

| Layer | Tool | Purpose |
|-------|------|----------|
| API Framework | **FastAPI** | High-performance async Python web API |
| Server | **Uvicorn** | ASGI server used for local/dev runs |
| ORM | **SQLAlchemy** | Database abstraction and queries |
| Migration Tool | **Alembic** | Handles schema versioning |
| Database | **PostgreSQL** (default) | Relational DB used in staging/prod |
| Local DB | **SQLite** (optional) | Lightweight dev database |
| Auth | **FastAPI Users + python-jose + passlib** | JWT authentication and password hashing |
| Logging | **Loguru + python-json-logger** | Structured logs for cloud environments |
| Audit Trail | **Starlette Middleware** | Automatic logging of POST/PUT/DELETE actions |
| Security | **casbin + slowapi** | RBAC & rate-limiting middleware |
| Metrics | **prometheus-fastapi-instrumentator** | `/metrics` endpoint for monitoring |
| Config | **python-dotenv** | Load `.env` variables |
| Containerization | **Docker / docker-compose** | Consistent environment for dev and deployment |

---

## 🧩 Project Structure

```

klima-api/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API endpoints
│   ├── core/
│   │   ├── config.py        # Settings from .env
│   │   ├── database.py      # DB engine setup
│   │   ├── security.py      # JWT / auth utils
│   ├── utils/               # Helpers, logging setup
│   ├── audit/               # fastapi-audit-trails setup
│   └── **init**.py
├── alembic/                 # DB migrations
├── .env.example             # Environment template
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

````

---

## ⚙️ Environment Setup

### 1. Prerequisites
- Python **3.12+**
- PostgreSQL **15+**
- Docker + Compose (for containerized setup)
- `uv` for isolated installs

### 2. Create `.env` file
Copy `.env.example` → `.env` and adjust as needed:

```bash
APP_NAME=Klima API
APP_ENV=development
APP_PORT=8000

DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/klima
SECRET_KEY=change_this_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

LOG_LEVEL=INFO
````

---

## 🧠 Dependencies and Their Uses

| Package                                            | Purpose                                |
| -------------------------------------------------- | -------------------------------------- |
| **fastapi**                                        | Core web framework                     |
| **uvicorn[standard]**                              | Async server engine                    |
| **sqlalchemy**, **alembic**                        | ORM and DB migrations                  |
| **psycopg2-binary**                                | PostgreSQL driver                      |
| **python-dotenv**                                  | Load `.env` config                     |
| **loguru**, **python-json-logger**                 | Logging setup                          |
| **python-jose[cryptography]**, **passlib[bcrypt]** | JWT + password hashing                 |
| **fastapi-users**                                  | Prebuilt auth models                   |
| **casbin**                                         | Role-based access control              |
| **slowapi**                                        | API rate limiting                      |
| **prometheus-fastapi-instrumentator**              | Exposes `/metrics`                     |
| **requests**                                       | HTTP client for external data fetching |

---

## 🧰 Running the API

### 🖥 Local (dev)

```bash
# Option 1: using uv
uv run uvicorn app.main:app --reload

# Option 2: using Python
python -m uvicorn app.main:app --reload
```

The API will be available at:
👉 [http://localhost:8000](http://localhost:8000)

Docs auto-generate at:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)
👉 [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 🐳 Docker (recommended)

```bash
docker-compose up --build
```

This starts:

* `api` → FastAPI server
* `db` → PostgreSQL 16 with persistent volume

Environment vars are automatically injected from `.env`.

---

### 🧪 Running Migrations

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

### 📈 Monitoring & Audit

* `/metrics` — Prometheus-ready metrics
* `/audit` — Access audit logs (depends on config)
* Logs stream in JSON format (stdout) for ELK/Loki ingestion.

---

## 🧰 Useful Commands

| Command                         | Description               |
| ------------------------------- | ------------------------- |
| `uvicorn app.main:app --reload` | Start dev server          |
| `pytest`                        | Run tests                 |
| `alembic upgrade head`          | Apply DB migrations       |
| `docker-compose up`             | Run via Docker            |
| `docker-compose logs -f api`    | Follow API logs           |

---

## 🏗 Deployment Notes

* **Frontend (Vercel)** communicates with this backend via HTTPS.
* For production, run behind **NGINX or Traefik** for SSL and load balancing.
* Use environment variables for DB credentials and secrets.
* Log output is JSON — suitable for centralized monitoring (Datadog, ELK, Grafana Loki).

---

## 🧩 Extending / Integrating

* Add new modules under `app/routes/` and import in `main.py`.
* Use `Depends(get_db)` pattern for dependency injection.
* To add new models:

  1. Create model in `app/models/`.
  2. Add Pydantic schema in `app/schemas/`.
  3. Create API routes.
  4. Generate Alembic migration.

---

## ⚖️ License

MIT © 2025 Signal No. 5
Developed for environmental and disaster-response initiatives in collaboration with government agencies.

