"""Capability change. The trial changes what the next step can do.

Pattern: an accepted trial may grow a tool. A refused trial may raise the bar.
The next ask uses the new genome. Fail-open.
A capability here is a dial the system reads. Not a biological function.
"""
from __future__ import annotations
import json
from colony.tools.genome import load, grow, prune, propose
from colony.tools.trial import run


def apply(trial: dict) -> dict:
    accepted = bool(trial.get("evaluate", {}).get("accept"))
    before = load()
    if accepted:
        change = grow("measured_edit", 1.0, 0.0)
        kind = "grew"
    else:
        # raise the refuse bar by proposing a stricter field if present
        current = int(before.get("refuse_if_off_target_above") or 3)
        change = propose("refuse_if_off_target_above", max(1, current - 1), 1.0, 0.0)
        kind = "tightened"
    after = load()
    return {
        "kind": kind,
        "accepted": accepted,
        "before_tools": before.get("tools"),
        "after_tools": after.get("tools"),
        "before_bar": before.get("refuse_if_off_target_above"),
        "after_bar": after.get("refuse_if_off_target_above"),
        "change": {k: change.get(k) for k in ("kept", "reason")},
    }


def demonstrate() -> dict:
    # crossing trial should tighten or refuse-path
    seq = "ATGAAACCCGGGTTTTAA"
    guide = "ATCGATCG"
    refused = run("crispr", seq, guide, ["ATCGATCA", "ATCGATAG", "ATCGATTA", "ATCGATTG", "GTCGATCG"])
    accepted = run("crispr", seq, guide, ["GGGGGGGG"])
    return {
        "on_refuse": apply(refused),
        "on_accept": apply(accepted),
        "genome": load(),
    }


if __name__ == "__main__":
    print(json.dumps(demonstrate()))
