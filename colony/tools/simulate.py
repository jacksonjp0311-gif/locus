"""Sequence simulator. Computational only.

Pattern: apply an edit, score it, refuse if off-target is high.
A better score is a proposal. Not a fact. Not a cell.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.sequence import clean, gc, find_motif, insert, remove

ROOT = Path(__file__).resolve().parent.parent.parent
SIMS = ROOT / "data" / "commons" / "simulations.jsonl"


def off_target(guide: str, corpus: list, max_mismatch: int = 2) -> int:
    """Count corpus strings within max_mismatch of the guide. Simple Hamming."""
    g = clean(guide)
    if not g:
        return 0
    n = 0
    for raw in corpus:
        s = clean(raw)
        if len(s) != len(g) or s == g:
            continue
        mis = sum(1 for a, b in zip(g, s) if a != b)
        if mis <= max_mismatch:
            n += 1
    return n


def simulate(seq: str, op: str, **kw) -> dict:
    """Apply insert or remove. Score GC and a motif. Append the result."""
    s = clean(seq)
    if op == "insert":
        out = insert(s, int(kw.get("pos", 0)), kw.get("payload", ""))
    elif op == "remove":
        out = remove(s, int(kw.get("start", 0)), int(kw.get("end", 0)))
    else:
        out = s
    rec = {
        "op": op,
        "before_len": len(s),
        "after_len": len(out),
        "gc_before": gc(s),
        "gc_after": gc(out),
        "motif_hits": len(find_motif(out, kw.get("motif", "GG"))),
        "status": "simulated",
    }
    try:
        SIMS.parent.mkdir(parents=True, exist_ok=True)
        with SIMS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec
