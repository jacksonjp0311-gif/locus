"""Locus interlink. Read-only observer.

Inspects the genome, the last ops run, and the swarm measurement.
Marks presence. Writes a receipt. Does not mutate the genome.
Does not apply suggestions. Fail-open.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GENOME = ROOT / "data" / "commons" / "genome.json"
OPS_RUN = ROOT / "data" / "commons" / "ops_run.jsonl"
SWARM = ROOT / "data" / "commons" / "swarm.jsonl"
PRESENCE = ROOT / "data" / "commons" / "interlink_presence.jsonl"
RECEIPTS = ROOT / "data" / "commons" / "interlink_receipts.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _tail(path: Path, n: int = 1) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _mark(kind: str) -> None:
    rec = {"ts": _now(), "kind": kind, "source": "locus"}
    try:
        PRESENCE.parent.mkdir(parents=True, exist_ok=True)
        with PRESENCE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def _receipt(kind: str, detail: dict) -> None:
    rec = {"ts": _now(), "kind": kind, "source": "locus", "detail": detail}
    try:
        RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
        with RECEIPTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def inspect() -> dict:
    """Read current state. Marks presence. Read-only."""
    _mark("inspect")
    genome = _read(GENOME) or {}
    last_run = (_tail(OPS_RUN, 1) or [None])[-1]
    last_swarm = (_tail(SWARM, 1) or [None])[-1]
    rec = {
        "status": "complete",
        "generation": genome.get("generation"),
        "last_score": genome.get("last_score"),
        "last_ops_run": last_run,
        "last_swarm": last_swarm,
        "note": "read-only. no mutation.",
    }
    _receipt("inspect", {"generation": rec["generation"], "score": rec["last_score"]})
    return rec


def main() -> int:
    import sys
    if len(sys.argv) < 2 or sys.argv[1] != "inspect":
        print(json.dumps({"status": "error", "note": "usage: inspect"}))
        return 1
    print(json.dumps(inspect(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
