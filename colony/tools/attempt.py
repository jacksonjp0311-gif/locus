"""Attempt. Reads the public statement. Does not see the check.

Pattern: reverse complement, codon, length.
The answer is computed. It is not looked up.
If this module imports checks, the trial is void.
"""
from __future__ import annotations
from colony.tools.tasks import QUEUE

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
CODON = {
    "ATG": "M", "TAA": "*", "TAG": "*", "TGA": "*",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A",
    "CGG": "R", "CGA": "R", "CGC": "R", "CGT": "R",
    "TGC": "C", "TGT": "C",
    "TTC": "F", "TTT": "F",
}


def reverse_complement(seq: str) -> str:
    return "".join(COMP.get(b, b) for b in reversed((seq or "").upper()))


def solve(seq: str) -> str:
    """Three steps. Computed. Not looked up."""
    rc = reverse_complement(seq)
    aa = CODON.get(rc[:3], "?")
    return f"{rc}:{aa}:{len(rc)}"


def attempt(task: dict) -> str:
    """One public task. Returns a computed answer. Does not import checks."""
    return solve(task.get("seq") or "")


def sham(answer: str) -> str:
    """One-step error. Length off by one. Same shape, wrong check."""
    if ":" not in answer:
        return answer + ":X"
    head, _, _ = answer.rpartition(":")
    return head + ":0"
