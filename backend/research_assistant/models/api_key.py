import uuid

from django.conf import settings
from django.db import models


class APIKeyConfig(models.Model):
    """Store and manage API key configurations per user."""

    PROVIDER_CHOICES = [
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("cohere", "Cohere"),
        ("huggingface", "HuggingFace"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=500, help_text="Encrypted API key")
    base_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_key_configs"
        unique_together = ["user", "provider"]

    def __str__(self):
        return f"{self.user.username} - {self.provider}"
