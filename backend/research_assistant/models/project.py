import uuid

from django.conf import settings
from django.db import models


class ResearchProject(models.Model):
    """A research project / workspace that contains papers and conversations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    tags = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    vector_collection_name = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("archived", "Archived"),
            ("processing", "Processing"),
        ],
        default="active",
    )
    paper_count = models.IntegerField(default=0)
    total_chunks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "research_projects"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.vector_collection_name:
            self.vector_collection_name = f"project_{self.id.hex[:12]}"
        super().save(*args, **kwargs)


class ProjectCollaborator(models.Model):
    """Collaboration permissions for a project."""

    ROLE_CHOICES = [
        ("viewer", "Viewer"),
        ("editor", "Editor"),
        ("admin", "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        ResearchProject, on_delete=models.CASCADE, related_name="collaborators"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collaborations",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="viewer")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="invitations_sent",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_collaborators"
        unique_together = ["project", "user"]

    def __str__(self):
        return f"{self.user.username} -> {self.project.name} ({self.role})"
