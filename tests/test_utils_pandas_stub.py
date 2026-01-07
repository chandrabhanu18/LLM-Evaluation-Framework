import sys
import types
import csv
from pathlib import Path
import json
import pytest

from llm_eval.utils import load_dataset, load_jsonl


class _FakeDF:
    def __init__(self, rows):
        self._rows = rows
        self.columns = list(rows[0].keys()) if rows else []

    @property
    def shape(self):
        return (len(self._rows), len(self.columns))

    def iterrows(self):
        for i, r in enumerate(self._rows):
            yield i, r

    def __getitem__(self, key):
        # behave like pandas row access for tests
        if isinstance(key, int):
            return self._rows[key]
        raise KeyError


def _make_fake_pandas():
    mod = types.SimpleNamespace()

    def DataFrame(rows):
        return _FakeDF(rows)

    def read_csv(path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader]
        return _FakeDF(rows)

    mod.DataFrame = DataFrame
    mod.read_csv = read_csv
    return mod


def test_load_dataset_jsonl_with_pandas_stub(monkeypatch, tmp_path):
    fake_pd = _make_fake_pandas()
    monkeypatch.setitem(sys.modules, "pandas", fake_pd)

    p = tmp_path / "d.jsonl"
    p.write_text(json.dumps({"query": "q", "expected_answer": "a", "retrieved_contexts": []}) + "\n")
    df = load_dataset(str(p))
    assert hasattr(df, "iterrows")
    assert df.shape[0] == 1


def test_load_dataset_csv_with_pandas_stub(monkeypatch, tmp_path):
    fake_pd = _make_fake_pandas()
    monkeypatch.setitem(sys.modules, "pandas", fake_pd)

    p = tmp_path / "d.csv"
    p.write_text("query,expected_answer,retrieved_contexts\nq,a,[]\n")
    df = load_dataset(str(p))
    assert df.shape[0] == 1


def test_load_dataset_missing_fields_with_pandas_stub(monkeypatch, tmp_path):
    fake_pd = _make_fake_pandas()
    monkeypatch.setitem(sys.modules, "pandas", fake_pd)

    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps({"q": "x"}) + "\n")
    with pytest.raises(ValueError):
        load_dataset(str(p))


def test_unsupported_format_with_pandas_stub(monkeypatch, tmp_path):
    fake_pd = _make_fake_pandas()
    monkeypatch.setitem(sys.modules, "pandas", fake_pd)

    p = tmp_path / "x.txt"
    p.write_text("nope")
    with pytest.raises(ValueError):
        load_dataset(str(p))
