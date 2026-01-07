import sys
import types
import subprocess
import json
from llm_eval.metrics.reference import BertSimMetric
from llm_eval.metrics.rag import ContextRelevancyMetric, AnswerRelevancyMetric
from llm_eval.metrics.llm_judge import LLMJudgeMetric


class DummyModel:
    def __init__(self, vec):
        self._vec = vec

    def encode(self, text, convert_to_tensor=False):
        return [self._vec]


class DummyCosSimResult:
    def __init__(self, v):
        self._v = v

    def item(self):
        return self._v


def make_util_cos(v=0.6):
    mod = types.SimpleNamespace()

    def cos_sim(a, b):
        return DummyCosSimResult(v)

    mod.cos_sim = cos_sim
    return mod


def test_bertsim_and_rag_with_stubbed_model(monkeypatch):
    # stub sentence_transformers.util
    sys.modules["sentence_transformers.util"] = make_util_cos(0.6)
    # set models
    BertSimMetric._model = DummyModel([0.1, 0.2])
    b = BertSimMetric()
    r = b.compute("q", "a", "b", None)
    assert 0.0 <= r.get("score", 0.0) <= 1.0

    ContextRelevancyMetric._model = DummyModel([0.1, 0.2])
    c = ContextRelevancyMetric()
    rc = c.compute("q", "", "", ["some context"])
    assert 0.0 <= rc.get("score", 0.0) <= 1.0

    AnswerRelevancyMetric._model = DummyModel([0.1, 0.2])
    a = AnswerRelevancyMetric()
    ar = a.compute("q", "", "ans", None)
    assert 0.0 <= ar.get("score", 0.0) <= 1.0


def test_llm_judge_disabled_by_failure_count():
    cfg = {"provider": "openai", "model": "m", "failure_threshold": 1}
    m = LLMJudgeMetric(cfg)
    m.failure_count = 1
    res = m.compute("q", "e", "a", [])
    assert "error" in res and "disabled" in res["error"]


def test_cli_main_guard_invocation():
    # run module as __main__ to exercise the main guard path
    res = subprocess.run([sys.executable, "-m", "llm_eval.cli", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
