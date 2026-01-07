import pytest
from pathlib import Path
import json

from llm_eval.config import EvalConfig, ModelConfig
from llm_eval.evaluator import Evaluator
from llm_eval.metrics import register_metric


class FixedLowMetric:
    def __init__(self):
        self.name = "fixedlow"

    def compute(self, query, expected, answer, contexts):
        return {"score": 0.1}


def test_instantiate_custom_and_unknown(tmp_path):
    # register custom
    register_metric("fixedlow", FixedLowMetric)
    cfg = EvalConfig(
        dataset="benchmarks/rag_benchmark.jsonl",
        output_dir=str(tmp_path / "out"),
        models=[ModelConfig(name="m", outputs="examples/model_a_outputs.jsonl")],
        metrics=["fixedlow"],
    )
    ev = Evaluator(cfg)
    # instantiate should pick up custom metric
    m = ev._instantiate_metric("fixedlow")
    assert isinstance(m, FixedLowMetric)

    # unknown metric should raise
    with pytest.raises(ValueError):
        ev._instantiate_metric("nope_metric")


def test_llm_judge_missing_config_raises(tmp_path):
    cfg = EvalConfig(
        dataset="benchmarks/rag_benchmark.jsonl",
        output_dir=str(tmp_path / "out2"),
        models=[ModelConfig(name="m", outputs="examples/model_a_outputs.jsonl")],
        metrics=["llm_judge"],
    )
    ev = Evaluator(cfg)
    with pytest.raises(ValueError):
        ev._instantiate_metric("llm_judge")


def test_load_model_outputs_handles_answer_and_prediction(tmp_path):
    data = [
        {"query": "q1", "prediction": "p1"},
        {"query": "q2", "answer": "a2"},
        {"noquery": "x"},
    ]
    p = tmp_path / "outs.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for o in data:
            f.write(json.dumps(o) + "\n")

    cfg = EvalConfig(
        dataset="benchmarks/rag_benchmark.jsonl",
        output_dir=str(tmp_path / "out3"),
        models=[ModelConfig(name="m", outputs=str(p))],
        metrics=["fixedlow"],
    )
    ev = Evaluator(cfg)
    mapping = ev._load_model_outputs(str(p))
    assert mapping.get("q1") == "p1"
    assert mapping.get("q2") == "a2"


def test_gates_failure_raises_systemexit(tmp_path):
    register_metric("fixedlow", FixedLowMetric)
    cfg = EvalConfig(
        dataset="benchmarks/rag_benchmark.jsonl",
        output_dir=str(tmp_path / "out4"),
        models=[ModelConfig(name="m", outputs="examples/model_a_outputs.jsonl")],
        metrics=["fixedlow"],
        gates={"fixedlow": 0.9},
    )
    ev = Evaluator(cfg)
    with pytest.raises(SystemExit):
        ev.run()
