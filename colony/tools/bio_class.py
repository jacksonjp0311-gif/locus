"""Biological function class. A model, not a protocol.

Pattern: name the published class. Apply the string analogue. Score.
Base edit: C to T in a window. That is the class.
This does not edit a cell. It does not produce a therapy.
Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.sequence import clean, gc

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "data" / "commons" / "bio_class.jsonl"

CLASSES = {
    "base_edit_c_to_t": "C to T in a window. No double-strand break. Published class.",
    "base_edit_a_to_g": "A to G in a window. No double-strand break. Published class.",
}


def base_edit(seq: str, kind: str = "base_edit_c_to_t", window: int = 5) -> dict:
    s = clean(seq)
    if kind == "base_edit_a_to_g":
        edited = s[:window].replace("A", "G") + s[window:]
        changed = "A>G"
    else:
        edited = s[:window].replace("C", "T") + s[window:]
        changed = "C>T"
        kind = "base_edit_c_to_t"
    rec = {
        "class": kind,
        "description": CLASSES.get(kind, ""),
        "changed": changed,
        "window": window,
        "before": s,
        "after": edited,
        "gc_before": gc(s),
        "gc_after": gc(edited),
        "status": "modeled",
        "cell": False,
    }
    try:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec


if __name__ == "__main__":
    print(json.dumps(base_edit("ATGCCCGGGAAA", "base_edit_c_to_t")))
