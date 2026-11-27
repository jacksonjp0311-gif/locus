"""Run a proposed sequence. The check stays hidden.

Pattern: read the One Mind ops receipt. Apply the sequence
to a queued task. Transfer only if the real arm passes
the hidden check and the sham does not.
Scores any proposal that has not yet been scored.
The attempt does not import the check. Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path
from colony.tools.tasks import QUEUE
from colony.tools.checks import check

ROOT = Path(__file__).resolve().parent.parent.parent
STORE = ROOT / "data" / "commons" / "ops_run.jsonl"
OPS_URL = "https://raw.githubusercontent.com/jacksonjp0311-gif/one-mind/main/data/commons/ops.jsonl"

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
# Standard codon table. Incomplete lookup was producing ?.
CODON = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def _read_all_ops() -> list[list]:
    """All One Mind sequences. Unavailable is empty."""
    import urllib.request
    try:
        with urllib.request.urlopen(OPS_URL, timeout=12) as r:
            lines = [ln for ln in r.read().decode().splitlines() if ln.strip()]
        out = []
        for ln in lines:
            try:
                ops = json.loads(ln).get("ops")
                if ops:
                    out.append(ops)
            except json.JSONDecodeError:
                continue
        return out
    except Exception:
        return []


def _scored() -> set:
    """Orders already scored."""
    try:
        if not STORE.exists():
            return set()
        out = set()
        for ln in STORE.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            try:
                ops = json.loads(ln).get("ops")
                if ops:
                    out.add(tuple(ops))
            except json.JSONDecodeError:
                continue
        return out
    except Exception:
        return set()


def _apply(seq: str, ops: list) -> str:
    """Apply a closed-set sequence. Unknown ops are skipped."""
    out = seq or ""
    for op in ops or []:
        if op == "reverse":
            out = out[::-1]
        elif op == "complement":
            out = "".join(COMP.get(b, b) for b in out.upper() if b in COMP or b.isalpha())
        elif op == "codon":
            base = out.split(":")[0]
            out = out + ":" + CODON.get(base[:3].upper(), "?")
        elif op == "length":
            out = out + ":" + str(len(out.split(":")[0]))
        elif op == "count":
            out = out + ":" + str(len(out.split(":")[0]))
    return out


def run(task: dict | None = None, prior: float = 0.0) -> dict:
    """Score every unscored proposal. Hidden check."""
    task = task or QUEUE[0]
    all_ops = _read_all_ops()
    already = _scored()
    rec = {"task": task.get("id"), "ops": None, "transfer": False, "reason": "no_proposal"}
    for ops in all_ops:
        if tuple(ops) in already:
            continue
        real = _apply(task.get("seq") or "", ops)
        sham = real.rsplit(":", 1)[0] + ":0" if ":" in real else real + ":0"
        real_pass = check(task.get("id"), real)
        sham_pass = check(task.get("id"), sham)
        rec = {
            "task": task.get("id"),
            "ops": ops,
            "answer": real,
            "sham": sham,
            "real_score": 1.0 if real_pass else 0.0,
            "sham_score": 1.0 if sham_pass else 0.0,
            "transfer": bool(real_pass and not sham_pass),
            "source": "locus",
            "kind": "proposed_sequence",
        }
        try:
            STORE.parent.mkdir(parents=True, exist_ok=True)
            with STORE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        except Exception:
            pass
        already.add(tuple(ops))
    return rec
