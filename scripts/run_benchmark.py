"""CLI: run the evaluation benchmark across pipeline configurations.

Usage: python scripts/run_benchmark.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.benchmark import run_benchmark

if __name__ == "__main__":
    run_benchmark()
