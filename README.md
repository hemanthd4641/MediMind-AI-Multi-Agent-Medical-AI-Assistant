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

## Phase 11: Enterprise AI Capabilities (In Progress)
- Hybrid RAG Pipeline (BM25 + Dense)
- PII Masking & Security
- Prompt Experimentation Framework

## Pinecone Cloud Vector Architecture
The RAG pipeline has been refactored to use **Pinecone Cloud** as the primary vector store.
- **Provider Abstraction**: A `VectorStore` interface decouples storage from application logic.
- **Namespaces**: The system separates domains (e.g. `medical-knowledge`, `patient-reports`) using Pinecone namespaces to eliminate cross-contamination during retrieval.
- **Rich Metadata**: Documents are chunks into Pinecone alongside their original text, document IDs, titles, and structural metadata for precise filtering.
- **Monitoring**: Real-time Vector DB health and stats are available via the `VectorDatabaseDashboard` UI.

**Note:** Ensure `PINECONE_API_KEY` is set in your `.env` before running document ingestion.

## Multi-Provider Embedding Architecture (Refactored)
The embedding subsystem has been refactored to use an extensible **Provider Pattern** that supports both local hardware-accelerated processing and remote Hugging Face API processing.
- **Local Sentence Transformers (`local`)**: The default provider. The 768-dimension PyTorch model is loaded once on FastAPI startup and cached in memory. GPU (CUDA) is automatically detected and utilized if available, ensuring minimal latency and high throughput.
- **Hugging Face Inference API (`huggingface_api`)**: An alternative lightweight provider that offloads processing to the cloud. It features built-in exponential backoff for handling rate limits and "503 Model Loading" errors.
- **Automatic Fallback**: If `EMBEDDING_PROVIDER=local` but the system lacks sufficient RAM/VRAM or the `sentence-transformers` library fails to load, the backend will automatically and seamlessly fall back to the Hugging Face API, preventing server crashes.
- **Configuration**: 
  Set `EMBEDDING_PROVIDER=local` or `EMBEDDING_PROVIDER=huggingface_api` in your `.env`.
  Set `HF_TOKEN` in your `.env` to authenticate with the Hugging Face Inference API.
  Set `HF_API_TIMEOUT` and `HF_MAX_RETRIES` to configure API fallback resilience.

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
