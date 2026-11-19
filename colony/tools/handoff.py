"""Swarm handoff. A number, not an order.

Colony or One Mind asks. Locus scores. Locus does not keep for them.
"""
from __future__ import annotations
from colony.tools.locus import score
from colony.tools.simulate import off_target, simulate


def ask(query: str = "", guide: str = "", corpus: list | None = None) -> dict:
    hits = score(query) if query else []
    ot = off_target(guide, corpus or []) if guide else 0
    return {
        "source": "locus",
        "query_hits": len(hits),
        "ids": [h.get("id") for h in hits][:8],
        "off_target": ot,
        "refuse": ot > 3,
    }
