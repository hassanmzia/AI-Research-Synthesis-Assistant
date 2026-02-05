import uuid

from django.conf import settings
from django.db import models


class Annotation(models.Model):
    """User annotations on papers or chunks."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="annotations",
    )
    paper = models.ForeignKey(
        "ResearchPaper",
        on_delete=models.CASCADE,
        related_name="annotations",
    )
    chunk = models.ForeignKey(
        "PaperChunk",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="annotations",
    )
    content = models.TextField()
    highlight_text = models.TextField(blank=True, default="")
    page_number = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=7, default="#FFE066")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "annotations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Annotation on {self.paper.title[:50]} by {self.user.username}"


class Bookmark(models.Model):
    """Bookmarked papers or conversations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    paper = models.ForeignKey(
        "ResearchPaper",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bookmarks",
    )
    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bookmarks",
    )
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bookmarks"
        ordering = ["-created_at"]

    def __str__(self):
        target = self.paper or self.conversation
        return f"Bookmark: {target}"
