"""Frozen-task trial. Real arm and sham arm.

Pattern: same task, two corpora.
Real may change the decision. Sham must not.
One number: transfer is true only if the real arm changed
and the sham arm did not. Fail-open. Not a biological result.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "frozen.jsonl"


def _score(corpus: list, query: str) -> int:
    """Hits of the query in the corpus. Higher is a change."""
    q = (query or "").lower()
    return sum(1 for item in corpus if q and q in str(item).lower())


def run(task: str, real: list, sham: list, prior: float = 0.0) -> dict:
    """One task. Two arms. Transfer only if real beats prior and sham does not."""
    real_score = float(_score(real or [], task))
    sham_score = float(_score(sham or [], task))
    real_changed = real_score > prior
    sham_changed = sham_score > prior
    transfer = bool(real_changed and not sham_changed)
    rec = {
        "task": task,
        "prior": prior,
        "real_score": real_score,
        "sham_score": sham_score,
        "real_changed": real_changed,
        "sham_changed": sham_changed,
        "transfer": transfer,
        "source": "locus",
    }
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        with STORE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec
