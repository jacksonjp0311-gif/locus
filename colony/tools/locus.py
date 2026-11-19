"""Locus. Genetics vertex.

Pattern: read the atlas, score a query, refuse or append a proposal.
Phrase search. Never mutate a fact. Never invent a protocol. Fail open.
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


def _blob(rec: dict) -> str:
    return " ".join(str(rec.get(k) or "") for k in ("id", "claim", "domain", "source")).lower().replace("_", " ")


def score(query: str) -> list:
    """Phrase or token. Underscores and spaces match."""
    q = (query or "").lower().replace("_", " ").strip()
    if not q:
        return []
    return [rec for rec in read_atlas() if q in _blob(rec)]


def propose(claim: str, against: str) -> dict:
    rec = {"kind": "proposal", "claim": claim, "against": against, "status": "proposed"}
    try:
        PROPOSALS.parent.mkdir(parents=True, exist_ok=True)
        with PROPOSALS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec


def cycle(query: str = "crispr") -> dict:
    """Read the translator. Score. Propose one genome field. Publish the keep or refuse."""
    try:
        t = ROOT / "TRANSLATOR.md"
        if t.exists():
            t.read_text(encoding="utf-8")
    except Exception:
        pass
    hits = score(query)
    habit = {"kept": False}
    try:
        from colony.tools.genome import load, propose
        g = load()
        prior = float(g.get("last_score") or 0)
        score_now = float(len(hits))
        # one field: record the score. kept only if it beats the prior.
        habit = propose("last_score", score_now, score_now, prior)
    except Exception:
        habit = {"kept": False, "reason": "fail-open"}
    return {
        "source": "locus",
        "query": query,
        "hits": len(hits),
        "ids": [h.get("id") for h in hits],
        "habit": {"kept": habit.get("kept"), "reason": habit.get("reason")},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(cycle("crispr")))
