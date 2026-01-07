import yaml
from llm_eval.cli import load_config
from llm_eval.metrics import register_metric, get_custom
from llm_eval.metrics.base import Metric


def test_load_config_yaml(tmp_path):
    cfg = {"dataset": "benchmarks/rag_benchmark.jsonl", "output_dir": "out", "models": [{"name": "m","outputs": "a"}], "metrics": ["bleu"]}
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(cfg))
    loaded = load_config(str(p))
    assert loaded.dataset == cfg["dataset"]


def test_register_custom_metric():
    class MyMetric(Metric):
        def __init__(self):
            super().__init__("my_metric")

        def compute(self, query, expected, answer, contexts):
            return {"score": 0.5}

    register_metric("my_metric", MyMetric)
    ctor = get_custom("my_metric")
    assert ctor is MyMetric
