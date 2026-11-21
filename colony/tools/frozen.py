"""Frozen-task trial. Real arm and sham arm.

Pattern: same computational task, two corpora.
The task is a reverse complement. Not a string search.
Real may contain the answer. Sham must not.
Transfer is true only if the real arm changed
and the sham arm did not. Fail-open. Not a biological result.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "frozen.jsonl"

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}

# Fixed task. Sequence in, reverse complement out.
TASK = "ATGC"
ANSWER = "GCAT"


def reverse_complement(seq: str) -> str:
    """Reverse complement of a DNA string. Unknown bases stay."""
    return "".join(COMP.get(b, b) for b in reversed((seq or "").upper()))


def _score(corpus: list, answer: str) -> int:
    """1 if the corpus holds the computed answer. 0 otherwise."""
    want = (answer or "").upper()
    return 1 if any(str(item).upper() == want for item in (corpus or [])) else 0


def run(task: str = TASK, real: list | None = None, sham: list | None = None,
        prior: float = 0.0) -> dict:
    """One task. Two arms. Transfer only if real beats prior and sham does not."""
    answer = reverse_complement(task or TASK)
    real_score = float(_score(real or [], answer))
    sham_score = float(_score(sham or [], answer))
    real_changed = real_score > prior
    sham_changed = sham_score > prior
    transfer = bool(real_changed and not sham_changed)
    rec = {
        "task": task or TASK,
        "answer": answer,
        "kind": "reverse_complement",
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
