import pytest
from llm_eval.config import EvalConfig, ModelConfig


def test_metrics_validator_rejects_empty():
    with pytest.raises(ValueError):
        EvalConfig(dataset="a.jsonl", output_dir="out", models=[ModelConfig(name="m", outputs="o")], metrics=[])
