"""Export service for generating various output formats."""
import csv
import io
import json
import logging
import os
import tempfile

from django.conf import settings

logger = logging.getLogger(__name__)


class ExportService:
    """Handles export generation for various data types and formats."""

    def generate_export(self, export_job) -> str:
        """Generate an export file based on job configuration."""
        export_type = export_job.export_type
        output_format = export_job.output_format
        params = export_job.parameters

        if export_type == "query_history":
            return self._export_query_history(export_job.user, output_format, params)
        elif export_type == "synthesis_report":
            return self._export_synthesis_report(output_format, params)
        elif export_type == "paper_citations":
            return self._export_citations(output_format, params)
        elif export_type == "analytics_data":
            return self._export_analytics(export_job.user, output_format)
        elif export_type == "conversation":
            return self._export_conversation(output_format, params)
        else:
            raise ValueError(f"Unknown export type: {export_type}")

    def _export_query_history(self, user, fmt, params):
        from ..models import QueryHistory

        queries = QueryHistory.objects.filter(user=user).order_by("-created_at")

        if params.get("project_id"):
            queries = queries.filter(project_id=params["project_id"])

        data = []
        for q in queries[:500]:
            data.append({
                "question": q.question,
                "answer": q.answer,
                "model": q.model_used,
                "tokens": q.total_tokens,
                "latency_ms": q.latency_ms,
                "created_at": str(q.created_at),
            })

        return self._write_output(data, fmt, "query_history")

    def _export_synthesis_report(self, fmt, params):
        from ..models import SynthesisReport

        report_id = params.get("report_id")
        if not report_id:
            raise ValueError("report_id is required")

        report = SynthesisReport.objects.get(id=report_id)

        if fmt == "markdown":
            return self._write_text(report.content_markdown, "report", "md")
        elif fmt == "json":
            data = {
                "title": report.title,
                "type": report.report_type,
                "content": report.content_markdown,
                "sections": [
                    {"title": s.title, "content": s.content}
                    for s in report.sections.all()
                ],
            }
            return self._write_text(json.dumps(data, indent=2), "report", "json")
        else:
            return self._write_text(report.content_markdown, "report", "md")

    def _export_citations(self, fmt, params):
        from ..agents import CitationAgent

        paper_id = params.get("paper_id")
        style = params.get("style", "apa")

        agent = CitationAgent()
        result = agent.execute(paper_id=paper_id, format_style=style)

        if fmt == "bibtex":
            entries = [c.get("formatted", "") for c in result.get("citations", [])
                       if style == "bibtex"]
            content = "\n\n".join(entries) if entries else ""
            return self._write_text(content, "citations", "bib")
        elif fmt == "json":
            return self._write_text(
                json.dumps(result.get("citations", []), indent=2),
                "citations", "json"
            )
        else:
            entries = [c.get("formatted", "") for c in result.get("citations", [])]
            return self._write_text("\n\n".join(entries), "citations", "txt")

    def _export_analytics(self, user, fmt):
        from ..models import AgentLog, QueryHistory

        data = {
            "total_queries": QueryHistory.objects.filter(user=user).count(),
            "queries": list(
                QueryHistory.objects.filter(user=user)
                .values("question", "total_tokens", "latency_ms", "created_at")[:100]
            ),
            "agent_logs": list(
                AgentLog.objects.filter(user=user)
                .values("agent_name", "status", "duration_ms", "tokens_used")[:100]
            ),
        }
        return self._write_text(
            json.dumps(data, indent=2, default=str), "analytics", "json"
        )

    def _export_conversation(self, fmt, params):
        from ..models import Conversation

        conv_id = params.get("conversation_id")
        conv = Conversation.objects.get(id=conv_id)
        messages = conv.messages.all()

        if fmt == "markdown":
            lines = [f"# {conv.title}\n"]
            for msg in messages:
                role = msg.role.upper()
                lines.append(f"## {role}\n{msg.content}\n")
            return self._write_text("\n".join(lines), "conversation", "md")
        elif fmt == "json":
            data = {
                "title": conv.title,
                "messages": [
                    {"role": m.role, "content": m.content, "created_at": str(m.created_at)}
                    for m in messages
                ],
            }
            return self._write_text(json.dumps(data, indent=2), "conversation", "json")
        else:
            lines = []
            for msg in messages:
                lines.append(f"[{msg.role}]: {msg.content}")
            return self._write_text("\n\n".join(lines), "conversation", "txt")

    def _write_output(self, data: list[dict], name: str, fmt: str) -> str:
        """Write list of dicts to file in the specified format."""
        if fmt == "csv":
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return self._save_file(output.getvalue(), name, "csv")
        elif fmt == "json":
            return self._write_text(json.dumps(data, indent=2, default=str), name, "json")
        else:
            return self._write_text(json.dumps(data, indent=2, default=str), name, "json")

    def _write_text(self, content: str, name: str, ext: str) -> str:
        return self._save_file(content, name, ext)

    def _save_file(self, content: str, name: str, ext: str) -> str:
        """Save content to a file in the media exports directory."""
        export_dir = os.path.join(settings.MEDIA_ROOT, "exports")
        os.makedirs(export_dir, exist_ok=True)

        fd, path = tempfile.mkstemp(
            suffix=f".{ext}", prefix=f"{name}_", dir=export_dir
        )
        with os.fdopen(fd, "w") as f:
            f.write(content)

        # Return relative path for Django FileField
        return os.path.relpath(path, settings.MEDIA_ROOT)
