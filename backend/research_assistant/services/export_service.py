"""Export service for generating various output formats."""
import csv
import io
import json
import logging
import os
import re
import tempfile

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

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
        elif fmt == "pdf":
            return self._generate_pdf_report(report)
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

    def _generate_pdf_report(self, report) -> str:
        """Generate a PDF from a synthesis report."""
        export_dir = os.path.join(settings.MEDIA_ROOT, "exports")
        os.makedirs(export_dir, exist_ok=True)

        fd, path = tempfile.mkstemp(suffix=".pdf", prefix="report_", dir=export_dir)
        os.close(fd)

        doc = SimpleDocTemplate(
            path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor("#1a1a2e"),
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor("#16213e"),
        )
        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            spaceAfter=10,
        )

        story = []

        # Title
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Report type badge
        report_type_text = f"<b>Report Type:</b> {report.report_type.replace('_', ' ').title()}"
        story.append(Paragraph(report_type_text, body_style))
        story.append(Spacer(1, 0.3 * inch))

        # Convert markdown content to PDF paragraphs
        content = report.content_markdown or ""
        self._parse_markdown_to_pdf(content, story, heading_style, body_style)

        # Add sections if available
        sections = report.sections.all()
        for section in sections:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(section.title, heading_style))
            self._parse_markdown_to_pdf(
                section.content or "", story, heading_style, body_style
            )

        doc.build(story)
        return os.path.relpath(path, settings.MEDIA_ROOT)

    def _parse_markdown_to_pdf(self, content: str, story: list, heading_style, body_style):
        """Parse markdown content and add to PDF story."""
        lines = content.split("\n")
        current_paragraph = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                if current_paragraph:
                    text = " ".join(current_paragraph)
                    text = self._escape_html(text)
                    story.append(Paragraph(text, body_style))
                    current_paragraph = []
                continue

            # Headings
            if stripped.startswith("### "):
                if current_paragraph:
                    text = " ".join(current_paragraph)
                    text = self._escape_html(text)
                    story.append(Paragraph(text, body_style))
                    current_paragraph = []
                heading_text = self._escape_html(stripped[4:])
                story.append(Paragraph(heading_text, heading_style))
            elif stripped.startswith("## "):
                if current_paragraph:
                    text = " ".join(current_paragraph)
                    text = self._escape_html(text)
                    story.append(Paragraph(text, body_style))
                    current_paragraph = []
                heading_text = self._escape_html(stripped[3:])
                story.append(Paragraph(heading_text, heading_style))
            elif stripped.startswith("# "):
                if current_paragraph:
                    text = " ".join(current_paragraph)
                    text = self._escape_html(text)
                    story.append(Paragraph(text, body_style))
                    current_paragraph = []
                heading_text = self._escape_html(stripped[2:])
                story.append(Paragraph(heading_text, heading_style))
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if current_paragraph:
                    text = " ".join(current_paragraph)
                    text = self._escape_html(text)
                    story.append(Paragraph(text, body_style))
                    current_paragraph = []
                bullet_text = self._escape_html(stripped[2:])
                story.append(Paragraph(f"• {bullet_text}", body_style))
            else:
                # Apply inline formatting
                formatted = self._format_inline_markdown(stripped)
                current_paragraph.append(formatted)

        if current_paragraph:
            text = " ".join(current_paragraph)
            text = self._escape_html(text)
            story.append(Paragraph(text, body_style))

    def _format_inline_markdown(self, text: str) -> str:
        """Convert inline markdown to ReportLab markup."""
        # Bold: **text** or __text__
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
        # Italic: *text* or _text_
        text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
        text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
        return text

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab."""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        # Re-apply our formatting tags
        text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
        return text

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
