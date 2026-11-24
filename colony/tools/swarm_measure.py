"""Swarm measurement. Records diversity of proposals and transfer status.

Reads the public ops receipts and the local ops_run. Writes one line
per cycle. Does not change any keep. Fail-open.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "swarm.jsonl"
OPS_URL = "https://raw.githubusercontent.com/jacksonjp0311-gif/one-mind/main/data/commons/ops.jsonl"
RUNS = ROOT / "data" / "commons" / "ops_run.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tail(path: Path, n: int = 16) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _ops() -> list[dict]:
    import urllib.request
    try:
        with urllib.request.urlopen(OPS_URL, timeout=12) as r:
            lines = [ln for ln in r.read().decode().splitlines() if ln.strip()]
        return [json.loads(ln) for ln in lines[-16:]]
    except Exception:
        return []


def measure() -> dict:
    ops = _ops()
    runs = _tail(RUNS)
    orders = [tuple(o.get("ops") or []) for o in ops if o.get("ops")]
    unique = len(set(orders))
    transfers = sum(1 for r in runs if r.get("transfer"))
    zeros = sum(1 for r in runs if r.get("real_score") == 0.0 and r.get("sham_score") == 0.0)
    rec = {
        "ts": _now(),
        "source": "locus",
        "kind": "swarm_measure",
        "proposals": len(ops),
        "unique_orders": unique,
        "runs": len(runs),
        "transfers": transfers,
        "zero_pairs": zeros,
        "note": "Descriptive only. No keep change.",
    }
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        with STORE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass
    return rec
