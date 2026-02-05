"""Retrieval Agent - Handles similarity search and context retrieval."""
import logging
from typing import Any

from django.conf import settings

from .base import BaseAgent

logger = logging.getLogger(__name__)


class RetrievalAgent(BaseAgent):
    name = "retrieval"
    description = "Performs similarity search and retrieves relevant context from the vector store"

    def get_capabilities(self) -> list[str]:
        return [
            "similarity_search",
            "context_retrieval",
            "multi_query_retrieval",
            "filtered_search",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        query = kwargs.get("query")
        project_id = kwargs.get("project_id")
        k = kwargs.get("k", settings.RAG_RETRIEVER_K)
        filters = kwargs.get("filters", {})

        if not query or not project_id:
            raise ValueError("query and project_id are required")

        from ..models import ResearchProject

        project = ResearchProject.objects.get(id=project_id)

        self.log_start({
            "query": query,
            "project_id": str(project_id),
            "k": k,
        })

        try:
            # Use EmbeddingAgent for search via A2A
            from .embedding import EmbeddingAgent

            embedding_agent = EmbeddingAgent(user=self.user, api_key=self.api_key)
            results = embedding_agent.search_similar(
                collection_name=project.vector_collection_name,
                query=query,
                k=k,
            )

            # Format context
            context_list = [r["content"] for r in results]
            context = ". ".join(context_list)

            # Build source references
            sources = []
            seen_papers = set()
            for r in results:
                paper_id = r["metadata"].get("paper_id", "")
                if paper_id and paper_id not in seen_papers:
                    seen_papers.add(paper_id)
                    sources.append({
                        "paper_id": paper_id,
                        "paper_title": r["metadata"].get("paper_title", ""),
                        "page_number": r["metadata"].get("page_number"),
                        "chunk_index": r["metadata"].get("chunk_index"),
                        "relevance_score": 1 - r.get("distance", 0),
                    })

            result = {
                "query": query,
                "context": context,
                "chunks": results,
                "sources": sources,
                "num_results": len(results),
            }

            self.log_complete(result)
            return result

        except Exception as e:
            self.log_error(str(e))
            raise

    def multi_query_retrieve(
        self, queries: list[str], project_id: str, k: int = 5
    ) -> dict[str, Any]:
        """Retrieve context for multiple queries and merge results."""
        all_chunks = []
        seen_ids = set()

        for query in queries:
            result = self.execute(query=query, project_id=project_id, k=k)
            for chunk in result["chunks"]:
                chunk_id = chunk.get("id", "")
                if chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    all_chunks.append(chunk)

        # Sort by distance (most relevant first)
        all_chunks.sort(key=lambda x: x.get("distance", 1))

        context_list = [c["content"] for c in all_chunks[:k * 2]]
        return {
            "context": ". ".join(context_list),
            "chunks": all_chunks[:k * 2],
            "queries_used": queries,
        }
