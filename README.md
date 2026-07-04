<p align="center">
  <h1 align="center">🧠 MediMind AI</h1>
  <p align="center">
    <strong>Enterprise Multi-Agent Medical AI Assistant</strong>
  </p>
  <p align="center">
    A production-grade, multi-agent AI system for intelligent medical consultations, prescription analysis, report interpretation, and personalized health intelligence — powered by 28+ specialized AI agents orchestrated through CrewAI and Groq LLMs.
  </p>
  <p align="center">
    <a href="#architecture">Architecture</a> •
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#api-reference">API Reference</a> •
    <a href="#license">License</a>
  </p>
</p>

---

## ✨ Highlights

| Capability | Description |
|:---|:---|
| **🤖 28+ Specialized AI Agents** | Purpose-built agents for routing, triage, symptom extraction, drug interaction checking, and more |
| **🧬 5 Orchestration Crews** | Medical, Consultation, Prescription, Report Analysis, and Health Intelligence crews |
| **📊 RAG Pipeline** | Hybrid retrieval with Pinecone Cloud, BM25 keyword scoring, and multi-signal reranking |
| **🔬 Medical Report OCR** | PaddleOCR + pdfplumber pipeline with automated reference range evaluation |
| **💊 Prescription Intelligence** | 7-agent pipeline: extraction → explanation → interaction → allergy → contraindication → scheduling → summary |
| **🛡️ AI Safety Guardrails** | Input/output guardrails blocking prompt injection and unsafe medical advice |
| **📈 MLOps Dashboard** | Real-time LLM execution tracking, cost estimation, evaluation scoring, and prompt versioning |
| **🐳 Docker-Ready** | One-command deployment with Docker Compose (PostgreSQL + Backend + Frontend) |

---

## 🏗️ Architecture

<a name="architecture"></a>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React + Vite + TailwindCSS)         │
│                                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ Clinical │ │ Medical  │ │Medication│ │  Health  │ │   AI Operations  │  │
│  │Interview │ │ Reports  │ │  Center  │ │ Timeline │ │    Dashboard     │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │             │            │             │                │           │
│  ┌────┴─────────────┴────────────┴─────────────┴────────────────┴────────┐  │
│  │                    AuthContext + ProtectedRoute                        │  │
│  └───────────────────────────────┬───────────────────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │ REST API (Axios)
┌──────────────────────────────────┼──────────────────────────────────────────┐
│                       BACKEND (FastAPI + Uvicorn)                           │
│                                                                             │
│  ┌─────────────────────────── API Layer ────────────────────────────────┐   │
│  │ /auth  /chat  /consultation  /reports  /prescriptions  /timeline    │   │
│  │ /rag   /ai-ops  /vector-admin  /health                             │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                  │                                          │
│  ┌──────────────────── Middleware Stack ───────────────────────────────┐   │
│  │  CORS  │  Request Logging (structlog)  │  Response Timing          │   │
│  └────────┴───────────────────────────────┴───────────────────────────┘   │
│                                  │                                          │
│  ┌──────────────── AI Orchestration Layer (CrewAI) ───────────────────┐   │
│  │                                                                     │   │
│  │  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────────┐  │   │
│  │  │ Medical Crew   │  │ Consultation Crew│  │ Prescription Crew   │  │   │
│  │  │ (6 agents)     │  │ (5 agents)       │  │ (7 agents)          │  │   │
│  │  └───────────────┘  └──────────────────┘  └─────────────────────┘  │   │
│  │  ┌───────────────────┐  ┌───────────────────────────────────────┐  │   │
│  │  │ Report Analysis   │  │ Health Intelligence Crew              │  │   │
│  │  │ Crew (4 agents)   │  │ (5 agents)                           │  │   │
│  │  └───────────────────┘  └───────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                  │                                          │
│  ┌────────────── AI Platform (MLOps & Safety) ────────────────────────┐   │
│  │  Guardrails Engine  │  Evaluation Engine  │  Metrics & Cost Tracker│   │
│  │  Prompt Manager     │  Test Framework     │  Execution Logger      │   │
│  └─────────────────────┴─────────────────────┴────────────────────────┘   │
│                                  │                                          │
│  ┌────────────── RAG Pipeline ────────────────────────────────────────┐   │
│  │  Document Loader → Chunker → Embedder → Pinecone Ingestion        │   │
│  │  Query Embedding → Vector Search → Reranker → Citation Generation │   │
│  └──────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│  ┌──── Domain Services ─────────┴─────────────────────────────────────┐   │
│  │  OCR Engine (PaddleOCR)    │ Reference Range Engine                │   │
│  │  Report Extractor Pipeline │ Prescription Extractor Pipeline       │   │
│  │  Trend Engine              │ Comparison Engine                     │   │
│  │  PDF Generator             │ Timeline Sync Service                 │   │
│  └────────────────────────────┴───────────────────────────────────────┘   │
│                                  │                                          │
│  ┌──── Data Layer ───────────────┴────────────────────────────────────┐   │
│  │  SQLAlchemy ORM + Alembic Migrations  │  Pinecone Cloud (Vectors) │   │
│  │  PostgreSQL (Relational Data)         │  Embedding Service        │   │
│  └───────────────────────────────────────┴────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
   ┌────────┴────────┐  ┌─────────┴─────────┐  ┌─────────┴─────────┐
   │   PostgreSQL    │  │  Pinecone Cloud   │  │   Groq Cloud      │
   │   (pgvector)    │  │  (Vector Store)   │  │   (LLM Inference) │
   └─────────────────┘  └───────────────────┘  └───────────────────┘
