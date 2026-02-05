"""Ingestion Agent - Handles PDF upload, text extraction, and chunking."""
import logging
import os
from typing import Any

import tiktoken
from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from .base import BaseAgent

logger = logging.getLogger(__name__)


class IngestionAgent(BaseAgent):
    name = "ingestion"
    description = "Handles PDF document loading, text extraction, and text chunking"

    def get_capabilities(self) -> list[str]:
        return [
            "pdf_extraction",
            "text_chunking",
            "metadata_extraction",
            "tiktoken_encoding",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        paper_id = kwargs.get("paper_id")
        if not paper_id:
            raise ValueError("paper_id is required")

        from ..models import PaperChunk, ResearchPaper

        paper = ResearchPaper.objects.get(id=paper_id)
        self.log_start({"paper_id": str(paper_id), "file_name": paper.file_name})

        try:
            paper.processing_status = "processing"
            paper.save(update_fields=["processing_status"])

            # Load PDF
            file_path = paper.file.path
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            paper.page_count = len(pages)

            # Create text splitter (matching notebook config)
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                encoding_name=settings.RAG_ENCODING_NAME,
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            )

            # Split documents into chunks
            chunks = text_splitter.split_documents(pages)

            # Count tokens per chunk
            encoding = tiktoken.get_encoding(settings.RAG_ENCODING_NAME)

            # Store chunks in database
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                token_count = len(encoding.encode(chunk.page_content))
                chunk_objects.append(
                    PaperChunk(
                        paper=paper,
                        chunk_index=i,
                        content=chunk.page_content,
                        page_number=chunk.metadata.get("page"),
                        token_count=token_count,
                        metadata=chunk.metadata,
                    )
                )

            PaperChunk.objects.bulk_create(chunk_objects)

            paper.chunk_count = len(chunks)
            paper.processing_status = "completed"

            # Extract metadata
            if pages:
                first_page = pages[0].page_content[:2000]
                metadata = self._extract_metadata(first_page, paper.file_name)
                if metadata.get("title") and not paper.title:
                    paper.title = metadata["title"]
                if metadata.get("authors"):
                    paper.authors = metadata["authors"]
                if metadata.get("abstract"):
                    paper.abstract = metadata["abstract"]

            paper.save()

            # Update project counts
            project = paper.project
            project.paper_count = project.papers.filter(
                processing_status="completed"
            ).count()
            project.total_chunks = sum(
                p.chunk_count
                for p in project.papers.filter(processing_status="completed")
            )
            project.save(update_fields=["paper_count", "total_chunks"])

            result = {
                "paper_id": str(paper.id),
                "pages": paper.page_count,
                "chunks": paper.chunk_count,
                "status": "completed",
            }
            self.log_complete(result)

            # Delegate to EmbeddingAgent via A2A
            self.send_a2a_message(
                "embedding",
                {
                    "paper_id": str(paper.id),
                    "project_id": str(paper.project_id),
                },
            )

            return result

        except Exception as e:
            paper.processing_status = "failed"
            paper.processing_error = str(e)
            paper.save(update_fields=["processing_status", "processing_error"])
            self.log_error(str(e))
            raise

    def _extract_metadata(self, first_page_text: str, file_name: str) -> dict:
        """Use LLM to extract paper metadata from first page."""
        try:
            prompt = f"""Extract metadata from this research paper's first page.
Return a JSON object with keys: title, authors (as a list), abstract.
If any field cannot be determined, use null.

Text:
{first_page_text[:1500]}

Return ONLY valid JSON, no other text."""

            response = self.llm.invoke(prompt)
            import json

            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            name = os.path.splitext(file_name)[0]
            return {"title": name, "authors": [], "abstract": ""}
