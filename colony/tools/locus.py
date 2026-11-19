"""Locus. Genetics vertex.

Pattern: read the atlas, score a query, refuse or append.
Never mutate a fact. Never invent a protocol. Fail open.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ATLAS = ROOT / "atlas" / "genetics.jsonl"
PROPOSALS = ROOT / "data" / "commons" / "proposals.jsonl"


def read_atlas() -> list:
    if not ATLAS.exists():
        return []
    out = []
    for line in ATLAS.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def score(query: str) -> list:
    """Return atlas entries whose claim or id contains the query. Fail-open."""
    q = (query or "").lower()
    if not q:
        return []
    hits = []
    for rec in read_atlas():
        blob = " ".join(str(rec.get(k) or "") for k in ("id", "claim", "domain")).lower()
        if q in blob:
            hits.append(rec)
    return hits


def propose(claim: str, against: str) -> dict:
    """A novel claim is a proposal. It is not a fact. Fail-open."""
    rec = {"kind": "proposal", "claim": claim, "against": against, "status": "proposed"}
    try:
        PROPOSALS.parent.mkdir(parents=True, exist_ok=True)
        with PROPOSALS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec


def cycle(query: str = "crispr") -> dict:
    try:
        t = ROOT / "TRANSLATOR.md"
        if t.exists():
            t.read_text(encoding="utf-8")
    except Exception:
        pass
    hits = score(query)
    return {"source": "locus", "query": query, "hits": len(hits), "ids": [h.get("id") for h in hits]}


if __name__ == "__main__":
    print(json.dumps(cycle("crispr")))
    print(json.dumps(cycle("does not exist")))
