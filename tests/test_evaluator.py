import numpy as np
from pathlib import Path
from llm_eval.config import EvalConfig, ModelConfig
from llm_eval.evaluator import Evaluator


class DummyModel:
    def encode(self, s, convert_to_tensor=False):
        if isinstance(s, str):
            return [len(s)]
        if isinstance(s, (list, tuple)):
            joined = " ".join(map(str, s))
            return [len(joined)]
        return [0]


def test_evaluator_end_to_end(tmp_path, monkeypatch):
    cfg = EvalConfig(
        dataset=str(Path("benchmarks/rag_benchmark.jsonl")),
        output_dir=str(tmp_path),
        models=[ModelConfig(name="model_a", outputs=str(Path("examples/model_a_outputs.jsonl")))],
        metrics=["bleu", "rouge_l", "bertscore", "faithfulness", "context_relevancy", "answer_relevancy"],
    )

    from llm_eval.metrics.reference import BertSimMetric
    from llm_eval.metrics.rag import ContextRelevancyMetric, AnswerRelevancyMetric

    BertSimMetric._model = DummyModel()
    ContextRelevancyMetric._model = DummyModel()
    AnswerRelevancyMetric._model = DummyModel()

    evaluator = Evaluator(cfg, verbose=False)
    report = evaluator.run()

    assert (Path(tmp_path) / "results.json").exists()
    assert "aggregate" in report
    for m in ["bleu", "rouge_l", "bertscore", "faithfulness", "context_relevancy", "answer_relevancy"]:
        assert m in report["aggregate"]
