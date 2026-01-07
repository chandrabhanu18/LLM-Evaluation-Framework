import json
from pathlib import Path
import pytest
from llm_eval.utils import load_dataset


def test_load_dataset_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("query,expected_answer,retrieved_contexts\nq1,ans1,ctx1\n")
    df = load_dataset(str(p))
    assert df.shape[0] == 1


def test_load_dataset_missing_fields(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps({"q": "x"}) + "\n")
    with pytest.raises(ValueError):
        load_dataset(str(p))
