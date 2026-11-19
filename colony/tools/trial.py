"""Four-vertex trial.

Pattern: propose, measure, record, evaluate.
Each step is a receipt. Authority stays with the evaluator.
Fail-open. Not a biological result.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.simulate import simulate, off_target
from colony.tools.locus import score

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "data" / "commons" / "four_vertex.jsonl"


def run(claim: str, seq: str, guide: str = "", corpus: list | None = None) -> dict:
    proposed = {"vertex": "propose", "claim": claim, "status": "proposed"}
    measured = simulate(seq, "insert", pos=3, payload="A")
    measured["vertex"] = "measure"
    measured["atlas_hits"] = len(score(claim)) if claim else 0
    measured["off_target"] = off_target(guide, corpus or []) if guide else 0
    recorded = {
        "vertex": "record",
        "claim": claim,
        "measured": True,
        "off_target": measured["off_target"],
    }
    # Evaluator: refuse if off-target high, else accept the measurement as a candidate.
    accept = measured["off_target"] <= 3
    evaluated = {
        "vertex": "evaluate",
        "accept": accept,
        "reason": "within_bar" if accept else "off_target",
    }
    trial = {
        "propose": proposed,
        "measure": measured,
        "record": recorded,
        "evaluate": evaluated,
    }
    try:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trial) + "\n")
    except Exception:
        pass
    return trial


if __name__ == "__main__":
    print(json.dumps(run("crispr", "ATGAAACCCGGG", "ATCG", ["ATGG"])))
