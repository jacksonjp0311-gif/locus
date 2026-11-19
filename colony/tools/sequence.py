"""Sequence bench. Computational only.

Pattern: read a string, score, refuse or append.
Insert, inject, remove, relocate, reattach are marks on a string.
A mark is not a cut in a cell. Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HITS = ROOT / "data" / "commons" / "sequence_hits.jsonl"
BASES = set("ACGTN")


def clean(seq: str) -> str:
    return "".join(c for c in (seq or "").upper() if c in BASES)


def gc(seq: str) -> float:
    s = clean(seq)
    if not s:
        return 0.0
    return round((s.count("G") + s.count("C")) / len(s), 3)


def find_motif(seq: str, motif: str) -> list:
    s, m = clean(seq), clean(motif)
    if not s or not m:
        return []
    out, i = [], 0
    while True:
        j = s.find(m, i)
        if j < 0:
            break
        out.append(j)
        i = j + 1
    return out


def orfs(seq: str, min_len: int = 30) -> list:
    s = clean(seq)
    stops = {"TAA", "TAG", "TGA"}
    found = []
    i = 0
    while i < len(s) - 2:
        if s[i:i + 3] == "ATG":
            j = i + 3
            while j < len(s) - 2:
                if s[j:j + 3] in stops:
                    if j - i >= min_len:
                        found.append({"start": i, "end": j + 3, "len": j + 3 - i})
                    break
                j += 3
        i += 1
    return found


def address(seq: str, motif: str = "GG") -> list:
    return [{"pos": p, "motif": motif, "kind": "address"} for p in find_motif(seq, motif)]


def insert(seq: str, pos: int, payload: str) -> str:
    s, p = clean(seq), clean(payload)
    pos = max(0, min(pos, len(s)))
    return s[:pos] + p + s[pos:]


def inject(seq: str, pos: int, payload: str, flank: int = 3) -> str:
    """Insert with the surrounding bases kept as context. Still a string."""
    return insert(seq, pos, payload)


def remove(seq: str, start: int, end: int) -> str:
    s = clean(seq)
    start, end = max(0, start), min(len(s), end)
    if end < start:
        start, end = end, start
    return s[:start] + s[end:]


def relocate(seq: str, start: int, end: int, dest: int) -> str:
    s = clean(seq)
    start, end = max(0, start), min(len(s), end)
    if end < start:
        start, end = end, start
    span = s[start:end]
    rest = s[:start] + s[end:]
    dest = max(0, min(dest, len(rest)))
    return rest[:dest] + span + rest[dest:]


def reattach(left: str, right: str) -> str:
    return clean(left) + clean(right)


def record(hit: dict) -> None:
    try:
        HITS.parent.mkdir(parents=True, exist_ok=True)
        with HITS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(hit) + "\n")
    except Exception:
        return
