import json
from pathlib import Path

from llm_eval.utils import load_dataset


def test_litedf_getitem_index_returns_row(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text(json.dumps({"query": "q", "expected_answer": "a", "retrieved_contexts": []}) + "\n")
    df = load_dataset(str(p))
    # use df[0] to trigger _LiteDF.__getitem__ and then access the row dict
    row = df[0]
    assert isinstance(row, dict)
    assert row["query"] == "q"