```

---

## 🤖 Multi-Agent System

<a name="features"></a>

### Medical Crew — Chat & Triage Pipeline
Dynamic intent-based routing that activates only the agents needed per query:

```
User Message → Router Agent → [Conditional Activation]
                    │
                    ├── Patient Intake Agent (symptom/emergency/history intents)
                    ├── Emergency Detection Agent (symptom/emergency intents)
                    ├── Medical Knowledge Agent (all medical intents + RAG retrieval)
                    ├── Citation Agent (when knowledge chunks are retrieved)
                    └── Response Composer Agent (always — combines all outputs)
```

### Consultation Crew — AI Clinical Interview
A 5-agent pipeline that conducts structured clinical interviews:

| Agent | Role |
|:---|:---|
| **Symptom Extraction Agent** | Parses symptoms with duration, severity, location, frequency, and triggers |
| **Conversation State Agent** | Tracks interview progress across 6 stages (greeting → summary) |
| **Follow-Up Agent** | Generates targeted clinical questions to fill information gaps |
| **Urgency Assessment Agent** | Classifies urgency as routine, soon, urgent, or emergency |
| **Consultation Summary Agent** | Produces structured clinical summaries with recommendations |

### Prescription Crew — Medication Intelligence
A 7-agent pipeline for comprehensive prescription analysis:

| Agent | Role |
|:---|:---|
| **Prescription Extraction Agent** | Extracts medicines, dosages, frequency from OCR/text |
| **Medicine Explanation Agent** | Generates plain-language educational explanations |
| **Drug Interaction Agent** | Checks for dangerous drug-drug interactions |
| **Allergy Agent** | Cross-references medicines against patient allergy history |
| **Contraindication Agent** | Flags contraindications based on chronic conditions |
| **Medication Schedule Agent** | Builds optimized daily medication timetables |
| **Medication Summary Agent** | Synthesizes all findings into an actionable summary |

### Report Analysis Crew — Lab Report Intelligence
A 4-agent pipeline for medical report interpretation:

| Agent | Role |
|:---|:---|
| **Abnormal Value Detection Agent** | Identifies out-of-range and critical lab values |
| **Medical Explanation Agent** | Explains what each parameter means in plain language |
| **Report Clinical Summary Agent** | Generates clinical narrative with discussion points |
| **Report Citation Agent** | Attaches medical references and evidence citations |

### Health Intelligence Crew — Personalized Insights
A 5-agent pipeline for longitudinal health analysis:

| Agent | Role |
|:---|:---|
| **Timeline Agent** | Generates narrative health timelines from event data |
| **Trend Analysis Agent** | Identifies increasing, decreasing, or stable trends |
| **Risk Insight Agent** | Assesses health risks based on profile and history |
| **Comparison Agent** | Compares current values against demographic baselines |
| **Personalized Recommendation Agent** | Generates tailored health recommendations |

---

## 🔬 Core Features

### 📄 Medical Report Processing
- **OCR Engine**: PaddleOCR with automatic angle correction for images + pdfplumber for text-layer PDFs + PyMuPDF fallback for scanned PDFs
- **Reference Range Engine**: Automated evaluation against 18+ clinical parameters (CBC, metabolic panel, lipid panel, thyroid, vitamins) with critical value flagging
- **AI Analysis**: Multi-agent interpretation with abnormal detection, explanations, clinical summaries, and evidence citations

### 💊 Prescription Analysis
- Upload prescriptions (image/PDF) → OCR extraction → AI pipeline
- Drug interaction checking, allergy cross-referencing, contraindication flagging
- Automated medication scheduling with educational explanations
- Visual medication timeline component

### 🩺 AI Clinical Consultation
- Stateful multi-turn clinical interviews with slot-filling
- 6-stage consultation flow: Chief Complaint → Symptom Details → Medical History → Medications → Allergies → Lifestyle
- Real-time urgency assessment with 4-level triage
- Downloadable consultation summaries (PDF)

### 📊 Health Timeline & Trends
- Longitudinal tracking of lab parameters across multiple reports
- Trend detection (increasing/decreasing/stable) with percentage change
- AI-powered risk insights and personalized recommendations
- Visual trend charts with Recharts

### 🧠 RAG Knowledge Base
- **Pinecone Cloud** vector storage with multi-namespace isolation (`medical_knowledge`, `patient_reports`, `prescriptions`, `clinical_guidelines`, etc.)
- **Multi-provider embeddings**: Local Sentence Transformers (GPU-accelerated) with automatic fallback to Hugging Face Inference API
- **Hybrid reranking**: 70% semantic similarity + 20% keyword overlap + 10% medical relevance
- **Strict Validation Layer**: Discards hallucinated chunks using a strict minimum similarity threshold (`0.65`)
- **Context Deduplication**: Automatically deduplicates retrieved vectors to maximize context window efficiency
- **Patient Security Lock**: Hard-enforces `patient_id` metadata verification directly in the retrieval layer to prevent cross-patient data leakage
- Document ingestion pipeline: Load (PyMuPDF) → Chunk → Classify Intent → Embed → Store with rich metadata

### 🛡️ AI Safety & Guardrails
- **Input guardrails**: Prompt injection detection, unsafe medical request blocking
- **Output guardrails**: Prevents AI from issuing diagnoses or prescriptions
- **Evaluation engine**: Groundedness, relevance, hallucination scoring, and safety checks on every LLM response

### 📈 AI Operations (MLOps)
- **Execution tracking**: Every LLM call logged with agent name, model, tokens, latency, and status
- **Cost estimation**: Real-time cost tracking per million tokens (input/output)
- **Prompt versioning**: Version-controlled prompt templates with rollback capability
- **Evaluation dashboard**: Groundedness, faithfulness, and safety scores per execution

---

## 🛠️ Tech Stack

<a name="tech-stack"></a>

### Backend
| Technology | Purpose |
|:---|:---|
| **FastAPI** | Async REST API framework |
| **SQLAlchemy 2.0** | ORM with async support |
| **Alembic** | Database migrations |
| **PostgreSQL** (pgvector) | Relational database |
| **Groq** (LLaMA 3 70B) | Ultra-fast LLM inference |
| **CrewAI** | Multi-agent orchestration |
| **Pinecone** | Cloud vector database |
| **Sentence Transformers** | Local embedding generation (768-dim) |
| **PaddleOCR** | Medical document OCR |
| **pdfplumber / PyMuPDF** | PDF text extraction |
| **structlog** | Structured JSON logging |
| **bcrypt + python-jose** | Auth with JWT tokens |
| **ReportLab** | PDF generation |

### Frontend
| Technology | Purpose |
|:---|:---|
| **React 18** | Component UI framework |
| **TypeScript** | Type-safe development |
| **Vite** | Fast build tooling |
| **TailwindCSS** | Utility-first styling |
| **Recharts** | Data visualization & charts |
| **Lucide React** | Icon library |
| **Axios** | HTTP client |
| **React Router v6** | Client-side routing |
| **React Dropzone** | Drag & drop file upload |
| **jsPDF** | Client-side PDF generation |

### Infrastructure
| Technology | Purpose |
|:---|:---|
| **Docker Compose** | Multi-service orchestration |
| **pgvector** | PostgreSQL with vector extensions |
| **Pinecone Cloud** | Managed vector database |
| **Groq Cloud** | Managed LLM inference |

---

## 📁 Project Structure

```
medmind-ai/
├── backend/
│   ├── main.py                          # FastAPI app factory with startup verification
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/                  # 28+ specialized AI agents
│   │   │   │   ├── router_agent.py          # Intent classification & routing
│   │   │   │   ├── patient_intake_agent.py  # Patient context extraction
│   │   │   │   ├── emergency_detection_agent.py
│   │   │   │   ├── medical_knowledge_agent.py   # RAG-powered knowledge
│   │   │   │   ├── citation_agent.py            # Source citation
│   │   │   │   ├── response_composer_agent.py   # Final response assembly
│   │   │   │   ├── symptom_extraction_agent.py
│   │   │   │   ├── conversation_state_agent.py
│   │   │   │   ├── follow_up_agent.py
│   │   │   │   ├── urgency_assessment_agent.py
│   │   │   │   ├── consultation_summary_agent.py
│   │   │   │   ├── prescription_extraction_agent.py
│   │   │   │   ├── medicine_explanation_agent.py
│   │   │   │   ├── drug_interaction_agent.py
│   │   │   │   ├── allergy_agent.py
│   │   │   │   ├── contraindication_agent.py
│   │   │   │   ├── medication_schedule_agent.py
│   │   │   │   ├── medication_summary_agent.py
│   │   │   │   ├── abnormal_value_detection_agent.py
│   │   │   │   ├── medical_explanation_agent.py
│   │   │   │   ├── report_clinical_summary_agent.py
│   │   │   │   ├── report_citation_agent.py
│   │   │   │   ├── report_extraction_agent.py
│   │   │   │   ├── timeline_agent.py
│   │   │   │   ├── trend_analysis_agent.py
│   │   │   │   ├── risk_insight_agent.py
│   │   │   │   ├── comparison_agent.py
│   │   │   │   └── personalized_recommendation_agent.py
│   │   │   ├── crews/                   # Orchestration crews
│   │   │   │   ├── medical_crew.py          # Chat & triage pipeline
│   │   │   │   ├── consultation_crew.py     # Clinical interview pipeline
│   │   │   │   ├── prescription_crew.py     # Medication analysis pipeline
│   │   │   │   ├── report_analysis_crew.py  # Lab report pipeline
│   │   │   │   └── health_intelligence_crew.py  # Health insights pipeline
│   │   │   ├── services/
│   │   │   │   ├── groq_llm_service.py      # Singleton LLM client with retries & guardrails
│   │   │   │   ├── consultation_engine.py   # Stateful consultation state machine
│   │   │   │   ├── medical_ai_service.py    # AI service layer
│   │   │   │   └── vector_store.py
│   │   │   └── schemas.py              # Pydantic schemas for AI responses
│   │   ├── ai_platform/                # MLOps & Safety
│   │   │   ├── guardrails/guardrails.py     # Input/output safety checks
│   │   │   ├── evaluation/evaluation_engine.py  # Response quality scoring
│   │   │   ├── metrics/metrics_service.py   # Usage & cost aggregation
│   │   │   ├── prompt_manager/prompt_manager.py # Versioned prompt templates
│   │   │   └── testing/test_framework.py    # AI testing utilities
│   │   ├── medical_reports/
│   │   │   ├── ocr/engine.py                # PaddleOCR + PDF extraction
│   │   │   ├── extractor/pipeline.py        # Report data extraction
│   │   │   └── reference_ranges/engine.py   # Clinical reference evaluation
│   │   ├── prescriptions/
│   │   │   ├── ocr/ocr_engine.py            # Prescription OCR
│   │   │   └── extractor/pipeline.py        # Prescription data extraction
│   │   ├── health_timeline/
│   │   │   ├── analytics/trend_engine.py    # Longitudinal trend analysis
│   │   │   ├── comparison/comparison_engine.py
│   │   │   ├── services/pdf_generator.py    # Health report PDF export
│   │   │   └── timeline/sync_service.py     # Timeline event sync
│   │   ├── embeddings/                 # Multi-provider embedding system
│   │   │   ├── providers/
│   │   │   │   ├── base.py                  # Abstract provider interface
│   │   │   │   ├── local_provider.py        # Sentence Transformers (GPU)
│   │   │   │   └── api_provider.py          # Hugging Face API fallback
│   │   │   ├── factory.py                   # Provider factory
│   │   │   └── service.py                   # Unified embedding service
│   │   ├── vector_store/               # Pinecone integration
│   │   │   ├── base.py                      # Abstract vector store interface
│   │   │   ├── pinecone_store.py            # Pinecone implementation
│   │   │   ├── factory.py                   # Store factory
│   │   │   └── service.py                   # Vector store service
│   │   ├── rag/                        # Retrieval-Augmented Generation
│   │   │   ├── loader/                      # Document loaders
│   │   │   ├── chunker/                     # Text chunking strategies
│   │   │   ├── ingestion/pipeline.py        # End-to-end ingestion
│   │   │   ├── retriever/vector_search.py   # Semantic search
│   │   │   ├── reranker/reranker.py         # Multi-signal reranking
│   │   │   └── embedder/                    # Embedding integration
│   │   ├── api/                        # REST API endpoints
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   └── config.py                   # Centralized settings
│   ├── middleware/                      # CORS, logging, timing
│   ├── tests/                          # pytest test suite
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/                      # 21 application pages
│       │   ├── Chat.tsx                     # AI chat interface
│       │   ├── ClinicalInterview.tsx         # Multi-turn consultation
│       │   ├── ConsultationSummary.tsx       # Consultation results
│       │   ├── MedicalReports.tsx            # Report upload & listing
│       │   ├── ReportDetails.tsx             # Report analysis view
│       │   ├── MedicationCenter.tsx          # Prescription management
│       │   ├── PrescriptionDetails.tsx       # Prescription analysis view
│       │   ├── PatientDashboard.tsx          # Patient overview
│       │   ├── HealthTimeline.tsx            # Event timeline
│       │   ├── HealthTrends.tsx              # Trend charts
│       │   ├── KnowledgeBase.tsx             # RAG document management
│       │   ├── AIOperationsDashboard.tsx     # MLOps monitoring
│       │   ├── ExecutionInspector.tsx        # LLM execution details
│       │   ├── PromptManager.tsx             # Prompt versioning UI
│       │   └── VectorDatabaseDashboard.tsx   # Vector store monitoring
│       ├── components/                 # Reusable UI components
│       │   ├── Navbar.tsx
│       │   ├── ProtectedRoute.tsx
│       │   ├── MedicationTimeline.tsx
│       │   ├── ReportCharts.tsx
│       │   └── InteractionDashboard.tsx
│       ├── contexts/AuthContext.tsx     # JWT auth state management
│       ├── services/api.ts             # Axios API client
│       └── utils/cn.ts                 # TailwindCSS class merging
├── docker-compose.yml                  # Multi-service deployment
├── Dockerfile.backend
├── Dockerfile.frontend
├── alembic.ini
├── run_all.py                          # Dev launcher script
└── .env.example
```

---

## 🚀 Getting Started

<a name="getting-started"></a>

### Prerequisites
- **Docker** & **Docker Compose** (recommended)
- **Python** 3.12+ (for local backend development)
- **Node.js** 20+ and **npm** (for local frontend development)

### 1. Clone & Configure

```bash
git clone https://github.com/hemanthd4641/MediMind-AI-Multi-Agent-Medical-AI-Assistant.git
cd MediMind-AI-Multi-Agent-Medical-AI-Assistant
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
POSTGRES_USER=medmind
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=medmind_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Authentication
JWT_SECRET_KEY=your_jwt_secret

