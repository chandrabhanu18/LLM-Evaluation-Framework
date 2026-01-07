"""Test-only stub package for `sentence_transformers`.
Placed under `tests/_stubs` so it is available during pytest runs
but not included in the installed package.
"""
from .util import cos_sim

class SentenceTransformer:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, **kwargs):
        if texts is None:
            return []
        if isinstance(texts, str):
            texts = [texts]
        return [[0.0] for _ in texts]

__all__ = ["SentenceTransformer", "cos_sim"]
