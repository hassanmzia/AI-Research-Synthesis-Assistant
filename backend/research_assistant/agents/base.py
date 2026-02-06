"""Base agent class for the multi-agent system."""
import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from django.conf import settings
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    name: str = "base"
    description: str = "Base agent"

    def __init__(self, user=None, api_key: str | None = None, parent_log=None):
        self.user = user
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.request_id = str(uuid.uuid4())
        self.parent_log = parent_log  # For tracking A2A call hierarchy
        self._llm = None
        self._log = None

    @property
    def llm(self) -> ChatOpenAI:
        """Lazily create the LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.AI_DEFAULT_MODEL,
                temperature=settings.AI_DEFAULT_TEMPERATURE,
                max_tokens=settings.AI_DEFAULT_MAX_TOKENS,
                top_p=0.95,
                frequency_penalty=1.2,
                api_key=self.api_key,
                base_url=settings.OPENAI_BASE_URL,
            )
        return self._llm

    @abstractmethod
    def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the agent's primary task."""
        raise NotImplementedError

    def log_start(self, input_data: dict) -> None:
        """Log agent task start."""
        from ..models import AgentLog

        self._log = AgentLog.objects.create(
            agent_name=self.name,
            task_id=self.request_id,
            status="started",
            input_data=input_data,
            user=self.user,
            parent_log=self.parent_log,  # Link to parent for A2A hierarchy
        )
        self._start_time = time.time()
        parent_info = f" (parent: {self.parent_log.agent_name})" if self.parent_log else ""
        logger.info(f"[{self.name}] Started task {self.request_id}{parent_info}")

    def log_complete(self, output_data: dict, tokens_used: int = 0) -> None:
        """Log agent task completion."""
        if hasattr(self, "_log") and self._log:
            duration = int((time.time() - self._start_time) * 1000)
            self._log.status = "completed"
            self._log.output_data = output_data
            self._log.duration_ms = duration
            self._log.tokens_used = tokens_used
            self._log.save()
            logger.info(
                f"[{self.name}] Completed task {self.request_id} "
                f"in {duration}ms, {tokens_used} tokens"
            )

    def log_error(self, error_message: str) -> None:
        """Log agent task failure."""
        if hasattr(self, "_log") and self._log:
            duration = int((time.time() - self._start_time) * 1000)
            self._log.status = "failed"
            self._log.error_message = error_message
            self._log.duration_ms = duration
            self._log.save()
            logger.error(f"[{self.name}] Failed task {self.request_id}: {error_message}")

    def send_a2a_message(self, target_agent: str, payload: dict) -> dict:
        """Send a message to another agent via A2A protocol."""
        from ..models import AgentInteraction

        # Get current log for parent reference
        current_log = getattr(self, "_log", None)

        interaction = AgentInteraction.objects.create(
            source_agent=self.name,
            target_agent=target_agent,
            protocol="a2a",
            request_payload=payload,
            parent_log=current_log,  # Link interaction to parent log
        )

        logger.info(
            f"[A2A] {self.name} -> {target_agent}: {list(payload.keys())}"
        )

        try:
            agent_class = get_agent_class(target_agent)
            # Pass parent_log so child can link its log to parent
            agent = agent_class(
                user=self.user,
                api_key=self.api_key,
                parent_log=current_log,
            )
            start = time.time()
            result = agent.execute(**payload)
            duration = int((time.time() - start) * 1000)

            interaction.response_payload = result
            interaction.status = "success"
            interaction.duration_ms = duration
            interaction.child_log = getattr(agent, "_log", None)  # Link to child's log
            interaction.save()

            logger.info(
                f"[A2A] {self.name} <- {target_agent}: success ({duration}ms)"
            )

            return result
        except Exception as e:
            interaction.status = "failed"
            interaction.response_payload = {"error": str(e)}
            interaction.save()
            logger.error(f"[A2A] {self.name} <- {target_agent}: failed - {e}")
            raise

    def get_agent_card(self) -> dict:
        """Return the A2A agent card for discovery."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.get_capabilities(),
            "protocol": "a2a",
            "version": "1.0",
        }

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return []


def get_agent_class(agent_name: str):
    """Get agent class by name."""
    from . import (
        CitationAgent,
        EmbeddingAgent,
        EvaluationAgent,
        IngestionAgent,
        OrchestratorAgent,
        RetrievalAgent,
        SummaryAgent,
        SynthesisAgent,
    )

    agents = {
        "orchestrator": OrchestratorAgent,
        "ingestion": IngestionAgent,
        "embedding": EmbeddingAgent,
        "retrieval": RetrievalAgent,
        "synthesis": SynthesisAgent,
        "evaluation": EvaluationAgent,
        "citation": CitationAgent,
        "summary": SummaryAgent,
    }
    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")
    return agents[agent_name]
