import uuid

from django.db import models


class ResearchPaper(models.Model):
    """A research paper uploaded to a project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "ResearchProject", on_delete=models.CASCADE, related_name="papers"
    )
    title = models.CharField(max_length=500)
    authors = models.JSONField(default=list, blank=True)
    abstract = models.TextField(blank=True, default="")
    publication_date = models.DateField(null=True, blank=True)
    journal = models.CharField(max_length=500, blank=True, default="")
    doi = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField(upload_to="papers/%Y/%m/")
    file_name = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    page_count = models.IntegerField(default=0)
    chunk_count = models.IntegerField(default=0)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    processing_error = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "research_papers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PaperChunk(models.Model):
    """A text chunk from a research paper, stored for reference."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paper = models.ForeignKey(
        ResearchPaper, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_index = models.IntegerField()
    content = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    token_count = models.IntegerField(default=0)
    embedding_id = models.CharField(
        max_length=255, blank=True, default="",
        help_text="ID in the ChromaDB vector store",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "paper_chunks"
        ordering = ["paper", "chunk_index"]
        unique_together = ["paper", "chunk_index"]

    def __str__(self):
        return f"{self.paper.title} - Chunk {self.chunk_index}"
