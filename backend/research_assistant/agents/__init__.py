"""
Multi-Agent AI Research Synthesis System
=========================================

Agent Architecture:
- OrchestratorAgent: Coordinates all agents, routes requests
- IngestionAgent: Handles PDF upload, text extraction, chunking
- EmbeddingAgent: Creates and manages vector embeddings in ChromaDB
- RetrievalAgent: Similarity search and context retrieval
- SynthesisAgent: RAG-based answer generation using LLM
- EvaluationAgent: Groundedness and relevance scoring (LLM-as-judge)
- CitationAgent: Extracts and formats citations/references
- SummaryAgent: Generates paper summaries and abstracts

Communication:
- A2A (Agent-to-Agent) protocol for inter-agent messaging
- MCP (Model Context Protocol) for tool exposure to external clients
"""

from .base import BaseAgent
from .orchestrator import OrchestratorAgent
from .ingestion import IngestionAgent
from .embedding import EmbeddingAgent
from .retrieval import RetrievalAgent
from .synthesis import SynthesisAgent
from .evaluation import EvaluationAgent
from .citation import CitationAgent
from .summary import SummaryAgent

__all__ = [
    "BaseAgent",
    "OrchestratorAgent",
    "IngestionAgent",
    "EmbeddingAgent",
    "RetrievalAgent",
    "SynthesisAgent",
    "EvaluationAgent",
    "CitationAgent",
    "SummaryAgent",
]
