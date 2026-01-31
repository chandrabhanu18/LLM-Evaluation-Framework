"""Shim to avoid shadowing the real openai package.

If the official openai package is installed, this module forwards all attributes
from the real package. Otherwise, it provides a minimal stub for tests.
"""

from __future__ import annotations

import importlib
import os
import sys
from types import SimpleNamespace


def _load_real_openai():
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # Temporarily remove current directory from sys.path and self from sys.modules
    removed = [p for p in list(sys.path) if os.path.abspath(p) == cur_dir]
    for p in removed:
        sys.path.remove(p)
    sys.modules.pop("openai", None)
    try:
        return importlib.import_module("openai")
    finally:
        for p in reversed(removed):
            sys.path.insert(0, p)


try:
    _real = _load_real_openai()
    globals().update(_real.__dict__)
except Exception:
    # Minimal stub used only when openai isn't installed
    class ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            raise RuntimeError("openai stub: no API configured")

    __all__ = ["ChatCompletion"]
