import uuid

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """A Q&A conversation within a research project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "ResearchProject", on_delete=models.CASCADE, related_name="conversations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=500, blank=True, default="New Conversation")
    is_pinned = models.BooleanField(default=False)
    message_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.project.name})"


class Message(models.Model):
    """A single message in a conversation."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    sources = models.JSONField(
        default=list, blank=True,
        help_text="List of source references used for this answer",
    )
    agent_name = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Which agent generated this message",
    )
    token_count = models.IntegerField(default=0)
    latency_ms = models.IntegerField(
        null=True, blank=True,
        help_text="Response generation time in milliseconds",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}..."
