import pytest
from llm_eval.config import EvalConfig, ModelConfig
from llm_eval.evaluator import Evaluator
from pathlib import Path


def test_missing_llm_judge_config_raises():
    cfg = EvalConfig(
        dataset=str(Path("benchmarks/rag_benchmark.jsonl")),
        output_dir="out",
        models=[ModelConfig(name="m", outputs="examples/model_a_outputs.jsonl")],
        metrics=["llm_judge"],
    )

    evaluator = Evaluator(cfg)
    with pytest.raises(ValueError):
        evaluator.run()
