import uuid

from django.conf import settings
from django.db import models


class QueryHistory(models.Model):
    """Tracks all RAG queries for analytics and auditing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="query_history",
    )
    project = models.ForeignKey(
        "ResearchProject",
        on_delete=models.CASCADE,
        related_name="query_history",
    )
    question = models.TextField()
    answer = models.TextField()
    context_chunks = models.JSONField(
        default=list,
        help_text="IDs of retrieved chunks used as context",
    )
    model_used = models.CharField(max_length=100)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    agents_involved = models.JSONField(
        default=list,
        help_text="List of agents that participated in this query",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "query_history"
        ordering = ["-created_at"]
        verbose_name_plural = "Query histories"

    def __str__(self):
        return f"Q: {self.question[:80]}..."


class QueryEvaluation(models.Model):
    """LLM-as-a-judge evaluation of a RAG response."""

    EVAL_TYPE_CHOICES = [
        ("groundedness", "Groundedness"),
        ("relevance", "Relevance"),
        ("coherence", "Coherence"),
        ("completeness", "Completeness"),
        ("faithfulness", "Faithfulness"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.ForeignKey(
        QueryHistory, on_delete=models.CASCADE, related_name="evaluations"
    )
    eval_type = models.CharField(max_length=20, choices=EVAL_TYPE_CHOICES)
    score = models.IntegerField(
        help_text="Score from 1-5",
    )
    explanation = models.TextField(
        help_text="Step-by-step evaluation reasoning",
    )
    evaluator_model = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "query_evaluations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.eval_type}: {self.score}/5"