# AI Services
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=medmind-index

# Embeddings
EMBEDDING_PROVIDER=local          # or 'huggingface_api'
HF_TOKEN=your_huggingface_token   # Required for API fallback
```

### 2a. Docker Compose (Recommended)

```bash
docker compose up --build
```

| Service | URL |
|:---|:---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

### 2b. Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Reference

<a name="api-reference"></a>

| Endpoint | Method | Description |
|:---|:---|:---|
| `/api/v1/health` | GET | Health check (DB, Pinecone, Groq status) |
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | JWT authentication |
| `/api/v1/chat` | POST | AI chat with multi-agent pipeline |
| `/api/v1/consultation/start` | POST | Start clinical interview |
| `/api/v1/consultation/message` | POST | Send consultation message |
| `/api/v1/consultation/{id}/summary` | GET | Get consultation summary |
| `/api/v1/reports/upload` | POST | Upload medical report (PDF/image) |
| `/api/v1/reports/{id}` | GET | Get analyzed report details |
| `/api/v1/prescriptions/upload` | POST | Upload prescription |
| `/api/v1/prescriptions/{id}` | GET | Get prescription analysis |
| `/api/v1/timeline` | GET | Get health timeline events |
| `/api/v1/timeline/trends` | GET | Get health parameter trends |
| `/api/v1/rag/ingest` | POST | Ingest documents into knowledge base |
| `/api/v1/rag/search` | POST | Semantic search with reranking |
| `/api/v1/ai-ops/metrics` | GET | LLM usage & cost metrics |
| `/api/v1/ai-ops/executions` | GET | LLM execution history |
| `/api/v1/ai-ops/prompts` | GET/POST | Prompt template management |
| `/api/v1/vector/health` | GET | Vector database health & stats |

> **Full interactive documentation** available at `/docs` (Swagger UI) when the backend is running.

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest -v

# Individual test suites
pytest tests/test_health.py
pytest tests/test_embeddings.py
pytest tests/test_vector_store.py
pytest tests/test_phase3_ai.py
```

