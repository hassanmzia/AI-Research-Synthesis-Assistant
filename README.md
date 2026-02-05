# AI Research Synthesis Assistant

A professional-grade, multi-agent AI system for research paper analysis, RAG-based Q&A, synthesis report generation, and quality evaluation. Built with Django, PostgreSQL, Node.js, React/TypeScript, and Docker Compose.

Based on the JHU Agentic AI RAG notebook by Zia Hassan, this application transforms the notebook's capabilities into a production-ready, multi-agent web application with MCP and A2A protocol support.

---

## Architecture

```
                    http://172.168.1.95:3066
                           |
                    ┌──────┴──────┐
                    │   Nginx     │  (port 3066)
                    │  Reverse    │
                    │   Proxy     │
                    └──┬───┬───┬──┘
                       │   │   │
        ┌──────────────┘   │   └──────────────┐
        ▼                  ▼                  ▼
 ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
 │   React     │   │  Node.js    │   │   Django    │
 │  Frontend   │   │  Gateway    │   │  Backend    │
 │ (TypeScript)│   │ (port 3071) │   │ (port 3070) │
 └─────────────┘   └──────┬──────┘   └──┬───┬───┬──┘
                          │              │   │   │
              ┌───────────┘    ┌─────────┘   │   └─────────┐
              ▼                ▼             ▼             ▼
       ┌───────────┐   ┌───────────┐ ┌───────────┐ ┌───────────┐
       │   Redis   │   │ PostgreSQL│ │ ChromaDB  │ │  Celery   │
       │(port 6380)│   │(port 5433)│ │(port 8100)│ │  Workers  │
       └───────────┘   └───────────┘ └───────────┘ └───────────┘
```

## Multi-Agent System

```
                    ┌──────────────────────────┐
                    │   Orchestrator Agent      │
                    │  (Routes & Coordinates)   │
                    └──┬──┬──┬──┬──┬──┬──┬─────┘
                       │  │  │  │  │  │  │
    ┌──────────────────┘  │  │  │  │  │  └──────────────────┐
    ▼                     ▼  │  │  │  ▼                     ▼
 ┌─────────┐  ┌──────────┐  │  │  │ ┌──────────┐  ┌─────────┐
 │Ingestion│  │Embedding │  │  │  │ │ Citation │  │ Summary │
 │  Agent  │→ │  Agent   │  │  │  │ │  Agent   │  │  Agent  │
 └─────────┘  └──────────┘  │  │  │ └──────────┘  └─────────┘
                             ▼  ▼  ▼
                    ┌──────────┐ ┌──────────┐
                    │Retrieval │ │Evaluation│
                    │  Agent   │ │  Agent   │
                    └────┬─────┘ └──────────┘
                         ▼
                    ┌──────────┐
                    │Synthesis │
                    │  Agent   │
                    └──────────┘
```

**Agents communicate via A2A (Agent-to-Agent) protocol and expose capabilities via MCP (Model Context Protocol).**

## Features

### From the Original Notebook
- PDF document loading and text extraction (PyPDFDirectoryLoader)
- Text chunking with tiktoken encoding (cl100k_base, 1000 tokens, 200 overlap)
- Vector embeddings using OpenAI text-embedding-ada-002
- ChromaDB vector store with similarity search (k=10)
- RAG Q&A pipeline with structured prompting
- LLM-as-a-judge evaluation: **Groundedness** and **Relevance** scoring (1-5 scale)
- GPT-4o-mini with specific parameters (temp=0, top_p=0.95, freq_penalty=1.2)

