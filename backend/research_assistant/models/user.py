import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with research-specific fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True, default="")
    institution = models.CharField(max_length=255, blank=True, default="")
    research_interests = models.JSONField(default=list, blank=True)
    avatar_url = models.URLField(blank=True, default="")
    openai_api_key = models.CharField(
        max_length=255, blank=True, default="",
        help_text="User's personal OpenAI API key (encrypted at rest)",
    )
    usage_quota_tokens = models.BigIntegerField(
        default=1_000_000,
        help_text="Monthly token quota",
    )
    tokens_used_this_month = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def quota_remaining(self):
        return max(0, self.usage_quota_tokens - self.tokens_used_this_month)
