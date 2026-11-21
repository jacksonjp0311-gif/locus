"""Frozen-task trial. Real arm and sham arm.

Pattern: same multi-step task, two corpora.
Steps: reverse complement, codon lookup, length check.
Real holds the full answer. Sham holds a one-step error.
Transfer only if the real arm changed and the sham did not.
Fail-open. Not a biological result.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "frozen.jsonl"

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
CODON = {
    "ATG": "M", "TAA": "*", "TAG": "*", "TGA": "*",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A",
    "CGG": "R", "CGA": "R", "CGC": "R", "CGT": "R",
    "TTC": "F", "TTT": "F",
}

# Fixed sequence. Three steps to the answer.
TASK = "ATGCCG"
# reverse complement of ATGCCG:
# reverse CCGTA, complement GGCAT -> wait
# ATGCCG reversed = GCCGTA
# complement of GCCGTA = CGGCAT
# first codon CGG = R
# length 6
ANSWER = "CGGCAT:R:6"


def reverse_complement(seq: str) -> str:
    return "".join(COMP.get(b, b) for b in reversed((seq or "").upper()))


def solve(seq: str) -> str:
    """Reverse complement, first codon, length. Three steps."""
    rc = reverse_complement(seq)
    codon = rc[:3]
    aa = CODON.get(codon, "?")
    return f"{rc}:{aa}:{len(rc)}"


def _score(corpus: list, answer: str) -> int:
    want = answer or ""
    return 1 if any(str(item) == want for item in (corpus or [])) else 0


def run(task: str = TASK, real: list | None = None, sham: list | None = None,
        prior: float = 0.0) -> dict:
    answer = solve(task or TASK)
    real_score = float(_score(real or [], answer))
    sham_score = float(_score(sham or [], answer))
    real_changed = real_score > prior
    sham_changed = sham_score > prior
    transfer = bool(real_changed and not sham_changed)
    rec = {
        "task": task or TASK,
        "answer": answer,
        "kind": "rc_codon_length",
        "steps": 3,
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
