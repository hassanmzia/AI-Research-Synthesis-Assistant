# AI Research Synthesis Assistant

A production-grade, multi-agent AI system for research paper analysis, RAG-based question answering, synthesis report generation, and quality evaluation. Built with a modern microservices architecture using Django, PostgreSQL, Node.js, React/TypeScript, and Docker Compose.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Multi-Agent System](#multi-agent-system)
4. [Technology Stack](#technology-stack)
5. [Features](#features)
6. [Installation & Setup](#installation--setup)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)
9. [Agent Protocols (MCP & A2A)](#agent-protocols-mcp--a2a)
10. [Development Guide](#development-guide)
11. [Troubleshooting](#troubleshooting)
12. [License](#license)

---

## Overview

The AI Research Synthesis Assistant is an enterprise-ready platform that transforms how researchers interact with academic literature. It combines:

- **Retrieval-Augmented Generation (RAG)**: Semantic search across uploaded research papers with context-aware responses
- **Multi-Agent Orchestration**: 8 specialized AI agents working together via standardized protocols
- **Quality Assurance**: LLM-as-a-judge evaluation with multi-metric scoring
- **Synthesis Capabilities**: Automated literature reviews, trend analysis, and research gap identification

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Document Ingestion** | PDF upload, text extraction, chunking with tiktoken encoding |
| **Semantic Search** | ChromaDB vector store with OpenAI embeddings for similarity search |
| **RAG Q&A** | Context-aware question answering with source citations |
| **Multi-Metric Evaluation** | Groundedness, Relevance, Coherence, Completeness, Faithfulness scoring |
| **Synthesis Reports** | Literature reviews, comparative analysis, executive summaries |
| **Agent Observability** | Full audit trail of agent interactions and A2A communications |
| **Export System** | PDF, DOCX, CSV, Excel, Markdown, JSON, BibTeX formats |

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    React Frontend (TypeScript)                       │    │
│  │  • Dashboard  • Projects  • Papers  • Chat  • Reports  • Agents     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GATEWAY LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Nginx Reverse Proxy (Port 13066)                  │    │
│  │  • SSL Termination  • Load Balancing  • Static File Serving          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                          │              │              │                     │
│              ┌───────────┘              │              └───────────┐         │
│              ▼                          ▼                          ▼         │
│  ┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐    │
│  │   Static Assets   │    │   Node.js Gateway  │    │   Django Backend  │    │
│  │   (React Build)   │    │     (Port 3071)    │    │    (Port 3070)    │    │
│  └───────────────────┘    │  • WebSocket       │    │  • REST API       │    │
│                           │  • Rate Limiting   │    │  • Authentication │    │
│                           │  • Request Routing │    │  • Business Logic │    │
│                           └───────────────────┘    └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVICE LAYER                                   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Multi-Agent Orchestration System                  │    │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │    │
│  │  │Orchestrator│ │ Ingestion │ │ Embedding │ │ Retrieval │           │    │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │    │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │    │
│  │  │ Synthesis │ │ Evaluation│ │  Citation │ │  Summary  │           │    │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  Celery Workers │    │   Celery Beat   │    │  Celery Flower  │         │
│  │  (Async Tasks)  │    │   (Scheduler)   │    │   (Monitoring)  │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   PostgreSQL    │    │     ChromaDB    │    │      Redis      │         │
│  │   (Port 5433)   │    │   (Port 8100)   │    │   (Port 6380)   │         │
│  │                 │    │                 │    │                 │         │
│  │  • Users        │    │  • Embeddings   │    │  • Cache        │         │
│  │  • Projects     │    │  • Vector Index │    │  • Sessions     │         │
│  │  • Papers       │    │  • Collections  │    │  • Celery Broker│         │
│  │  • Queries      │    │                 │    │  • Rate Limits  │         │
│  │  • Reports      │    │                 │    │                 │         │
│  │  • Agent Logs   │    │                 │    │                 │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                  │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   OpenAI API    │    │ Other LLM APIs  │    │  File Storage   │         │
│  │                 │    │ (Configurable)  │    │   (Local/S3)    │         │
│  │  • GPT-4o-mini  │    │  • Anthropic    │    │                 │         │
│  │  • Embeddings   │    │  • Azure OpenAI │    │  • PDF Files    │         │
│  │  • Evaluations  │    │  • Custom       │    │  • Exports      │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Container Architecture

| Container | Service | Port | Description |
|-----------|---------|------|-------------|
| `nginx` | Reverse Proxy | 13066 | SSL termination, static files, request routing |
| `frontend` | React App | 3000 (internal) | Single-page application |
| `gateway` | Node.js API Gateway | 3071 | WebSocket, rate limiting, request proxying |
| `backend` | Django REST API | 3070 | Core business logic, authentication |
| `celery-worker` | Async Workers | - | Background task processing |
| `celery-beat` | Task Scheduler | - | Periodic task scheduling |
| `flower` | Task Monitor | 5556 | Celery task monitoring UI |
| `postgres` | PostgreSQL | 5433 | Primary database |
| `redis` | Redis | 6380 | Cache, message broker, sessions |
| `chroma` | ChromaDB | 8100 | Vector database for embeddings |

---

## Multi-Agent System

### Agent Overview

The system employs 8 specialized AI agents that communicate via the A2A (Agent-to-Agent) protocol:

```
                         ┌─────────────────────────────────┐
                         │      ORCHESTRATOR AGENT         │
                         │   "The Coordinator"             │
                         │                                 │
                         │   • Routes incoming requests    │
                         │   • Manages agent workflows     │
                         │   • Handles A2A discovery       │
                         │   • Aggregates responses        │
                         └───────────────┬─────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│  INGESTION AGENT  │        │  RETRIEVAL AGENT  │        │  SYNTHESIS AGENT  │
│  "The Processor"  │        │  "The Searcher"   │        │  "The Writer"     │
│                   │        │                   │        │                   │
│  • PDF extraction │        │  • Semantic search│        │  • Report writing │
│  • Text chunking  │        │  • Context ranking│        │  • Literature     │
│  • Metadata parse │        │  • Source citing  │        │    reviews        │
└─────────┬─────────┘        └───────────────────┘        └───────────────────┘
          │
          ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│  EMBEDDING AGENT  │        │  EVALUATION AGENT │        │  CITATION AGENT   │
│  "The Encoder"    │        │  "The Judge"      │        │  "The Formatter"  │
│                   │        │                   │        │                   │
│  • Vector encoding│        │  • Quality scoring│        │  • Citation       │
│  • ChromaDB store │        │  • LLM-as-judge   │        │    extraction     │
│  • Similarity calc│        │  • Multi-metric   │        │  • APA/MLA/BibTeX │
└───────────────────┘        └───────────────────┘        └───────────────────┘

                             ┌───────────────────┐
                             │   SUMMARY AGENT   │
                             │  "The Summarizer" │
                             │                   │
                             │  • Key points     │
                             │  • Executive      │
                             │    summaries      │
                             └───────────────────┘
```

### Agent Specifications

| Agent | Purpose | Capabilities | A2A Protocol |
|-------|---------|--------------|--------------|
| **Orchestrator** | Central coordinator | `route_requests`, `coordinate_agents`, `manage_workflows`, `agent_discovery` | ✓ |
| **Ingestion** | Document processing | `pdf_extraction`, `text_chunking`, `metadata_parsing` | ✓ |
| **Embedding** | Vector encoding | `generate_embeddings`, `store_vectors`, `similarity_search` | ✓ |
| **Retrieval** | Context retrieval | `semantic_search`, `context_ranking`, `source_citation` | ✓ |
| **Synthesis** | Content generation | `report_writing`, `literature_review`, `trend_analysis` | ✓ |
| **Evaluation** | Quality assessment | `groundedness_check`, `relevance_scoring`, `coherence_eval` | ✓ |
| **Citation** | Reference formatting | `citation_extraction`, `format_apa`, `format_mla`, `format_bibtex` | ✓ |
| **Summary** | Summarization | `key_point_extraction`, `executive_summary`, `abstract_generation` | ✓ |

### Agent Communication Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          RAG QUERY WORKFLOW                                   │
└──────────────────────────────────────────────────────────────────────────────┘

User Query: "What are the key findings about climate change mitigation?"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. ORCHESTRATOR receives query                                               │
│    └──> Analyzes intent, determines required agents                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│ 2. RETRIEVAL AGENT            │   │ 3. EVALUATION AGENT           │
│    └──> Semantic search       │   │    └──> Prepared for scoring  │
│    └──> Returns top-k chunks  │   │                               │
│    └──> Ranks by relevance    │   │                               │
└───────────────────────────────┘   └───────────────────────────────┘
                    │                               │
                    ▼                               │
┌───────────────────────────────┐                   │
│ 4. SYNTHESIS AGENT            │                   │
│    └──> Generates answer      │                   │
│    └──> Cites sources         │                   │
│    └──> Structured response   │                   │
└───────────────────────────────┘                   │
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. EVALUATION AGENT scores response                                          │
│    └──> Groundedness: 4.5/5 (well-supported by context)                      │
│    └──> Relevance: 5/5 (directly addresses question)                         │
│    └──> Coherence: 4/5 (logically structured)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. ORCHESTRATOR aggregates and returns final response with:                  │
│    • Answer text with inline citations                                       │
│    • Source references                                                       │
│    • Quality scores                                                          │
│    • Token usage metrics                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Primary backend language |
| Django | 5.1 | Web framework |
| Django REST Framework | 3.14 | REST API |
| Celery | 5.3 | Async task processing |
| Gunicorn | 21.2 | WSGI server |
| PostgreSQL | 16 | Relational database |
| Redis | 7 | Cache & message broker |
| ChromaDB | 0.4 | Vector database |
| PyPDF | 3.17 | PDF processing |
| tiktoken | 0.5 | Token counting |
| OpenAI SDK | 1.6 | LLM integration |
| ReportLab | 4.0 | PDF generation |
| python-docx | 0.8 | DOCX generation |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2 | UI framework |
| TypeScript | 5.3 | Type-safe JavaScript |
| Tailwind CSS | 3.4 | Utility-first CSS |
| Vite | 5.0 | Build tool |
| Axios | 1.6 | HTTP client |
| React Router | 6.21 | Client-side routing |

### Gateway Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 20 LTS | Runtime |
| Express | 4.18 | Web framework |
| ws | 8.14 | WebSocket support |
| http-proxy-middleware | 2.0 | Request proxying |

### Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24+ | Containerization |
| Docker Compose | 2.23+ | Multi-container orchestration |
| Nginx | 1.25 | Reverse proxy |

---

## Features

### Core Features

#### 1. Document Management
- **PDF Upload**: Drag-and-drop or click-to-upload interface
- **Automatic Processing**: Text extraction, chunking, and embedding generation
- **Metadata Extraction**: Title, authors, abstract, publication date
- **Multi-Project Organization**: Organize papers into research projects

#### 2. RAG-Based Q&A
- **Semantic Search**: Find relevant passages across all uploaded papers
- **Context-Aware Responses**: Answers grounded in your research documents
- **Source Citations**: Every response includes references to source papers
- **Conversation History**: Maintain context across multiple questions

#### 3. Multi-Metric Evaluation
All responses are evaluated on 5 metrics using LLM-as-a-judge:

| Metric | Description | Scale |
|--------|-------------|-------|
| **Groundedness** | Is the answer supported by the retrieved context? | 1-5 |
| **Relevance** | Does the answer address the question asked? | 1-5 |
| **Coherence** | Is the answer logically structured and clear? | 1-5 |
| **Completeness** | Does the answer cover all aspects of the question? | 1-5 |
| **Faithfulness** | Does the answer avoid hallucination? | 1-5 |

#### 4. Synthesis Reports
Generate comprehensive research documents:

| Report Type | Description |
|-------------|-------------|
| **Literature Review** | Comprehensive analysis of research themes and findings |
| **Comparative Analysis** | Side-by-side comparison of methodologies and results |
| **Research Gap Analysis** | Identification of unexplored areas and opportunities |
| **Trend Analysis** | Temporal analysis of research directions |
| **Executive Summary** | High-level overview for stakeholders |

#### 5. Export System
Export reports and data in multiple formats:
- **PDF**: Professional formatted documents with citations
- **DOCX**: Microsoft Word compatible documents
- **Markdown**: For documentation and version control
- **CSV/Excel**: Structured data export
- **JSON**: API-friendly data format
- **BibTeX**: Bibliography management

#### 6. Agent Observability
Full transparency into AI agent operations:
- **Audit Logs**: Complete history of all agent interactions
- **A2A Tracing**: Track inter-agent communication
- **Performance Metrics**: Token usage, latency, success rates
- **Human-Readable Display**: Formatted payloads instead of raw JSON

### Additional Features

- **User Authentication**: JWT-based auth with secure token refresh
- **API Key Management**: Configure personal OpenAI/other provider keys
- **Dark Mode**: Full dark/light theme support
- **Real-time Updates**: WebSocket notifications for async operations
- **Rate Limiting**: Configurable request limits
- **Annotations**: Highlight and annotate paper sections
- **Bookmarks**: Save important conversations and findings

---

## Installation & Setup

### Prerequisites

- **Docker**: Version 24.0 or higher
- **Docker Compose**: Version 2.23 or higher
- **OpenAI API Key**: Required for LLM operations
- **Memory**: Minimum 8GB RAM recommended
- **Storage**: Minimum 10GB free disk space

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Research-Synthesis-Assistant.git
cd AI-Research-Synthesis-Assistant
```

#### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your configuration
nano .env  # or use your preferred editor
```

**Required environment variables:**

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-api-key-here

# Security (Change in production!)
DJANGO_SECRET_KEY=your-secure-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Database (Optional - defaults provided)
POSTGRES_PASSWORD=your-db-password
```

#### 3. Start All Services

```bash
# Make the start script executable
chmod +x scripts/start.sh

# Start all containers
./scripts/start.sh
```

The script will:
1. Build all Docker images
2. Create the database and run migrations
3. Create default admin and researcher users
4. Start all services

#### 4. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Main Application | http://localhost:13066 | React frontend |
| Admin Panel | http://localhost:13066/admin/ | Django admin |
| API Documentation | http://localhost:3070/api/ | REST API |
| Celery Monitor | http://localhost:5556 | Task monitoring |
| API Gateway | http://localhost:3071/health | Health check |

#### 5. Default Credentials

| User | Username | Password | Role |
|------|----------|----------|------|
| Administrator | admin | admin123 | Full access |
| Researcher | researcher | research123 | Standard user |

**Important**: Change these passwords immediately in production!

### Stopping Services

```bash
./scripts/stop.sh
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `OPENAI_MODEL` | gpt-4o-mini | LLM model for generation |
| `OPENAI_EMBEDDING_MODEL` | text-embedding-ada-002 | Embedding model |
| `DJANGO_SECRET_KEY` | - | Django security key |
| `JWT_SECRET` | - | JWT signing secret |
| `POSTGRES_DB` | research_assistant | Database name |
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | - | Database password |
| `REDIS_URL` | redis://redis:6379/0 | Redis connection URL |
| `CHROMA_HOST` | chroma | ChromaDB host |
| `CHROMA_PORT` | 8000 | ChromaDB port |
| `DEBUG` | False | Django debug mode |
| `ALLOWED_HOSTS` | * | Allowed hostnames |

### LLM Configuration

The system uses OpenAI's API with these default parameters:

```python
# Generation settings
TEMPERATURE = 0
TOP_P = 0.95
FREQUENCY_PENALTY = 1.2
MAX_TOKENS = 2000

# Chunking settings
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 200  # tokens
ENCODING = "cl100k_base"  # tiktoken encoding

# Retrieval settings
TOP_K = 10  # Number of chunks to retrieve
```

---

## API Reference

### Authentication Endpoints

```
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/me/
POST /api/auth/refresh/
POST /api/auth/logout/
```

### Projects

```
GET    /api/projects/           # List all projects
POST   /api/projects/           # Create project
GET    /api/projects/:id/       # Get project details
PUT    /api/projects/:id/       # Update project
DELETE /api/projects/:id/       # Delete project
```

### Papers

```
POST   /api/papers/upload/      # Upload PDF
GET    /api/papers/             # List papers
GET    /api/papers/:id/         # Get paper details
GET    /api/papers/:id/chunks/  # Get paper chunks
DELETE /api/papers/:id/         # Delete paper
```

### RAG Query

```
POST   /api/query/              # Execute RAG query
GET    /api/query/history/      # Query history
GET    /api/query/:id/          # Get query details
POST   /api/query/:id/evaluate/ # Evaluate response
```

**Query Request Body:**
```json
{
  "question": "What are the main findings?",
  "project_id": "uuid",
  "conversation_id": "uuid",  // Optional
  "top_k": 10                  // Optional
}
```

### Synthesis Reports

```
POST   /api/reports/generate/   # Generate report
GET    /api/reports/            # List reports
GET    /api/reports/:id/        # Get report
DELETE /api/reports/:id/        # Delete report
```

**Report Types:**
- `literature_review`
- `comparative_analysis`
- `research_gaps`
- `trend_analysis`
- `executive_summary`

### Exports

```
POST   /api/exports/            # Create export job
GET    /api/exports/:id/        # Get export status
GET    /api/exports/:id/download/ # Download file
```

### Agent Observability

```
GET    /api/agents/             # List agents
GET    /api/agents/logs/        # Agent execution logs
GET    /api/agents/interactions/ # A2A interactions
```

---

## Agent Protocols (MCP & A2A)

### MCP (Model Context Protocol)

Expose agent capabilities as tools for external AI clients:

```
GET  /mcp/                      # Server manifest
GET  /mcp/tools/                # List available tools
POST /mcp/tools/:name/execute/  # Execute a tool
```

**Available MCP Tools:**
- `ingest_paper` - Process a PDF document
- `search_papers` - Semantic search
- `generate_answer` - RAG Q&A
- `evaluate_response` - Quality evaluation
- `generate_report` - Create synthesis report
- `extract_citations` - Get paper citations

### A2A (Agent-to-Agent Protocol)

Google's A2A protocol for agent discovery and communication:

```
GET  /a2a/                      # Agent card
GET  /a2a/agents/               # Discover agents
POST /a2a/tasks/                # Create task
GET  /a2a/tasks/:id/            # Get task status
POST /a2a/message/              # Send message
```

**Agent Card Response:**
```json
{
  "name": "research-assistant",
  "version": "1.0",
  "protocol": "a2a",
  "capabilities": [
    "document_ingestion",
    "semantic_search",
    "rag_query",
    "synthesis_report",
    "quality_evaluation"
  ],
  "agents": [...]
}
```

---

## Development Guide

### Local Development Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 3070
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Gateway

```bash
cd gateway
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Style

- **Python**: Black, isort, flake8
- **TypeScript**: ESLint, Prettier
- **Pre-commit hooks**: Configured for consistent formatting

---

## Troubleshooting

### Common Issues

#### Port Conflicts

If you see "port is already allocated" errors:

```bash
# Check what's using the port
lsof -i :3070

# Stop conflicting services or change ports in .env
```

#### Database Migration Errors

```bash
# Reset and recreate database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python manage.py migrate
```

#### ChromaDB Connection Issues

Ensure ChromaDB is running and accessible:

```bash
curl http://localhost:8100/api/v1/heartbeat
```

#### Memory Issues

If containers are crashing due to memory:

```bash
# Increase Docker memory allocation
# Or reduce worker concurrency in .env:
CELERY_WORKER_CONCURRENCY=2
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker

# View last 100 lines
docker-compose logs --tail=100 backend
```

---

## Project Structure

```
AI-Research-Synthesis-Assistant/
├── docker-compose.yml          # Container orchestration
├── .env.example                # Environment template
├── README.md                   # This file
│
├── nginx/                      # Reverse proxy
│   ├── nginx.conf
│   └── conf.d/default.conf
│
├── backend/                    # Django backend
│   ├── Dockerfile
│   ├── entrypoint.sh           # Container initialization
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/                 # Django configuration
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   └── research_assistant/     # Main application
│       ├── models/             # Database models
│       │   ├── user.py
│       │   ├── project.py
│       │   ├── paper.py
│       │   ├── query.py
│       │   ├── report.py
│       │   └── agent_log.py
│       ├── agents/             # Multi-agent system
│       │   ├── base.py         # Base agent class
│       │   ├── orchestrator.py
│       │   ├── ingestion.py
│       │   ├── embedding.py
│       │   ├── retrieval.py
│       │   ├── synthesis.py
│       │   ├── evaluation.py
│       │   ├── citation.py
│       │   └── summary.py
│       ├── api/                # REST API
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── urls.py
│       │   └── authentication.py
│       ├── mcp/                # MCP protocol
│       ├── a2a/                # A2A protocol
│       ├── services/           # Business logic
│       │   ├── rag_service.py
│       │   ├── vector_service.py
│       │   └── export_service.py
│       └── tasks.py            # Celery tasks
│
├── gateway/                    # Node.js gateway
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── index.ts
│       ├── routes/
│       ├── middleware/
│       └── services/
│
├── frontend/                   # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── pages/
│       │   ├── DashboardPage.tsx
│       │   ├── ProjectsPage.tsx
│       │   ├── ChatPage.tsx
│       │   ├── AgentsPage.tsx
│       │   └── SettingsPage.tsx
│       ├── services/
│       │   └── api.ts
│       └── types/
│
├── scripts/                    # Utility scripts
│   ├── start.sh
│   ├── stop.sh
│   └── init_db.sql
│
├── docs/                       # Documentation
│   ├── architecture.drawio
│   └── architecture.pptx
│
└── sample_papers/              # Test documents
```

---

## License

This project is for educational and research purposes.

---

## Support

For issues and feature requests, please use the GitHub issue tracker.
