"""Lightweight test stub for sacrebleu used in tests.

Provides a `sentence_bleu` function returning an object with a `.score` attribute.
This stub is intentionally minimal to avoid heavy dependencies during local testing.
"""

from typing import Sequence


class _Score:
    def __init__(self, score: float):
        self.score = score


def sentence_bleu(hypothesis: str, references: Sequence[str]):
    """Return a dummy BLEU-like score object (0-100)."""
    # Very simple heuristic: 100 if hypothesis equals first ref, else 50
    try:
        if hypothesis == references[0]:
            return _Score(100.0)
    except Exception:
        pass
    return _Score(50.0)
