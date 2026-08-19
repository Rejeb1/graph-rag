"""Make `src` importable when running pytest from the repo root, same as scripts/*.py."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load a real .env first (if present) — otherwise the dummy fallback below
# would win, since load_dotenv() never overrides an already-set env var,
# and setdefault() would have already "set" it.
load_dotenv()

# The Groq SDK raises at client construction (not just at request time) if no
# API key is present anywhere. src/api/main.py builds a client at import
# time, so importing it in CI (no real secrets) would otherwise crash before
# a single test runs. A dummy key is enough to satisfy construction — tests
# that need a real response are marked `live` and skipped without one.
os.environ.setdefault("GROQ_API_KEY", "test-dummy-key")
