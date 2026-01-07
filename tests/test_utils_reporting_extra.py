import json
import pytest
from pathlib import Path

from llm_eval.utils import load_jsonl, load_dataset
from llm_eval.reporting import save_markdown_report


def test_load_jsonl_and_csv(tmp_path):
    # create jsonl
    js = tmp_path / "a.jsonl"
    js.write_text(json.dumps({"query": "q", "expected_answer": "e", "retrieved_contexts": []}) + "\n")
    rows = list(load_jsonl(str(js)))
    assert rows and rows[0]["query"] == "q"

    # csv path
    csvp = tmp_path / "d.csv"
    csvp.write_text("query,expected_answer,retrieved_contexts\nq,e,[]\n")
    df = load_dataset(str(csvp))
    assert df.iloc[0]["query"] == "q"


def test_load_dataset_unsupported_and_missing_fields(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("nope")
    with pytest.raises(ValueError):
        load_dataset(str(f))

    # missing fields
    csvp = tmp_path / "d2.csv"
    csvp.write_text("a,b,c\n1,2,3\n")
    with pytest.raises(ValueError):
        load_dataset(str(csvp))


def test_save_markdown_report_variations(tmp_path):
    report = {
        "aggregate": {"m1": None, "m2": {"mean": 0.5, "median": 0.5, "std": 0.0, "min": 0.5, "max": 0.5}},
        "per_example": [
            {"query": "q", "results": {"model_a": {"prediction": "p", "metrics": {"m1": {}}}}},
            {"query": "q2", "results": {"model_b": "notadict"}},
        ],
    }
    out = tmp_path / "r.md"
    save_markdown_report(report, out)
    txt = out.read_text(encoding="utf-8")
    assert "Aggregate Statistics" in txt
    assert "No scores" in txt
