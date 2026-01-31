"""Tests for utils load_dataset fallback and wrapper behavior."""
import builtins
import json
import sys
import types
from pathlib import Path

import pytest

from llm_eval import utils
from llm_eval.utils import load_dataset


def _block_pandas_import(monkeypatch):
    real_import = builtins.__import__

    def _custom_import(name, *args, **kwargs):
        if name == "pandas":
            raise ImportError("blocked pandas")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _custom_import)


def test_load_dataset_jsonl_fallback(monkeypatch, tmp_path):
    _block_pandas_import(monkeypatch)
    jsonl = tmp_path / "data.jsonl"
    jsonl.write_text(
        json.dumps({"query": "Q1", "expected_answer": "A1", "retrieved_contexts": ["C1"]}) + "\n",
        encoding="utf-8",
    )
    df = load_dataset(str(jsonl))
    assert df.shape[0] == 1
    assert df[0]["query"] == "Q1"
    assert df["expected_answer"] == ["A1"]
    rows = list(df.iterrows())
    assert rows[0][1]["retrieved_contexts"] == ["C1"]


def test_load_dataset_csv_fallback(monkeypatch, tmp_path):
    _block_pandas_import(monkeypatch)
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(
        "query,expected_answer,retrieved_contexts\nQ1,A1,C1\nQ2,A2,C2\n",
        encoding="utf-8",
    )
    df = load_dataset(str(csv_path))
    assert df.shape[0] == 2
    assert df[0]["query"] == "Q1"
    assert df["retrieved_contexts"] == ["C1", "C2"]


def test_load_dataset_missing_fields_fallback(monkeypatch, tmp_path):
    _block_pandas_import(monkeypatch)
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("query,expected_answer\nQ1,A1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_dataset(str(csv_path))


def test_dataframe_wrapper_behavior(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(
        "query,expected_answer,retrieved_contexts\nQ1,A1,C1\nQ2,A2,C2\n",
        encoding="utf-8",
    )
    df = load_dataset(str(csv_path))
    # _DataFrameWrapper API
    assert df.shape[0] == 2
    assert df[0]["query"] == "Q1"
    assert df["query"] == ["Q1", "Q2"]
    rows = list(df.iterrows())
    assert rows[1][1]["expected_answer"] == "A2"
