"""Evaluation Agent - Groundedness and Relevance scoring (LLM-as-judge).

Implements the exact evaluation methodology from the notebook:
1. Groundedness: Checks if answer is derived from context
2. Relevance: Checks if answer addresses main aspects of question
"""
import json
import logging
import re
from typing import Any

from django.conf import settings
from langchain_openai import ChatOpenAI

from .base import BaseAgent

logger = logging.getLogger(__name__)

# Exact system messages from the notebook
GROUNDEDNESS_SYSTEM_MESSAGE = """
You are tasked with rating AI generated answers to questions posed by users.
You will be presented a question, context used by the AI system to generate the answer and an AI generated answer to the question.
In the input, the question will begin with ###Question, the context will begin with ###Context while the AI generated answer will begin with ###Answer.

Evaluation criteria:
The task is to judge the extent to which the metric is followed by the answer.
1 - The metric is not followed at all
2 - The metric is followed only to a limited extent
3 - The metric is followed to a good extent
4 - The metric is followed mostly
5 - The metric is followed completely

Metric:
The answer should be derived only from the information presented in the context

Instructions:
1. First write down the steps that are needed to evaluate the answer as per the metric.
2. Give a step-by-step explanation if the answer adheres to the metric considering the question and context as the input.
3. Next, evaluate the extent to which the metric is followed.
4. Use the previous information to rate the answer using the evaluaton criteria and assign a score.
"""

RELEVANCE_SYSTEM_MESSAGE = """
You are tasked with rating AI generated answers to questions posed by users.
You will be presented a question, context used by the AI system to generate the answer and an AI generated answer to the question.
In the input, the question will begin with ###Question, the context will begin with ###Context while the AI generated answer will begin with ###Answer.

Evaluation criteria:
The task is to judge the extent to which the metric is followed by the answer.
1 - The metric is not followed at all
2 - The metric is followed only to a limited extent
3 - The metric is followed to a good extent
4 - The metric is followed mostly
5 - The metric is followed completely

Metric:
Relevance measures how well the answer addresses the main aspects of the question, based on the context.
Consider whether all and only the important aspects are contained in the answer when evaluating relevance.

Instructions:
1. First write down the steps that are needed to evaluate the context as per the metric.
2. Give a step-by-step explanation if the context adheres to the metric considering the question as the input.
3. Next, evaluate the extent to which the metric is followed.
4. Use the previous information to rate the context using the evaluaton criteria and assign a score.
"""

COHERENCE_SYSTEM_MESSAGE = """
You are tasked with rating AI generated answers to questions posed by users.
You will be presented a question, context used by the AI system to generate the answer and an AI generated answer to the question.
In the input, the question will begin with ###Question, the context will begin with ###Context while the AI generated answer will begin with ###Answer.

Evaluation criteria:
The task is to judge the extent to which the metric is followed by the answer.
1 - The metric is not followed at all
2 - The metric is followed only to a limited extent
3 - The metric is followed to a good extent
4 - The metric is followed mostly
5 - The metric is followed completely

Metric:
Coherence measures how logically consistent and well-structured the answer is.
The answer should flow naturally, be free of contradictions, and present information in an organized manner.

Instructions:
1. First write down the steps that are needed to evaluate the answer as per the metric.
2. Give a step-by-step explanation if the answer adheres to the metric.
3. Next, evaluate the extent to which the metric is followed.
4. Use the previous information to rate the answer using the evaluation criteria and assign a score.
"""

COMPLETENESS_SYSTEM_MESSAGE = """
You are tasked with rating AI generated answers to questions posed by users.
You will be presented a question, context used by the AI system to generate the answer and an AI generated answer to the question.
In the input, the question will begin with ###Question, the context will begin with ###Context while the AI generated answer will begin with ###Answer.

Evaluation criteria:
The task is to judge the extent to which the metric is followed by the answer.
1 - The metric is not followed at all
2 - The metric is followed only to a limited extent
3 - The metric is followed to a good extent
4 - The metric is followed mostly
5 - The metric is followed completely

Metric:
Completeness measures whether the answer thoroughly covers all relevant aspects of the question using the available context.
Consider if any important information from the context that addresses the question has been left out.

Instructions:
1. First write down the steps needed to evaluate completeness.
2. Give a step-by-step explanation of whether all important aspects are covered.
3. Next, evaluate the extent to which the metric is followed.
4. Assign a score based on the evaluation criteria.
"""

