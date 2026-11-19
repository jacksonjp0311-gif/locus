"""Invariant ingest. Deduped. Fail-open.

Pattern: a claim comes in. If the same claim and source exist, refuse.
Otherwise append. Never rewrite. Never promote to kept.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "invariants.jsonl"


def _id(claim: str, source: str) -> str:
    raw = (claim or "").strip().lower() + "|" + (source or "").strip().lower()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _seen() -> set:
    if not STORE.exists():
        return set()
    out = set()
    for line in STORE.read_text(encoding="utf-8").splitlines():
        try:
            out.add(json.loads(line).get("id"))
        except Exception:
            continue
    return out


def ingest(claim: str, source: str, domain: str = "observed") -> dict:
    """Append a unique invariant. Duplicate returns the existing id and added=False."""
    rec = {
        "id": _id(claim, source),
        "claim": (claim or "").strip(),
        "source": (source or "").strip(),
        "domain": domain,
        "status": "observed",
    }
    if not rec["claim"]:
        return {"added": False, "reason": "empty"}
    try:
        if rec["id"] in _seen():
            return {"added": False, "id": rec["id"], "reason": "duplicate"}
        STORE.parent.mkdir(parents=True, exist_ok=True)
        with STORE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        return {"added": True, "id": rec["id"]}
    except Exception:
        return {"added": False, "reason": "fail-open"}
