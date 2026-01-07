import os
import json
from typing import Dict, Any, List
from pathlib import Path
from .config import EvalConfig
from .utils import load_dataset, load_jsonl

from .metrics.reference import BleuMetric, RougeLMetric, BertSimMetric
from .metrics.rag import FaithfulnessMetric, ContextRelevancyMetric, AnswerRelevancyMetric
from .metrics.llm_judge import LLMJudgeMetric
from .metrics import get_custom
from .reporting import save_json_report, save_markdown_report, plot_histograms, plot_radar


METRIC_REGISTRY = {
    "bleu": BleuMetric,
    "rouge_l": RougeLMetric,
    "bertscore": BertSimMetric,
    "faithfulness": FaithfulnessMetric,
    "context_relevancy": ContextRelevancyMetric,
    "answer_relevancy": AnswerRelevancyMetric,
    "llm_judge": LLMJudgeMetric,
}


class Evaluator:
    def __init__(self, config: EvalConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.dataset = load_dataset(config.dataset)
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    def _load_model_outputs(self, path: str) -> Dict[str, str]:
        outputs = {}
        for obj in load_jsonl(path):
            q = obj.get("query")
            pred = obj.get("prediction") or obj.get("answer")
            if q:
                outputs[q] = pred
        return outputs

    def _instantiate_metric(self, name: str):
        custom = get_custom(name)
        if custom:
            return custom()
        if name == "llm_judge":
            if not self.config.llm_judge:
                raise ValueError("llm_judge configured in metrics but missing llm_judge section")
            return LLMJudgeMetric(self.config.llm_judge.dict() if hasattr(self.config.llm_judge, "dict") else self.config.llm_judge)
        cls = METRIC_REGISTRY.get(name)
        if not cls:
            raise ValueError(f"Unknown metric: {name}")
        return cls()

    def run(self):
        per_example = []

        metrics = [self._instantiate_metric(m) for m in self.config.metrics]

        model_outputs = {m.name: self._load_model_outputs(m.outputs) for m in self.config.models}

        # Support both pandas DataFrame and plain list-of-dicts (for lightweight tests)
        if hasattr(self.dataset, "iterrows"):
            iterator = (row for _, row in self.dataset.iterrows())
        else:
            iterator = (row for row in self.dataset)

        for row in iterator:
            query = row["query"]
            expected = row["expected_answer"]
            contexts = row["retrieved_contexts"]
            example = {"query": query, "expected_answer": expected}
            example_results = {}
            for model in self.config.models:
                pred = model_outputs.get(model.name, {}).get(query, "")
                model_res = {}
                for metric in metrics:
                    try:
                        out = metric.compute(query, expected, pred, contexts)
                    except Exception as e:
                        out = {"error": str(e)}
                    model_res[metric.name] = out
                example_results[model.name] = {"prediction": pred, "metrics": model_res}
            example["results"] = example_results
            per_example.append(example)

        agg = {}
        for metric_name in self.config.metrics:
            all_scores = []
            for ex in per_example:
                for mname, v in ex["results"].items():
                    val = v["metrics"].get(metric_name, {})
                    score = val.get("score")
                    if isinstance(score, (int, float)):
                        all_scores.append(score)
            import numpy as np

            if all_scores:
                arr = np.array(all_scores)
                agg[metric_name] = {
                    "mean": float(arr.mean()),
                    "median": float(np.median(arr)),
                    "std": float(arr.std()),
                    "min": float(arr.min()),
                    "max": float(arr.max()),
                }
            else:
                agg[metric_name] = None

        report = {"aggregate": agg, "per_example": per_example}

        out_json = Path(self.config.output_dir) / "results.json"
        save_json_report(report, out_json)

        out_md = Path(self.config.output_dir) / "results.md"
        save_markdown_report(report, out_md)

        plot_histograms(report, Path(self.config.output_dir))
        plot_radar(report, Path(self.config.output_dir))

        if getattr(self.config, "gates", None):
            failed = []
            for metric_name, threshold in self.config.gates.items():
                stats = agg.get(metric_name)
                mean = None
                if stats:
                    mean = stats.get("mean")
                if mean is None or mean < float(threshold):
                    failed.append({"metric": metric_name, "mean": mean, "threshold": threshold})
            if failed:
                raise SystemExit(2)

        return report
