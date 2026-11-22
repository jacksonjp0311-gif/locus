"""Run a proposed sequence. The check stays hidden.

Pattern: read the One Mind ops receipt. Apply the sequence
to a queued task. Transfer only if the real arm passes
the hidden check and the sham does not.
The attempt does not import the check. Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.tasks import QUEUE
from colony.tools.checks import check

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "ops_run.jsonl"
OPS_URL = "https://raw.githubusercontent.com/jacksonjp0311-gif/one-mind/main/data/commons/ops.jsonl"

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
CODON = {
    "ATG": "M", "TAA": "*", "TAG": "*", "TGA": "*",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A",
    "CGG": "R", "CGA": "R", "CGC": "R", "CGT": "R",
    "TGC": "C", "TGT": "C", "TTC": "F", "TTT": "F",
}


def _read_ops() -> list | None:
    """Last One Mind sequence. Unavailable is None."""
    import urllib.request
    try:
        with urllib.request.urlopen(OPS_URL, timeout=12) as r:
            lines = [ln for ln in r.read().decode().splitlines() if ln.strip()]
        if not lines:
            return None
        return json.loads(lines[-1]).get("ops")
    except Exception:
        return None


def _apply(seq: str, ops: list) -> str:
    """Apply a closed-set sequence. Unknown ops are skipped."""
    out = seq or ""
    for op in ops or []:
        if op == "reverse":
            out = out[::-1]
        elif op == "complement":
            out = "".join(COMP.get(b, b) for b in out.upper())
        elif op == "codon":
            out = out + ":" + CODON.get(out[:3].upper(), "?")
        elif op == "length":
            out = out + ":" + str(len(out.split(":")[0]))
        elif op == "count":
            out = out + ":" + str(len(out))
    return out


def run(task: dict | None = None, prior: float = 0.0) -> dict:
    """One proposed sequence against one task. Hidden check."""
    task = task or QUEUE[0]
    ops = _read_ops()
    if not ops:
        rec = {"task": task.get("id"), "ops": None, "transfer": False, "reason": "no_proposal"}
    else:
        real = _apply(task.get("seq") or "", ops)
        sham = real.rsplit(":", 1)[0] + ":0" if ":" in real else real + ":0"
        real_pass = check(task.get("id"), real)
        sham_pass = check(task.get("id"), sham)
        rec = {
            "task": task.get("id"),
            "ops": ops,
            "answer": real,
            "sham": sham,
            "real_score": 1.0 if real_pass else 0.0,
            "sham_score": 1.0 if sham_pass else 0.0,
            "transfer": bool(real_pass and not sham_pass),
            "source": "locus",
            "kind": "proposed_sequence",
        }
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        with STORE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec
