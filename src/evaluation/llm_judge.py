"""LLM-as-judge: score a generated answer for correctness, relevance, and groundedness."""

import json

from groq import Groq

from src.config import LARGE_MODEL

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "correctness": {
            "type": "integer",
            "description": "1 (wrong) to 5 (fully correct), judged against the reference answer.",
        },
        "relevance": {"type": "integer", "description": "1 (off-topic) to 5 (directly answers the question)."},
        "grounded": {
            "type": "boolean",
            "description": "True only if every claim in the answer is supported by the provided context.",
        },
        "explanation": {"type": "string"},
    },
    "required": ["correctness", "relevance", "grounded", "explanation"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = "You are an impartial judge scoring a RAG system's answer. Score strictly and briefly justify your scores."


def judge(client: Groq, question: str, answer: str, context: str, reference: str = "") -> dict:
    user_content = (
        f"Question: {question}\n\n"
        f"Context provided to the system:\n{context}\n\n"
        f"System's answer:\n{answer}\n\n"
        f"Reference answer (if available): {reference or '(none provided)'}"
    )
    response = client.chat.completions.create(
        model=LARGE_MODEL,
        max_tokens=512,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "judge_scores", "strict": True, "schema": JUDGE_SCHEMA},
        },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return json.loads(response.choices[0].message.content)
