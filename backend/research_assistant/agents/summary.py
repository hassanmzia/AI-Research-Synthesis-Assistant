"""Summary Agent - Generates paper summaries, abstracts, and synthesis reports."""
import logging
import time
from typing import Any

from django.conf import settings

from .base import BaseAgent

logger = logging.getLogger(__name__)


class SummaryAgent(BaseAgent):
    name = "summary"
    description = "Generates paper summaries, research synthesis reports, and comparative analyses"

    def get_capabilities(self) -> list[str]:
        return [
            "paper_summary",
            "literature_review",
            "comparative_analysis",
            "research_gap_analysis",
            "trend_analysis",
            "executive_summary",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        task_type = kwargs.get("task_type", "paper_summary")
        paper_id = kwargs.get("paper_id")
        project_id = kwargs.get("project_id")
        report_id = kwargs.get("report_id")

        self.log_start({
            "task_type": task_type,
            "paper_id": str(paper_id) if paper_id else None,
            "project_id": str(project_id) if project_id else None,
        })

        try:
            if task_type == "paper_summary":
                return self._generate_paper_summary(paper_id)
            elif task_type in (
                "literature_review",
                "comparative_analysis",
                "research_gap",
                "trend_analysis",
                "executive_summary",
            ):
                return self._generate_synthesis_report(
                    project_id, task_type, report_id
                )
            else:
                raise ValueError(f"Unknown task_type: {task_type}")

        except Exception as e:
            self.log_error(str(e))
            raise

    def _generate_paper_summary(self, paper_id: str) -> dict:
        """Generate a concise summary of a single paper."""
        from ..models import PaperChunk, ResearchPaper

        paper = ResearchPaper.objects.get(id=paper_id)
        chunks = PaperChunk.objects.filter(paper=paper).order_by("chunk_index")

        # Get representative chunks (beginning, middle, end)
        total = chunks.count()
        if total <= 6:
            selected = list(chunks)
        else:
            indices = [0, 1, total // 4, total // 2, 3 * total // 4, total - 1]
            selected = [chunks[i] for i in indices]

        text = "\n---\n".join(c.content for c in selected)

        prompt = f"""Based on the following excerpts from the research paper "{paper.title}",
generate a comprehensive summary including:
1. **Objective**: What is the main research question or goal?
2. **Methodology**: What methods or approaches were used?
3. **Key Findings**: What are the main results?
4. **Contributions**: What are the paper's key contributions to the field?
5. **Limitations**: Any noted limitations?
6. **Future Work**: Suggested future research directions?

Paper Excerpts:
{text[:4000]}

Provide a structured summary in markdown format."""

        response = self.llm.invoke(prompt)
        summary = response.content

        tokens = response.response_metadata.get(
            "token_usage", {}
        ).get("total_tokens", 0)

        paper.abstract = summary[:2000] if not paper.abstract else paper.abstract
        paper.save(update_fields=["abstract"])

        result = {
            "paper_id": str(paper_id),
            "title": paper.title,
            "summary": summary,
            "tokens_used": tokens,
        }
        self.log_complete(result, tokens_used=tokens)
        return result

    def _generate_synthesis_report(
        self, project_id: str, report_type: str, report_id: str | None = None
    ) -> dict:
        """Generate a multi-paper synthesis report."""
        from ..models import (
            PaperChunk,
            ResearchPaper,
            ResearchProject,
            SynthesisReport,
            SynthesisSection,
        )

        project = ResearchProject.objects.get(id=project_id)
        papers = ResearchPaper.objects.filter(
            project=project, processing_status="completed"
        )

        if report_id:
            report = SynthesisReport.objects.get(id=report_id)
        else:
            report = SynthesisReport.objects.create(
                project=project,
                user=self.user,
                title=f"{report_type.replace('_', ' ').title()} - {project.name}",
                report_type=report_type,
                status="generating",
                papers_included=[str(p.id) for p in papers],
            )

        report.status = "generating"
        report.save(update_fields=["status"])

        start_time = time.time()
        total_tokens = 0

        try:
            # Gather paper summaries for context
            paper_contexts = []
            for paper in papers[:10]:  # Limit to 10 papers
                chunks = PaperChunk.objects.filter(paper=paper).order_by(
                    "chunk_index"
                )[:3]
                text = "\n".join(c.content for c in chunks)
                paper_contexts.append(
                    f"**{paper.title}**\n"
                    f"Authors: {', '.join(paper.authors) if paper.authors else 'N/A'}\n"
                    f"Excerpt: {text[:800]}"
                )

            combined_context = "\n\n---\n\n".join(paper_contexts)

            # Generate report sections based on type
            sections_config = self._get_sections_config(report_type)

            all_content = []
            for i, section_cfg in enumerate(sections_config):
                section_prompt = f"""You are writing a {report_type.replace('_', ' ')} report.
Based on the following research papers, write the "{section_cfg['title']}" section.

{section_cfg['instructions']}

Papers:
{combined_context[:3000]}

Write in academic markdown format. Be thorough and cite specific papers by title."""

                resp = self.llm.invoke(section_prompt)
                section_content = resp.content

                tokens = resp.response_metadata.get(
                    "token_usage", {}
                ).get("total_tokens", 0)
                total_tokens += tokens

                SynthesisSection.objects.create(
                    report=report,
                    title=section_cfg["title"],
                    content=section_content,
                    order=i,
                    source_papers=[str(p.id) for p in papers],
                )
                all_content.append(f"## {section_cfg['title']}\n\n{section_content}")

            # Combine into full report
            report.content_markdown = (
                f"# {report.title}\n\n" + "\n\n".join(all_content)
            )
            report.status = "completed"
            report.total_tokens_used = total_tokens
            report.generation_time_ms = int((time.time() - start_time) * 1000)
            report.save()

            result = {
                "report_id": str(report.id),
                "title": report.title,
                "sections": len(sections_config),
                "tokens_used": total_tokens,
                "status": "completed",
            }
            self.log_complete(result, tokens_used=total_tokens)
            return result

        except Exception as e:
            report.status = "failed"
            report.save(update_fields=["status"])
            raise

    def _get_sections_config(self, report_type: str) -> list[dict]:
        """Get section configuration based on report type."""
        configs = {
            "literature_review": [
                {
                    "title": "Introduction",
                    "instructions": "Write an introduction covering the research landscape and key themes.",
                },
                {
                    "title": "Thematic Analysis",
                    "instructions": "Identify and discuss the major themes across the papers.",
                },
                {
                    "title": "Methodological Overview",
                    "instructions": "Compare and contrast the methodologies used.",
                },
                {
                    "title": "Key Findings",
                    "instructions": "Synthesize the key findings across all papers.",
                },
                {
                    "title": "Discussion & Gaps",
                    "instructions": "Discuss implications and identify research gaps.",
                },
                {
                    "title": "Conclusion",
                    "instructions": "Summarize the literature review and suggest future directions.",
                },
            ],
            "comparative_analysis": [
                {
                    "title": "Overview",
                    "instructions": "Provide a high-level overview of the papers being compared.",
                },
                {
                    "title": "Comparison Matrix",
                    "instructions": "Create a detailed comparison of approaches, methods, and findings using a table format.",
                },
                {
                    "title": "Strengths & Weaknesses",
                    "instructions": "Analyze strengths and weaknesses of each approach.",
                },
                {
                    "title": "Synthesis",
                    "instructions": "Synthesize insights from the comparison.",
                },
            ],
            "research_gap": [
                {
                    "title": "Current State of Research",
                    "instructions": "Describe the current state based on the papers.",
                },
                {
                    "title": "Identified Gaps",
                    "instructions": "Identify and describe specific research gaps.",
                },
                {
                    "title": "Opportunities",
                    "instructions": "Suggest research opportunities to address the gaps.",
                },
            ],
            "trend_analysis": [
                {
                    "title": "Historical Context",
                    "instructions": "Describe the historical evolution of the research area.",
                },
                {
                    "title": "Current Trends",
                    "instructions": "Identify and analyze current research trends.",
                },
                {
                    "title": "Emerging Directions",
                    "instructions": "Discuss emerging research directions and predictions.",
                },
            ],
            "executive_summary": [
                {
                    "title": "Executive Summary",
                    "instructions": "Write a comprehensive executive summary covering all key points, findings, and recommendations.",
                },
            ],
        }
        return configs.get(report_type, configs["literature_review"])
