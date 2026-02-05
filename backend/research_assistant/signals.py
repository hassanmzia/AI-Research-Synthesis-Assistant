"""Django signals for the Research Assistant app."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ResearchPaper

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ResearchPaper)
def trigger_paper_processing(sender, instance, created, **kwargs):
    """When a new paper is uploaded, trigger async processing."""
    if created and instance.processing_status == "pending":
        from .tasks import process_paper_task

        process_paper_task.delay(str(instance.id))
        logger.info(f"Triggered processing for paper: {instance.title}")
