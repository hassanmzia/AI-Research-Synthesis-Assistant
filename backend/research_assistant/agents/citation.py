"""Citation Agent - Extracts and formats citations and references."""
import json
import logging
from typing import Any

from .base import BaseAgent

logger = logging.getLogger(__name__)


class CitationAgent(BaseAgent):
    name = "citation"
    description = "Extracts and formats academic citations and references from research papers"

    def get_capabilities(self) -> list[str]:
        return [
            "citation_extraction",
            "reference_formatting",
            "bibtex_generation",
            "apa_formatting",
            "cross_reference_analysis",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        paper_id = kwargs.get("paper_id")
        text = kwargs.get("text")
        format_style = kwargs.get("format_style", "apa")

        self.log_start({
            "paper_id": str(paper_id) if paper_id else None,
            "format_style": format_style,
        })

        try:
            if paper_id:
                from ..models import PaperChunk, ResearchPaper

                paper = ResearchPaper.objects.get(id=paper_id)
                # Get last chunks which typically contain references
                chunks = PaperChunk.objects.filter(paper=paper).order_by(
                    "-chunk_index"
                )[:5]
                text = "\n".join(c.content for c in chunks)

            if not text:
                raise ValueError("No text provided for citation extraction")

            prompt = f"""Extract all academic citations/references from the following text.
Return a JSON array where each object has:
- "authors": list of author names
- "title": paper title
- "year": publication year
- "journal": journal/conference name
- "doi": DOI if available
- "volume": volume number if available
- "pages": page numbers if available

Text:
{text[:3000]}

Return ONLY valid JSON array, no other text."""

            response = self.llm.invoke(prompt)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]

            try:
                citations = json.loads(content)
            except json.JSONDecodeError:
                citations = []

            # Format citations
            formatted = []
            for cite in citations:
                formatted.append({
                    **cite,
                    "formatted": self._format_citation(cite, format_style),
                })

            result = {
                "citations": formatted,
                "count": len(formatted),
                "format_style": format_style,
            }

            tokens = response.response_metadata.get(
                "token_usage", {}
            ).get("total_tokens", 0)
            self.log_complete(result, tokens_used=tokens)
            return result

        except Exception as e:
            self.log_error(str(e))
            raise

    def _format_citation(self, citation: dict, style: str) -> str:
        """Format a single citation in the specified style."""
        authors = citation.get("authors", [])
        title = citation.get("title", "")
        year = citation.get("year", "")
        journal = citation.get("journal", "")

        if style == "apa":
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            return f"{author_str} ({year}). {title}. {journal}."

        elif style == "bibtex":
            key = (
                f"{authors[0].split()[-1].lower() if authors else 'unknown'}{year}"
            )
            return (
                f"@article{{{key},\n"
                f'  author = {{{" and ".join(authors)}}},\n'
                f"  title = {{{title}}},\n"
                f"  year = {{{year}}},\n"
                f"  journal = {{{journal}}}\n"
                f"}}"
            )

        elif style == "mla":
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += ", et al."
            return f'{author_str}. "{title}." {journal} ({year}).'

        return f"{', '.join(authors)} ({year}). {title}. {journal}."

    def generate_bibliography(self, paper_ids: list[str], style: str = "apa") -> str:
        """Generate a formatted bibliography for multiple papers."""
        from ..models import ResearchPaper

        papers = ResearchPaper.objects.filter(id__in=paper_ids)
        entries = []

        for paper in papers:
            cite = {
                "authors": paper.authors,
                "title": paper.title,
                "year": (
                    paper.publication_date.year if paper.publication_date else ""
                ),
                "journal": paper.journal,
            }
            entries.append(self._format_citation(cite, style))

        return "\n\n".join(sorted(entries))
