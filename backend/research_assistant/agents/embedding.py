"""Embedding Agent - Creates and manages vector embeddings in ChromaDB."""
import logging
from typing import Any

import chromadb
from django.conf import settings
from langchain_openai import OpenAIEmbeddings

from .base import BaseAgent

logger = logging.getLogger(__name__)


class EmbeddingAgent(BaseAgent):
    name = "embedding"
    description = "Creates and manages vector embeddings in ChromaDB"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chroma_client = None
        self._embedding_model = None

    @property
    def chroma_client(self):
        if self._chroma_client is None:
            self._chroma_client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST,
                port=settings.CHROMADB_PORT,
            )
        return self._chroma_client

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = OpenAIEmbeddings(
                model=settings.AI_EMBEDDING_MODEL,
                api_key=self.api_key,
                base_url=settings.OPENAI_BASE_URL,
            )
        return self._embedding_model

    def get_capabilities(self) -> list[str]:
        return [
            "create_embeddings",
            "manage_collections",
            "batch_embedding",
            "similarity_search",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        paper_id = kwargs.get("paper_id")
        project_id = kwargs.get("project_id")
        if not paper_id or not project_id:
            raise ValueError("paper_id and project_id are required")

        from ..models import PaperChunk, ResearchPaper, ResearchProject

        paper = ResearchPaper.objects.get(id=paper_id)
        project = ResearchProject.objects.get(id=project_id)
        chunks = PaperChunk.objects.filter(paper=paper).order_by("chunk_index")

        self.log_start({
            "paper_id": str(paper_id),
            "project_id": str(project_id),
            "chunk_count": chunks.count(),
        })

        try:
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=project.vector_collection_name,
                metadata={"project_id": str(project_id)},
            )

            # Prepare batch data
            documents = []
            ids = []
            metadatas = []

            for chunk in chunks:
                doc_id = f"{paper_id}_{chunk.chunk_index}"
                documents.append(chunk.content)
                ids.append(doc_id)
                metadatas.append({
                    "paper_id": str(paper_id),
                    "paper_title": paper.title,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number or 0,
                    "source": paper.file_name,
                })

            # Batch embed and add to collection
            batch_size = 50
            total_embedded = 0

            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]
                batch_meta = metadatas[i : i + batch_size]

                embeddings = self.embedding_model.embed_documents(batch_docs)

                collection.add(
                    documents=batch_docs,
                    embeddings=embeddings,
                    ids=batch_ids,
                    metadatas=batch_meta,
                )
                total_embedded += len(batch_docs)

            # Update chunk embedding IDs
            for chunk in chunks:
                chunk.embedding_id = f"{paper_id}_{chunk.chunk_index}"
            PaperChunk.objects.bulk_update(chunks, ["embedding_id"])

            result = {
                "paper_id": str(paper_id),
                "collection": project.vector_collection_name,
                "chunks_embedded": total_embedded,
                "status": "completed",
            }
            self.log_complete(result)
            return result

        except Exception as e:
            self.log_error(str(e))
            raise

    def search_similar(
        self,
        collection_name: str,
        query: str,
        k: int | None = None,
    ) -> list[dict]:
        """Search for similar documents in a collection."""
        k = k or settings.RAG_RETRIEVER_K

        collection = self.chroma_client.get_collection(name=collection_name)
        query_embedding = self.embedding_model.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                    "id": results["ids"][0][i] if results["ids"] else "",
                })

        return documents

    def delete_paper_embeddings(self, collection_name: str, paper_id: str) -> None:
        """Delete all embeddings for a specific paper."""
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
            # Get all IDs for this paper
            results = collection.get(
                where={"paper_id": paper_id},
                include=[],
            )
            if results["ids"]:
                collection.delete(ids=results["ids"])
                logger.info(
                    f"Deleted {len(results['ids'])} embeddings for paper {paper_id}"
                )
        except Exception as e:
            logger.error(f"Failed to delete embeddings: {e}")
