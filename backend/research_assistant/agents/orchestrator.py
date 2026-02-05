"""Orchestrator Agent - Coordinates all agents and routes requests."""
import logging
from typing import Any

from .base import BaseAgent, get_agent_class

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "Coordinates all agents, routes requests, and manages the multi-agent workflow"

    def get_capabilities(self) -> list[str]:
        return [
            "route_requests",
            "coordinate_agents",
            "manage_workflows",
            "agent_discovery",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        action = kwargs.get("action")
        if not action:
            raise ValueError("action is required")

        self.log_start({"action": action, **kwargs})

        try:
            result = {}

            if action == "query":
                result = self._handle_query(**kwargs)
            elif action == "ingest_paper":
                result = self._handle_ingest(**kwargs)
            elif action == "generate_summary":
                result = self._handle_summary(**kwargs)
            elif action == "generate_report":
                result = self._handle_report(**kwargs)
            elif action == "extract_citations":
                result = self._handle_citations(**kwargs)
            elif action == "evaluate":
                result = self._handle_evaluate(**kwargs)
            elif action == "discover_agents":
                result = self._handle_discovery()
            else:
                raise ValueError(f"Unknown action: {action}")

            self.log_complete(result)
            return result

        except Exception as e:
            self.log_error(str(e))
            raise

    def _handle_query(self, **kwargs) -> dict:
        """Route a Q&A query through the RAG pipeline."""
        return self.send_a2a_message(
            "synthesis",
            {
                "question": kwargs["question"],
                "project_id": kwargs["project_id"],
                "conversation_id": kwargs.get("conversation_id"),
                "run_evaluation": kwargs.get("run_evaluation", True),
            },
        )

    def _handle_ingest(self, **kwargs) -> dict:
        """Route paper ingestion."""
        return self.send_a2a_message(
            "ingestion",
            {"paper_id": kwargs["paper_id"]},
        )

    def _handle_summary(self, **kwargs) -> dict:
        """Route summary generation."""
        return self.send_a2a_message(
            "summary",
            {
                "task_type": "paper_summary",
                "paper_id": kwargs["paper_id"],
            },
        )

    def _handle_report(self, **kwargs) -> dict:
        """Route synthesis report generation."""
        return self.send_a2a_message(
            "summary",
            {
                "task_type": kwargs.get("report_type", "literature_review"),
                "project_id": kwargs["project_id"],
                "report_id": kwargs.get("report_id"),
            },
        )

    def _handle_citations(self, **kwargs) -> dict:
        """Route citation extraction."""
        return self.send_a2a_message(
            "citation",
            {
                "paper_id": kwargs.get("paper_id"),
                "text": kwargs.get("text"),
                "format_style": kwargs.get("format_style", "apa"),
            },
        )

    def _handle_evaluate(self, **kwargs) -> dict:
        """Route evaluation."""
        return self.send_a2a_message(
            "evaluation",
            {
                "query_id": kwargs.get("query_id"),
                "question": kwargs["question"],
                "answer": kwargs["answer"],
                "context": kwargs["context"],
                "eval_types": kwargs.get(
                    "eval_types",
                    ["groundedness", "relevance", "coherence", "completeness", "faithfulness"],
                ),
            },
        )

    def _handle_discovery(self) -> dict:
        """Return information about all available agents."""
        agent_names = [
            "orchestrator", "ingestion", "embedding", "retrieval",
            "synthesis", "evaluation", "citation", "summary",
        ]
        agents = []
        for name in agent_names:
            agent_cls = get_agent_class(name)
            agent = agent_cls(user=self.user)
            agents.append(agent.get_agent_card())
        return {"agents": agents}
