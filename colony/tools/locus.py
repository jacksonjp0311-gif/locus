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
    """Read the translator. Measure a trial. Propose one field

    Score is the trial quality, not the atlas hit count.
    Higher is better. Kept only if it beats the prior.
    A worse trial refuses. Fail-open.
    """
    try:
        t = ROOT / "TRANSLATOR.md"
        if t.exists():
            t.read_text(encoding="utf-8")
    except Exception:
        pass
    hits = score(query)
    habit = {"kept": False}
    quality = 0.0
    try:
        from colony.tools.genome import load, propose
        from colony.tools.trial import run as trial_run
        g = load()
        prior = float(g.get("last_score") or 0)
        trial = trial_run(query or "crispr", "ACGTACGTACGT", guide="ACGT", corpus=[])
        measured = trial.get("measure") or {}
        ot = float(measured.get("off_target") or 0)
        motifs = float(measured.get("motif_hits") or 0)
        accepted = 1.0 if (trial.get("evaluate") or {}).get("accept") else 0.0
        quality = round(max(0.0, (10.0 - ot) * accepted + motifs), 3)
        habit = propose("last_score", quality, quality, prior)
        try:
            from colony.tools.seeded import record
            record(prior, quality, bool(habit.get("kept")), "locus")
        except Exception:
            pass
    except Exception:
        habit = {"kept": False, "reason": "fail-open"}
    try:
        from colony.tools.evaluate import run as eval_run
        from colony.tools.tasks import QUEUE
        # Open queue. Hidden check. Attempt does not see the check.
        # Run every task, not only the first. rc2 cycles beside rc1.
        queue_results = []
        for task in QUEUE:
            try:
                queue_results.append(eval_run(task))
            except Exception:
                queue_results.append({"task": task, "error": "fail-open"})
    except Exception:
        queue_results = []
    return {
        "source": "locus",
        "query": query,
        "hits": len(hits),
        "ids": [h.get("id") for h in hits],
        "quality": quality,
        "habit": {"kept": habit.get("kept"), "reason": habit.get("reason")},
        "queue": queue_results,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(cycle("crispr")))
