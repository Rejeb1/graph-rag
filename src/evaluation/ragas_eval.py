"""Ragas-based evaluation: faithfulness and context precision.

Uses Groq's small model (via litellm, free) as the evaluator LLM — see the
comment in run_ragas() for why small rather than large. Both metrics are
pure LLM-judgment metrics — no embeddings needed. (answer_relevancy was
dropped: it requires both an `embed_query()` method our embeddings wrapper
doesn't expose and 3 generations per call, which Groq/litellm only returns
1 of — neither is a transient issue, it's a real incompatibility with this
setup.)
"""

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

from src.config import SMALL_MODEL


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
    # Route through plain litellm.completion — a prior attempt wrapped this
    # in a custom retry function to work around litellm's own num_retries
    # not engaging, but that only covers calls Ragas makes directly; some of
    # its internal calls go through `instructor` instead, bypassing any
    # wrapper passed as `client`. The actually-effective retry axis is
    # RunConfig below, which Ragas's own tenacity-based retry decorator
    # wraps around *every* internal call path, instructor included.
    evaluator_llm = llm_factory(
        # SMALL_MODEL, not LARGE_MODEL: Groq's daily token budget is tracked
        # per model, and the large model's has been repeatedly exhausted by
        # this benchmark's own volume of verification calls. The small
        # model's daily budget is separate and untouched. This only affects
        # the Ragas evaluator — the app's real generation/judge calls still
        # use LARGE_MODEL, unchanged.
        f"groq/{SMALL_MODEL}",
        provider="litellm",
        client=litellm.completion,
        max_tokens=4096,  # default was too small, truncating verification output mid-generation (IncompleteOutputException)
    )

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, context_precision],
        llm=evaluator_llm,
        run_config=RunConfig(
            # Ragas defaults to 16 concurrent workers, which bursts well
            # past Groq's free-tier tokens-per-minute limit before retries
            # get a chance to help. Low concurrency keeps usage spread out.
            max_workers=2,
            # Groq's error messages have asked for waits up to ~20s; the
            # 180s default total-job timeout doesn't leave room for several
            # such backoffs within one job before giving up.
            timeout=900,
            max_retries=8,
            max_wait=60,
        ),
    )
    return result.to_pandas().mean(numeric_only=True).to_dict()
