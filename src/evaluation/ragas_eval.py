"""Ragas-based evaluation: faithfulness, answer relevancy, context precision.

Uses Groq (via litellm, free) as the evaluator LLM and a local
sentence-transformers model as the evaluator embeddings (via
ragas.embeddings.HuggingFaceEmbeddings, use_api=False) — nothing here
requires a paid API key.
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
from ragas.embeddings import HuggingFaceEmbeddings
from ragas.llms import llm_factory
# NB: this path is deprecated in favor of ragas.metrics.collections (class-based
# metrics with a different construction contract) but is confirmed working
# against ragas 0.4.3's evaluate(); re-check on upgrade.
from ragas.metrics import answer_relevancy, context_precision, faithfulness

from src.config import EMBEDDING_MODEL, LARGE_MODEL


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
    # litellm reads GROQ_API_KEY from the environment itself; no client object needed.
    evaluator_llm = llm_factory(f"groq/{LARGE_MODEL}", provider="litellm", client=litellm.completion)
    evaluator_embeddings = HuggingFaceEmbeddings(model=EMBEDDING_MODEL, use_api=False)

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )
    return result.to_pandas().mean(numeric_only=True).to_dict()
