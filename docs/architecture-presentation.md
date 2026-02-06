---
marp: true
theme: default
paginate: true
backgroundColor: #fff
---

# AI Research Synthesis Assistant

## Technical Architecture Overview

**Multi-Agent RAG System for Research Paper Analysis**

---

# Agenda

1. System Overview
2. High-Level Architecture
3. Multi-Agent System
4. Technology Stack
5. Data Flow
6. Key Features
7. Deployment Architecture

---

# System Overview

## What is it?

A **production-grade, multi-agent AI system** for:

- Research paper analysis
- RAG-based question answering
- Synthesis report generation
- Quality evaluation with LLM-as-judge

---

# Key Capabilities

| Capability | Description |
|------------|-------------|
| **Document Ingestion** | PDF upload, text extraction, chunking |
| **Semantic Search** | ChromaDB vector store with OpenAI embeddings |
| **RAG Q&A** | Context-aware question answering |
| **Multi-Metric Evaluation** | Groundedness, Relevance, Coherence scoring |
| **Synthesis Reports** | Literature reviews, comparative analysis |
| **Agent Observability** | Full audit trail of A2A communications |

---

# High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
│              React Frontend (TypeScript)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     GATEWAY LAYER                            │
│    Nginx (13066) → Node.js (3071) → Django (3070)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                            │
│              Multi-Agent Orchestration System                │
│              Celery Workers | Beat | Flower                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│      PostgreSQL (5433) | ChromaDB (8100) | Redis (6380)     │
└─────────────────────────────────────────────────────────────┘
```

---

# Container Architecture

| Container | Service | Port |
|-----------|---------|------|
| nginx | Reverse Proxy | 13066 |
| frontend | React App | 3000 |
| gateway | Node.js API Gateway | 3071 |
| backend | Django REST API | 3070 |
| celery-worker | Async Workers | - |
| postgres | PostgreSQL | 5433 |
| redis | Redis | 6380 |
| chroma | ChromaDB | 8100 |

---

# Multi-Agent System

## 8 Specialized AI Agents

```
                    ┌───────────────────┐
                    │   ORCHESTRATOR    │
                    │  (Coordinator)    │
                    └─────────┬─────────┘
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │Ingestion │        │Retrieval │        │Synthesis │
    └──────────┘        └──────────┘        └──────────┘
          │
          ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │Embedding │        │Evaluation│        │ Citation │
    └──────────┘        └──────────┘        └──────────┘
                                                  │
                                            ┌──────────┐
                                            │ Summary  │
                                            └──────────┘
```

---

# Agent Specifications

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **Orchestrator** | Coordinator | Route requests, manage workflows |
| **Ingestion** | Document processing | PDF extraction, chunking |
| **Embedding** | Vector encoding | Generate embeddings, store vectors |
| **Retrieval** | Context retrieval | Semantic search, ranking |
| **Synthesis** | Content generation | Report writing, reviews |
| **Evaluation** | Quality assessment | Scoring, LLM-as-judge |
| **Citation** | Reference formatting | APA, MLA, BibTeX |
| **Summary** | Summarization | Key points, abstracts |

---

# Agent Communication Protocols

## A2A Protocol (Agent-to-Agent)

- Agent discovery
- Task management
- Inter-agent messaging

## MCP Protocol (Model Context Protocol)

- Tool exposure
- External AI client integration

---

# Technology Stack - Backend

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Primary language |
| Django 5.1 | Web framework |
| Django REST Framework | REST API |
| Celery | Async processing |
| PostgreSQL 16 | Database |
| Redis 7 | Cache & broker |
| ChromaDB | Vector database |
| OpenAI API | LLM integration |

---

# Technology Stack - Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type-safe JavaScript |
| Tailwind CSS | Styling |
| Vite | Build tool |
| Axios | HTTP client |

---

# RAG Query Data Flow

```
User Query
    │
    ▼
┌─────────────────┐
│  1. Orchestrator │ ─── Analyzes intent
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Retrieval│ │  Eval  │ ─── Prepared for scoring
└────┬───┘ └────────┘
     │
     ▼
┌────────────┐
│  Synthesis  │ ─── Generates answer
└─────┬──────┘
      │
      ▼
┌────────────┐
│ Evaluation  │ ─── Scores response
└─────┬──────┘
      │
      ▼
┌────────────┐
│   Response  │ ─── Answer + Sources + Scores
└────────────┘
```

---

# Multi-Metric Evaluation

## LLM-as-Judge Scoring (1-5 Scale)

| Metric | Description |
|--------|-------------|
| **Groundedness** | Is the answer supported by context? |
| **Relevance** | Does it address the question? |
| **Coherence** | Is it logically structured? |
| **Completeness** | Does it cover all aspects? |
| **Faithfulness** | Does it avoid hallucination? |

---

# Key Features

## Document Management
- PDF upload with drag-and-drop
- Automatic text extraction and chunking
- Multi-project organization

## RAG-Based Q&A
- Semantic search across papers
- Source citations in responses
- Conversation history

---

# Key Features (Continued)

## Synthesis Reports
- Literature reviews
- Comparative analysis
- Research gap analysis
- Trend analysis
- Executive summaries

## Export System
- PDF, DOCX, Markdown
- CSV, Excel, JSON
- BibTeX

---

# Agent Observability

## Full Transparency

- **Audit Logs**: Complete history of all agent interactions
- **A2A Tracing**: Track inter-agent communication
- **Performance Metrics**: Token usage, latency, success rates
- **Human-Readable Display**: Formatted payloads (not raw JSON)

---

# Deployment Architecture

## Docker Compose Orchestration

- 10 containers
- Isolated networks
- Volume persistence
- Health checks
- Auto-restart policies

## Quick Start

```bash
cp .env.example .env
./scripts/start.sh
```

Access: http://localhost:13066

---

# Summary

## AI Research Synthesis Assistant

- **8 Specialized AI Agents** with A2A/MCP protocols
- **RAG Pipeline** with ChromaDB vector search
- **Multi-Metric Evaluation** with LLM-as-judge
- **Full Observability** of agent interactions
- **Production-Ready** with Docker Compose deployment

---

# Questions?

## Resources

- **Documentation**: README.md
- **Architecture Diagram**: docs/architecture.drawio
- **API Reference**: /api/ endpoints

---

# Thank You

**AI Research Synthesis Assistant**

Multi-Agent RAG System for Research Paper Analysis
