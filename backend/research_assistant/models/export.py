import uuid

from django.conf import settings
from django.db import models


class ExportJob(models.Model):
    """Track export jobs for reports and data."""

    FORMAT_CHOICES = [
        ("pdf", "PDF"),
        ("docx", "DOCX"),
        ("csv", "CSV"),
        ("xlsx", "Excel"),
        ("markdown", "Markdown"),
        ("json", "JSON"),
        ("bibtex", "BibTeX"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="export_jobs",
    )
    export_type = models.CharField(
        max_length=30,
        choices=[
            ("query_history", "Query History"),
            ("synthesis_report", "Synthesis Report"),
            ("paper_citations", "Paper Citations"),
            ("analytics_data", "Analytics Data"),
            ("conversation", "Conversation"),
        ],
    )
    output_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file = models.FileField(upload_to="exports/%Y/%m/", blank=True, null=True)
    error_message = models.TextField(blank=True, default="")
    parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "export_jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Export {self.export_type} ({self.output_format}) - {self.status}"
