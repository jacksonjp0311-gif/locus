"""Computational sequence tools.

Pattern: read a string, score, refuse or append a candidate.
Analogy to CRISPR: address a site, cut is a mark, repair is a proposal.
No wet-lab protocol. Fail-open.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HITS = ROOT / "data" / "commons" / "sequence_hits.jsonl"
BASES = set("ACGT")


def clean(seq: str) -> str:
    return "".join(c for c in (seq or "").upper() if c in BASES)


def gc(seq: str) -> float:
    s = clean(seq)
    if not s:
        return 0.0
    return round((s.count("G") + s.count("C")) / len(s), 3)


def find_motif(seq: str, motif: str) -> list:
    s, m = clean(seq), clean(motif)
    if not s or not m:
        return []
    out = []
    i = 0
    while True:
        j = s.find(m, i)
        if j < 0:
            break
        out.append(j)
        i = j + 1
    return out


def orfs(seq: str, min_len: int = 30) -> list:
    """Start-to-stop runs on one strand. Computational only."""
    s = clean(seq)
    stops = {"TAA", "TAG", "TGA"}
    found = []
    i = 0
    while i < len(s) - 2:
        if s[i:i+3] == "ATG":
            j = i + 3
            while j < len(s) - 2:
                if s[j:j+3] in stops:
                    if j - i >= min_len:
                        found.append({"start": i, "end": j + 3, "len": j + 3 - i})
                    break
                j += 3
        i += 1
    return found


def address(seq: str, motif: str = "GG") -> list:
    """Find addressable sites ending in a short motif. A mark, not a cut."""
    sites = find_motif(seq, motif)
    return [{"pos": p, "motif": motif, "kind": "address"} for p in sites]


def record(hit: dict) -> None:
    try:
        HITS.parent.mkdir(parents=True, exist_ok=True)
        with HITS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(hit) + "\n")
    except Exception:
        return


if __name__ == "__main__":
    demo = "ATGAAACCCGGGTTTTAATAGATGCCCCCCTAA"
    print(json.dumps({"gc": gc(demo), "orfs": orfs(demo, 9), "addresses": address(demo, "GG")[:5]}))
