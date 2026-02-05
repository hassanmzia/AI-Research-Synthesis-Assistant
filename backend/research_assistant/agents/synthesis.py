"""Synthesis Agent - RAG-based answer generation using LLM."""
import logging
import time
from typing import Any

from django.conf import settings

from .base import BaseAgent

logger = logging.getLogger(__name__)

# System message matching the notebook's QnA system
QNA_SYSTEM_MESSAGE = """
You are an assistant whose work is to review the articles and provide the appropriate answers from the context.
User input will have the context required by you to answer user questions.
This context will begin with the token: ###Context.
The context contains references to specific portions of a document relevant to the user query.

User questions will begin with the token: ###Question.

Please answer only using the context provided in the input. Do not mention anything about the context in your final answer.

If the answer is not found in the context, respond "I don't know".
"""

QNA_USER_TEMPLATE = """
###Context
Here are some documents that are relevant to the question mentioned below.
{context}

###Question
{question}
"""


class SynthesisAgent(BaseAgent):
    name = "synthesis"
    description = "Generates comprehensive answers using RAG (Retrieval-Augmented Generation)"

    def get_capabilities(self) -> list[str]:
        return [
            "rag_qa",
            "contextual_answering",
            "research_synthesis",
            "multi_paper_analysis",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        question = kwargs.get("question")
        project_id = kwargs.get("project_id")
        conversation_id = kwargs.get("conversation_id")
        run_evaluation = kwargs.get("run_evaluation", True)

        if not question or not project_id:
            raise ValueError("question and project_id are required")

        self.log_start({
            "question": question,
            "project_id": str(project_id),
        })

        try:
            start_time = time.time()

            # Step 1: Retrieve context via RetrievalAgent (A2A)
            retrieval_result = self.send_a2a_message(
                "retrieval",
                {"query": question, "project_id": str(project_id)},
            )

            context = retrieval_result.get("context", "")
            sources = retrieval_result.get("sources", [])

            # Step 2: Generate answer using LLM (matching notebook RAG function)
            formatted_prompt = (
                f"[INST]{QNA_SYSTEM_MESSAGE}\n"
                f"user: {QNA_USER_TEMPLATE.format(context=context, question=question)}"
                f"[/INST]"
            )

            response = self.llm.invoke(formatted_prompt)
            answer = response.content

            # Calculate token usage
            prompt_tokens = response.response_metadata.get(
                "token_usage", {}
            ).get("prompt_tokens", 0)
            completion_tokens = response.response_metadata.get(
                "token_usage", {}
            ).get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens

            latency_ms = int((time.time() - start_time) * 1000)

            # Step 3: Store query history
            from ..models import QueryHistory, ResearchProject

            project = ResearchProject.objects.get(id=project_id)
            query_record = QueryHistory.objects.create(
                user=self.user,
                project=project,
                question=question,
                answer=answer,
                context_chunks=[s.get("paper_id", "") for s in sources],
                model_used=settings.AI_DEFAULT_MODEL,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                agents_involved=["retrieval", "synthesis"],
            )

            # Step 4: Save as conversation message if applicable
            if conversation_id:
                from ..models import Conversation, Message

                conv = Conversation.objects.get(id=conversation_id)
                Message.objects.create(
                    conversation=conv,
                    role="assistant",
                    content=answer,
                    sources=[{
                        "paper_id": s.get("paper_id"),
                        "paper_title": s.get("paper_title"),
                        "page_number": s.get("page_number"),
                    } for s in sources],
                    agent_name=self.name,
                    token_count=total_tokens,
                    latency_ms=latency_ms,
                )
                conv.message_count = conv.messages.count()
                conv.save(update_fields=["message_count", "updated_at"])

            # Step 5: Optionally run evaluation via A2A
            evaluation_results = {}
            if run_evaluation:
                try:
                    evaluation_results = self.send_a2a_message(
                        "evaluation",
                        {
                            "query_id": str(query_record.id),
                            "question": question,
                            "answer": answer,
                            "context": context,
                        },
                    )
                except Exception as e:
                    logger.warning(f"Evaluation failed: {e}")

            result = {
                "answer": answer,
                "sources": sources,
                "query_id": str(query_record.id),
                "model": settings.AI_DEFAULT_MODEL,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens,
                },
                "latency_ms": latency_ms,
                "evaluation": evaluation_results,
            }

            self.log_complete(result, tokens_used=total_tokens)

            # Update user token usage
            if self.user:
                self.user.tokens_used_this_month += total_tokens
                self.user.save(update_fields=["tokens_used_this_month"])

            return result

        except Exception as e:
            self.log_error(str(e))
            raise
