import uuid

from django.conf import settings
from django.db import models


class AgentLog(models.Model):
    """Logs for multi-agent orchestration tracking."""

    AGENT_CHOICES = [
        ("orchestrator", "Orchestrator Agent"),
        ("ingestion", "Ingestion Agent"),
        ("embedding", "Embedding Agent"),
        ("retrieval", "Retrieval Agent"),
        ("synthesis", "Synthesis Agent"),
        ("evaluation", "Evaluation Agent"),
        ("citation", "Citation Agent"),
        ("summary", "Summary Agent"),
    ]

    STATUS_CHOICES = [
        ("started", "Started"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=50, choices=AGENT_CHOICES)
    task_id = models.CharField(max_length=255, help_text="Celery task ID or request ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="started")
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    duration_ms = models.IntegerField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_logs",
    )
    parent_log = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_logs",
        help_text="Parent agent log for A2A delegation tracking",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "agent_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.agent_name}] {self.status} - {self.task_id[:12]}"


class AgentInteraction(models.Model):
    """Records A2A (Agent-to-Agent) interactions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_agent = models.CharField(max_length=50)
    target_agent = models.CharField(max_length=50)
    protocol = models.CharField(
        max_length=20,
        choices=[("a2a", "A2A"), ("mcp", "MCP"), ("direct", "Direct")],
        default="a2a",
    )
    request_payload = models.JSONField(default=dict)
    response_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("timeout", "Timeout"),
        ],
        default="pending",
    )
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "agent_interactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_agent} -> {self.target_agent} ({self.protocol})"
