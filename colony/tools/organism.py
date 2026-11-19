"""The repository as an organism.

Pattern: name the organs. Read them. Report the state.
A genome is hereditary material. A cycle is metabolism.
A refuse is immune. A prune is apoptosis.
This is a model of the repo. It is not alive. It is not a cell.
Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.genome import load as load_genome
from colony.tools.locus import read_atlas

ROOT = Path(__file__).resolve().parent.parent.parent
STATE = ROOT / "data" / "commons" / "organism.json"

ORGANS = {
    "genome": "hereditary material. the schedule the next cycle reads",
    "atlas": "memory. established facts. not rewritten",
    "bench": "metabolism. gc, motif, edit, score",
    "ingest": "nutrition. unique claims in. duplicates refused",
    "immune": "refuse. off-target above the bar is not kept",
    "apoptosis": "prune. a tool below the bar is removed",
    "growth": "a tool above the prior is added",
    "witness_link": "sensory. reads others. decides nothing",
}


def state() -> dict:
    g = load_genome()
    atlas = read_atlas()
    rec = {
        "organism": "locus",
        "alive": False,
        "cell": False,
        "generation": g.get("generation"),
        "organs": ORGANS,
        "genome_tools": g.get("tools"),
        "bar": g.get("refuse_if_off_target_above"),
        "atlas_n": len(atlas),
        "status": "modeled",
    }
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    except Exception:
        pass
    return rec


if __name__ == "__main__":
    print(json.dumps(state()))
