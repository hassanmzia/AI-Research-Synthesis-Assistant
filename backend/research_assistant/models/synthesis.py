import uuid

from django.conf import settings
from django.db import models


class SynthesisReport(models.Model):
    """An AI-generated research synthesis report."""

    FORMAT_CHOICES = [
        ("markdown", "Markdown"),
        ("pdf", "PDF"),
        ("docx", "DOCX"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "ResearchProject", on_delete=models.CASCADE, related_name="synthesis_reports"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="synthesis_reports",
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    report_type = models.CharField(
        max_length=30,
        choices=[
            ("literature_review", "Literature Review"),
            ("comparative_analysis", "Comparative Analysis"),
            ("research_gap", "Research Gap Analysis"),
            ("methodology_review", "Methodology Review"),
            ("trend_analysis", "Trend Analysis"),
            ("executive_summary", "Executive Summary"),
        ],
        default="literature_review",
    )
    content_markdown = models.TextField(blank=True, default="")
    papers_included = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    output_format = models.CharField(
        max_length=10, choices=FORMAT_CHOICES, default="markdown"
    )
    file = models.FileField(upload_to="reports/%Y/%m/", blank=True, null=True)
    total_tokens_used = models.IntegerField(default=0)
    generation_time_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "synthesis_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SynthesisSection(models.Model):
    """A section within a synthesis report."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        SynthesisReport, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=500)
    content = models.TextField()
    order = models.IntegerField(default=0)
    source_papers = models.JSONField(default=list)
    citations = models.JSONField(default=list)

    class Meta:
        db_table = "synthesis_sections"
        ordering = ["order"]

    def __str__(self):
        return f"{self.report.title} - {self.title}"
