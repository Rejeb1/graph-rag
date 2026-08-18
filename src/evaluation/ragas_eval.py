"""Ragas-based evaluation: faithfulness and context precision.

Uses Groq (via litellm, free) as the evaluator LLM. Both metrics are pure
LLM-judgment metrics — no embeddings needed. (answer_relevancy was dropped:
it requires both an `embed_query()` method our embeddings wrapper doesn't
expose and 3 generations per call, which Groq/litellm only returns 1 of —
neither is a transient issue, it's a real incompatibility with this setup.)
"""

import functools
import sys
import types

# Workaround: ragas 0.4.3's ragas.llms.base unconditionally imports
# `langchain_community.chat_models.vertexai.ChatVertexAI`, but current
# langchain-community releases removed that submodule (moved to the
# separate langchain-google-vertexai package). We never use Vertex AI, so a
# stub with the right name is enough to satisfy the import. Remove this once
# ragas updates its langchain-community pin (upstream issue, not ours).
if "langchain_community.chat_models.vertexai" not in sys.modules:
    _vertexai_stub = types.ModuleType("langchain_community.chat_models.vertexai")

    class ChatVertexAI:  # pragma: no cover - unused stub
        pass

    _vertexai_stub.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _vertexai_stub

import litellm
from ragas import EvaluationDataset, evaluate
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import llm_factory
from ragas.run_config import RunConfig
# NB: this path is deprecated in favor of ragas.metrics.collections (class-based
# metrics with a different construction contract) but is confirmed working
# against ragas 0.4.3's evaluate(); re-check on upgrade.
from ragas.metrics import context_precision, faithfulness

from src.config import LARGE_MODEL


def build_dataset(records: list[dict]) -> EvaluationDataset:
    """`records`: [{"question", "answer", "contexts": [...], "reference"}, ...]"""
    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"],
            reference=r.get("reference", ""),
        )
        for r in records
    ]
    return EvaluationDataset(samples=samples)


def run_ragas(records: list[dict]) -> dict:
    dataset = build_dataset(records)
    # Ragas decomposes each question into several verification sub-calls,
    # which can burst past Groq's free-tier tokens-per-minute limit.
    # num_retries makes litellm wait out the "try again in Xs" window
    # instead of giving up after one attempt.
    groq_completion = functools.partial(litellm.completion, num_retries=5)
    evaluator_llm = llm_factory(f"groq/{LARGE_MODEL}", provider="litellm", client=groq_completion)

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, context_precision],
        llm=evaluator_llm,
        # Ragas defaults to 16 concurrent workers, which bursts well past
        # Groq's free-tier tokens-per-minute limit before num_retries above
        # gets a chance to help. Low concurrency keeps token usage spread
        # out enough to stay under the cap.
        run_config=RunConfig(max_workers=2),
    )
    return result.to_pandas().mean(numeric_only=True).to_dict()
