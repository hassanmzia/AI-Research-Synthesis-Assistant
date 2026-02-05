"""Celery tasks for async processing."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_paper_task(self, paper_id: str):
    """Process a newly uploaded paper: extract text, chunk, embed."""
    from .agents import IngestionAgent
    from .models import ResearchPaper

    try:
        paper = ResearchPaper.objects.get(id=paper_id)
        agent = IngestionAgent()
        result = agent.execute(paper_id=paper_id)
        logger.info(f"Paper processed successfully: {paper.title}")
        return result
    except Exception as exc:
        logger.exception(f"Paper processing failed for {paper_id}")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def generate_synthesis_report_task(
    self, user_id: str, project_id: str, report_type: str
):
    """Generate a synthesis report asynchronously."""
    from .agents import SummaryAgent
    from .models import User

    try:
        user = User.objects.get(id=user_id)
        agent = SummaryAgent(user=user)
        result = agent.execute(
            task_type=report_type,
            project_id=project_id,
        )
        logger.info(f"Report generated: {result.get('report_id')}")
        return result
    except Exception as exc:
        logger.exception(f"Report generation failed")
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def process_export_task(self, export_id: str):
    """Process an export job."""
    from django.utils import timezone

    from .models import ExportJob
    from .services.export_service import ExportService

    try:
        export = ExportJob.objects.get(id=export_id)
        export.status = "processing"
        export.save(update_fields=["status"])

        service = ExportService()
        file_path = service.generate_export(export)

        export.status = "completed"
        export.file = file_path
        export.completed_at = timezone.now()
        export.save()

        logger.info(f"Export completed: {export_id}")
    except Exception as exc:
        ExportJob.objects.filter(id=export_id).update(
            status="failed", error_message=str(exc)
        )
        logger.exception(f"Export failed: {export_id}")
        self.retry(exc=exc)


@shared_task
def reset_monthly_token_usage():
    """Reset token usage counters on the first of each month."""
    from .models import User

    User.objects.all().update(tokens_used_this_month=0)
    logger.info("Monthly token usage counters reset")


@shared_task
def cleanup_old_export_files():
    """Delete export files older than 7 days."""
    import datetime

    from django.utils import timezone

    from .models import ExportJob

    cutoff = timezone.now() - datetime.timedelta(days=7)
    old_exports = ExportJob.objects.filter(
        created_at__lt=cutoff, status="completed"
    )
    count = old_exports.count()
    for export in old_exports:
        if export.file:
            export.file.delete()
    old_exports.delete()
    logger.info(f"Cleaned up {count} old export files")
