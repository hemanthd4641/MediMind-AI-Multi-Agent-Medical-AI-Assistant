# README.md

# MediMind AI (Phase 1 Scaffold)

## Overview
MediMind AI is a **production‑ready, scalable scaffold** for a medical AI assistant. This repository contains a clean‑architecture backend built with **FastAPI**, a modern **React** frontend, and Docker‑based deployment. All AI‑specific features (RAG, OCR, CrewAI, etc.) are intentionally omitted for Phase 1.

## Architecture Diagram
```
+----------------+      +----------------+      +----------------+
|   Frontend     | <--->|   Backend API  | <--->|   PostgreSQL   |
| (React + Vite) |      | (FastAPI)      |      | (Data Store)   |
+----------------+      +----------------+      +----------------+
        |                     |                     |
        | Docker Compose      | Docker Compose      |
        +---------------------+---------------------+
```

## Folder Structure
```
medmind-ai/
├─ backend/
│  ├─ api/
│  │   └─ health.py
│  ├─ core/
│  ├─ config/
│  │   └─ settings.py
│  ├─ database/
│  │   ├─ __init__.py
│  │   └─ base.py
│  ├─ models/
│  ├─ schemas/
│  ├─ services/
│  ├─ repositories/
│  ├─ middleware/
│  │   ├─ cors.py
│  │   ├─ request_logging.py
│  │   └─ timing.py
│  ├─ utils/
│  │   ├─ logger.py
│  │   └─ exceptions.py
│  ├─ tests/
│  │   └─ test_health.py
│  ├─ alembic/
│  │   └─ (migration scaffolding)
│  ├─ requirements.txt
│  ├─ pyproject.toml
│  └─ app.py
├─ frontend/
│  ├─ src/
│  │   ├─ main.tsx
│  │   ├─ App.tsx
│  │   ├─ index.css
│  │   ├─ components/
│  │   │   └─ Navbar.tsx
│  │   ├─ pages/
│  │   │   ├─ Home.tsx
│  │   │   ├─ Login.tsx
│  │   │   ├─ Dashboard.tsx
│  │   │   ├─ Profile.tsx
│  │   │   ├─ Chat.tsx
│  │   │   ├─ Reports.tsx
│  │   │   └─ Settings.tsx
│  │   ├─ services/
│  │   │   └─ api.ts
│  │   ├─ contexts/
│  │   │   └─ AuthContext.tsx
│  │   ├─ hooks/
│  │   └─ utils/
│  ├─ vite.config.ts
│  ├─ tsconfig.json
│  ├─ tailwind.config.js
│  ├─ postcss.config.js
│  └─ package.json
├─ .env.example
├─ Dockerfile.backend
├─ Dockerfile.frontend
├─ docker-compose.yml
└─ .dockerignore
```

## Getting Started
### Prerequisites
- **Docker** & **Docker Compose**
- **Node.js** (>=20) and **npm** (or **yarn**) for local frontend development
- **Python** 3.12 (only needed if you run the backend outside Docker)

### Environment Variables
Copy the example file and fill in the values:
```bash
cp .env.example .env
```
Required variables:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `JWT_SECRET_KEY`
- `API_V1_STR` (default: `/api/v1`)

### Development Setup
#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
pip install -r requirements.txt
uv run app.py
```
The API will be available at `http://localhost:8000`.

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
The app runs at `http://localhost:5173`.

### Docker Compose (All services)
```bash
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: default port 5432

## Testing
### Backend
```bash
cd backend
pytest
```
### Frontend
```bash
cd frontend
npm test
```

## Production Build
```bash
docker compose -f docker-compose.yml up --build -d
```

## License
MIT

---
*This scaffold is intentionally minimalistic to serve as a solid foundation for future AI features.*