FAITHFULNESS_SYSTEM_MESSAGE = """
You are tasked with rating AI generated answers to questions posed by users.
You will be presented a question, context used by the AI system to generate the answer and an AI generated answer to the question.
In the input, the question will begin with ###Question, the context will begin with ###Context while the AI generated answer will begin with ###Answer.

Evaluation criteria:
The task is to judge the extent to which the metric is followed by the answer.
1 - The metric is not followed at all
2 - The metric is followed only to a limited extent
3 - The metric is followed to a good extent
4 - The metric is followed mostly
5 - The metric is followed completely

Metric:
Faithfulness measures whether the answer avoids introducing claims not supported by the provided context.
Check if any statements in the answer are hallucinated or fabricated beyond what the context provides.

Instructions:
1. First write down the steps needed to evaluate faithfulness.
2. Give a step-by-step explanation checking each claim against the context.
3. Next, evaluate the extent to which the metric is followed.
4. Assign a score based on the evaluation criteria.
"""

EVAL_MESSAGES = {
    "groundedness": GROUNDEDNESS_SYSTEM_MESSAGE,
    "relevance": RELEVANCE_SYSTEM_MESSAGE,
    "coherence": COHERENCE_SYSTEM_MESSAGE,
    "completeness": COMPLETENESS_SYSTEM_MESSAGE,
    "faithfulness": FAITHFULNESS_SYSTEM_MESSAGE,
}

USER_MESSAGE_TEMPLATE = """
###Question
{question}

###Context
{context}

###Answer
{answer}
"""


class EvaluationAgent(BaseAgent):
    name = "evaluation"
    description = "Evaluates RAG responses using LLM-as-a-judge methodology for groundedness, relevance, coherence, completeness, and faithfulness"

    def get_capabilities(self) -> list[str]:
        return [
            "groundedness_evaluation",
            "relevance_evaluation",
            "coherence_evaluation",
            "completeness_evaluation",
            "faithfulness_evaluation",
            "composite_scoring",
        ]

    def execute(self, **kwargs) -> dict[str, Any]:
        query_id = kwargs.get("query_id")
        question = kwargs.get("question")
        answer = kwargs.get("answer")
        context = kwargs.get("context")
        eval_types = kwargs.get("eval_types", ["groundedness", "relevance"])

        if not all([question, answer, context]):
            raise ValueError("question, answer, and context are required")

        self.log_start({
            "query_id": str(query_id) if query_id else None,
            "eval_types": eval_types,
        })

        try:
            evaluator_llm = ChatOpenAI(
                model=settings.AI_DEFAULT_MODEL,
                temperature=0,
                max_tokens=500,
                top_p=0.95,
                frequency_penalty=1.2,
                api_key=self.api_key,
                base_url=settings.OPENAI_BASE_URL,
            )

            user_message = USER_MESSAGE_TEMPLATE.format(
                question=question,
                context=context[:4000],  # Limit context length
                answer=answer,
            )

            results = {}
            total_tokens = 0

            for eval_type in eval_types:
                if eval_type not in EVAL_MESSAGES:
                    continue

                system_message = EVAL_MESSAGES[eval_type]
                prompt = f"[INST]{system_message}\nuser: {user_message}[/INST]"

                response = evaluator_llm.invoke(prompt)
                explanation = response.content

                # Extract score from response
                score = self._extract_score(explanation)

                tokens = response.response_metadata.get(
                    "token_usage", {}
                ).get("total_tokens", 0)
                total_tokens += tokens

                # Save evaluation to database
                if query_id:
                    from ..models import QueryEvaluation, QueryHistory

                    try:
                        query = QueryHistory.objects.get(id=query_id)
                        QueryEvaluation.objects.create(
                            query=query,
                            eval_type=eval_type,
                            score=score,
                            explanation=explanation,
                            evaluator_model=settings.AI_DEFAULT_MODEL,
                        )
                    except QueryHistory.DoesNotExist:
                        pass

                results[eval_type] = {
                    "score": score,
                    "explanation": explanation,
                }

            # Compute composite score
            scores = [r["score"] for r in results.values() if r["score"] > 0]
            composite_score = sum(scores) / len(scores) if scores else 0

            output = {
                "evaluations": results,
                "composite_score": round(composite_score, 2),
                "total_tokens": total_tokens,
            }

            self.log_complete(output, tokens_used=total_tokens)
            return output

        except Exception as e:
            self.log_error(str(e))
            raise

    def _extract_score(self, text: str) -> int:
        """Extract numeric score from evaluation response."""
        # Look for patterns like "score of 5", "Score: 5", "**5**", "rating: 5"
        patterns = [
            r"score[:\s]*\**(\d)\**",
            r"rating[:\s]*\**(\d)\**",
            r"\*\*(\d)\*\*",
            r"assign a score[:\s]*\**(\d)\**",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                score = int(match.group(1))
                if 1 <= score <= 5:
                    return score
        return 3  # Default middle score if extraction fails