---

## 🔒 Security Features

- **JWT Authentication** with refresh tokens and bcrypt password hashing
- **Protected Routes** on both frontend and backend
- **Input Guardrails**: Blocks prompt injection attempts (`ignore previous instructions`, `reveal system prompt`, etc.)
- **Output Guardrails**: Prevents AI from issuing medical diagnoses or prescriptions
- **CORS Middleware**: Configurable cross-origin resource sharing
- **Request Logging**: Structured JSON logging with structlog for audit trails

---

## 📊 Data Models

| Model | Description |
|:---|:---|
| `User` | Authentication and profile data |
| `PatientProfile` | Medical history, allergies, chronic conditions |
| `MedicalReport` / `MedicalReportItem` | Lab reports with parameter-level analysis |
| `Prescription` / `PrescriptionItem` | Prescription data with drug details |
| `HealthEvent` / `HealthInsight` | Timeline events and AI-generated insights |
| `LLMExecution` / `EvaluationResult` | MLOps tracking and quality scoring |
| `PromptTemplate` | Versioned prompt management |
| `RefreshToken` | JWT refresh token storage |

---

## 🗺️ Roadmap

- [x] Multi-agent medical chat with dynamic routing
- [x] RAG pipeline with Pinecone Cloud
- [x] AI clinical consultation system
- [x] Medical report OCR and analysis
- [x] Prescription intelligence pipeline
- [x] Health timeline and trend analysis
- [x] AI Operations dashboard
- [x] Prompt versioning and management
- [x] AI safety guardrails
- [ ] FHIR/HL7 interoperability
- [ ] Real-time WebSocket streaming
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced A/B testing for prompts

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/hemanthd4641">hemanthd4641</a>
</p>