### Enhanced Professional Features
- **Multi-Agent Architecture**: 8 specialized agents (Orchestrator, Ingestion, Embedding, Retrieval, Synthesis, Evaluation, Citation, Summary)
- **MCP Protocol**: Expose all agent capabilities as MCP tools for external AI client integration
- **A2A Protocol**: Google A2A protocol for agent discovery, task management, and inter-agent messaging
- **User Authentication**: JWT-based auth with registration, login, and profile management
- **Research Workspaces**: Project-based organization with collaboration support
- **Real-time Chat**: Conversation-based Q&A with message history and source references
- **5-Metric Evaluation**: Groundedness, Relevance, Coherence, Completeness, Faithfulness
- **Synthesis Reports**: Literature reviews, comparative analysis, research gap analysis, trend analysis, executive summaries
- **Citation Management**: Automatic extraction with APA, MLA, and BibTeX formatting
- **Export System**: PDF, DOCX, CSV, Excel, Markdown, JSON, BibTeX export formats
- **Analytics Dashboard**: Usage metrics, quality scores, agent performance tracking
- **Annotations & Bookmarks**: Annotate papers and bookmark conversations
- **Token Quota Management**: Per-user usage tracking and quotas
- **Dark Mode**: Full dark/light theme support
- **WebSocket**: Real-time notifications for async operations
- **Async Processing**: Celery workers for paper ingestion, report generation, exports
- **API Key Management**: Configure personal API keys for multiple providers
- **Rate Limiting**: Built-in rate limiting at both gateway and API level
- **Audit Logging**: Complete agent interaction and query history logging

## Tech Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Frontend | React 18, TypeScript, Tailwind CSS | (via Nginx) |
| API Gateway | Node.js, Express, WebSocket | 3071 |
| Backend | Django 5.1, DRF, Celery | 3070 |
| Database | PostgreSQL 16 | 5433 |
| Cache/Broker | Redis 7 | 6380 |
| Vector Store | ChromaDB | 8100 |
| Reverse Proxy | Nginx | **3066** |
| Task Monitor | Celery Flower | 5556 |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 2. Start All Services
```bash
./scripts/start.sh
```

### 3. Access the Application
- **Main Site**: http://172.168.1.95:3066
- **Admin Panel**: http://172.168.1.95:3066/admin/
- **API Gateway**: http://172.168.1.95:3071/health
- **Celery Monitor**: http://172.168.1.95:5556

### Default Credentials
| User | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Researcher | researcher | research123 |

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `GET  /api/auth/me/` - Get current user

### Projects
- `GET/POST /api/projects/` - List/create projects
- `GET/PUT/DELETE /api/projects/:id/` - Project detail

### Papers
- `POST /api/papers/upload/` - Upload PDF
- `GET  /api/papers/:id/summary/` - Get AI summary
- `GET  /api/papers/:id/citations/` - Extract citations

### RAG Query
- `POST /api/query/` - Ask a question (RAG)
- `GET  /api/query/history/` - Query history
- `POST /api/query/:id/evaluate/` - Run evaluation

### Synthesis Reports
- `POST /api/reports/generate/` - Generate report
- `GET  /api/reports/:id/` - Get report

### MCP Protocol
- `GET  /mcp/` - Server manifest
- `GET  /mcp/tools/` - List available tools
- `POST /mcp/tools/:name/execute/` - Execute tool

### A2A Protocol
- `GET  /a2a/` - Agent card
- `GET  /a2a/agents/` - List agents
- `POST /a2a/tasks/` - Create task
- `POST /a2a/message/` - Send message

## Stopping Services

```bash
./scripts/stop.sh
```

## Project Structure
```
AI-Research-Synthesis-Assistant/
├── docker-compose.yml          # Multi-service orchestration
├── .env.example                # Environment template
├── nginx/                      # Reverse proxy config
│   ├── nginx.conf
│   └── conf.d/default.conf
├── backend/                    # Django backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/                 # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   └── research_assistant/     # Main app
│       ├── models/             # Database models
│       ├── agents/             # Multi-agent system
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
│       ├── mcp/                # MCP protocol server
│       ├── a2a/                # A2A protocol server
│       ├── services/           # Business logic
│       └── tasks.py            # Celery async tasks
├── gateway/                    # Node.js API gateway
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── index.ts
│       ├── routes/
│       ├── middleware/
│       ├── services/
│       │   └── websocket.ts
│       └── types/
├── frontend/                   # React TypeScript frontend
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── pages/
│       ├── services/api.ts
│       ├── store/
│       ├── hooks/
│       └── types/
├── scripts/                    # Utility scripts
│   ├── start.sh
│   ├── stop.sh
│   └── init_db.sql
└── sample_papers/              # Sample PDFs for testing
```

## License

This project is for educational and research purposes.
Based on JHU Agentic AI RAG Notebook by Zia Hassan.
