"""Compare pipeline configurations: graph on/off x routing on/off.

Runs the eval set (src/evaluation/dataset.py) through each configuration,
scores answers with Ragas + an LLM judge, and prints/saves a comparison
table — the cost/latency/quality tradeoff artifact this project is meant to
produce (the RouteLLM-style benchmark referenced in the ChapsVision posting).
"""

import csv
import json
import time
from pathlib import Path

from groq import Groq

from src.config import GROQ_API_KEY, ROOT_DIR
from src.evaluation.dataset import EVAL_SET
from src.evaluation.llm_judge import judge
from src.evaluation.ragas_eval import run_ragas
from src.generation.generator import generate_answer
from src.retrieval.pipeline import retrieve
from src.routing.router import route

CONFIGS = [
    {"name": "vector_only-large_only", "use_graph": False, "use_routing": False},
    {"name": "graph+vector-large_only", "use_graph": True, "use_routing": False},
    {"name": "vector_only-routed", "use_graph": False, "use_routing": True},
    {"name": "graph+vector-routed", "use_graph": True, "use_routing": True},
]


def run_config(client: Groq, config: dict) -> dict:
    records = []
    total_latency = 0.0
    tier_counts = {"small": 0, "large": 0}

    for item in EVAL_SET:
        question = item["question"]
        retrieval = retrieve(client, question, use_graph=config["use_graph"])
        decision = route(question, use_routing=config["use_routing"])
        tier_counts[decision.tier] += 1

        result = generate_answer(client, decision, question, retrieval["context"])
        total_latency += result.latency_seconds

        judged = judge(client, question, result.answer, retrieval["context"], item.get("reference", ""))

        records.append(
            {
                "question": question,
                "answer": result.answer,
                "contexts": [retrieval["context"]],
                "reference": item.get("reference", ""),
                "model": result.model,
                "tier": result.tier,
                "latency_seconds": result.latency_seconds,
                "judge": judged,
            }
        )

    ragas_scores = run_ragas(
        [
            {"question": r["question"], "answer": r["answer"], "contexts": r["contexts"], "reference": r["reference"]}
            for r in records
        ]
    )

    n = len(records)
    avg_correctness = sum(r["judge"]["correctness"] for r in records) / n
    avg_relevance = sum(r["judge"]["relevance"] for r in records) / n
    grounded_rate = sum(r["judge"]["grounded"] for r in records) / n

    return {
        "config": config["name"],
        "avg_latency_seconds": round(total_latency / n, 3),
        "tier_counts": tier_counts,
        "judge_avg_correctness": round(avg_correctness, 2),
        "judge_avg_relevance": round(avg_relevance, 2),
        "judge_grounded_rate": round(grounded_rate, 2),
        **{f"ragas_{k}": round(v, 3) for k, v in ragas_scores.items()},
        "records": records,
    }


def _print_table(results: list[dict]) -> None:
    headers = [
        "config",
        "avg_latency_seconds",
        "tier_counts",
        "judge_avg_correctness",
        "judge_avg_relevance",
        "judge_grounded_rate",
    ]
    headers += sorted(k for k in results[0] if k.startswith("ragas_"))
    print(" | ".join(headers))
    for r in results:
        print(" | ".join(str(r.get(h, "")) for h in headers))


def run_benchmark(save_dir: Path | None = None, pause_between_configs: float = 65.0) -> list[dict]:
    save_dir = save_dir or (ROOT_DIR / "runs")
    save_dir.mkdir(exist_ok=True)
    client = Groq(api_key=GROQ_API_KEY)

    results = []
    for i, config in enumerate(CONFIGS):
        if i > 0:
            # Ragas's per-question decomposition into several verification
            # calls burns through Groq's free-tier tokens-per-minute budget
            # within one config's run; starting the next config immediately
            # hits the same still-exhausted window. Waiting out a full
            # minute between configs gives each one a fresh budget instead
            # of silently degrading to NaN scores.
            print(f"Waiting {pause_between_configs:.0f}s for the Groq rate limit window to reset...")
            time.sleep(pause_between_configs)
        results.append(run_config(client, config))

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    (save_dir / f"benchmark-{timestamp}.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    summary_keys = [k for k in results[0] if k != "records"]
    csv_path = save_dir / f"benchmark-{timestamp}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in summary_keys})

    print(f"Saved detailed results to {save_dir / f'benchmark-{timestamp}.json'}")
    print(f"Saved summary table to {csv_path}")
    _print_table(results)
    return results
