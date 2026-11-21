"""Open task queue. Public statements. No answers.

Pattern: a task is a statement. The answer is not here.
The attempt reads this file. It does not read the checks.
"""
from __future__ import annotations

QUEUE = [
    {
        "id": "rc1",
        "statement": "Reverse complement of ATGCCG. Then the amino acid of the first codon. Then the length. Format RC:AA:LEN.",
        "seq": "ATGCCG",
    },
    {
        "id": "rc2",
        "statement": "Reverse complement of TTCGCA. Then the amino acid of the first codon. Then the length. Format RC:AA:LEN.",
        "seq": "TTCGCA",
    },
]
