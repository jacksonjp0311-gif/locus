"""Hidden checks. Not for the attempt.

Pattern: the check is a function. The attempt does not see it.
If the attempt imports this module, the trial is void.
"""
from __future__ import annotations

# Expected answers. Derived offline. Not imported by attempt.
_EXPECTED = {
    "rc1": "CGGCAT:R:6",
    "rc2": "TGCGAA:C:6",
}


def check(task_id: str, answer: str) -> bool:
    """True only if the answer matches the hidden expected."""
    want = _EXPECTED.get(task_id or "")
    if want is None:
        return False
    return str(answer) == want


def expected(task_id: str) -> str | None:
    """For the evaluator only. The attempt must not call this."""
    return _EXPECTED.get(task_id or "")
