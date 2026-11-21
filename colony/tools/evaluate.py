"""Evaluator. Calls the hidden check. The attempt does not.

Pattern: real arm and sham arm.
Transfer is true only if the real arm passes the hidden check
and the sham arm does not.
If the attempt imported the checks, the trial is void.
Fail-open. Not a biological result.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.tasks import QUEUE
from colony.tools.attempt import attempt, sham
from colony.tools.checks import check

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "frozen.jsonl"


def _void() -> bool:
    """True if the attempt module imported the checks. Then the trial is void."""
    import colony.tools.attempt as A
    src = Path(A.__file__).read_text(encoding="utf-8")
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("from colony.tools.checks") or s.startswith("import checks"):
            return True
    return False


def run(task: dict | None = None, prior: float = 0.0) -> dict:
    """One task from the queue. Real and sham. Hidden check."""
    task = task or QUEUE[0]
    if _void():
        rec = {"task": task.get("id"), "void": True, "transfer": False, "source": "locus"}
    else:
        real_answer = attempt(task)
        sham_answer = sham(real_answer)
        real_pass = check(task.get("id"), real_answer)
        sham_pass = check(task.get("id"), sham_answer)
        real_score = 1.0 if real_pass else 0.0
        sham_score = 1.0 if sham_pass else 0.0
        transfer = bool(real_score > prior and sham_score <= prior)
        rec = {
            "task": task.get("id"),
            "statement": task.get("statement"),
            "kind": "open_queue",
            "answer": real_answer,
            "sham": sham_answer,
            "prior": prior,
            "real_score": real_score,
            "sham_score": sham_score,
            "real_changed": real_score > prior,
            "sham_changed": sham_score > prior,
            "transfer": transfer,
            "void": False,
            "source": "locus",
        }
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        with STORE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec
