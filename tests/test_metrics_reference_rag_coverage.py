"""Coverage tests for reference and rag metrics."""
import sys
import types

import pytest

from llm_eval.metrics.reference import BleuMetric, RougeLMetric, BertSimMetric
from llm_eval.metrics.rag import ContextRelevancyMetric, AnswerRelevancyMetric, FaithfulnessMetric


def test_bleu_fallback_to_sentence_bleu(monkeypatch):
    import sacrebleu

    class DummySentenceBleu:
        def __init__(self, score):
            self.score = score

    def _sentence_bleu(answer, refs):
        return DummySentenceBleu(50.0)

    monkeypatch.setattr(sacrebleu, "metrics", None, raising=False)
    monkeypatch.setattr(sacrebleu, "sentence_bleu", _sentence_bleu, raising=False)
    metric = BleuMetric()
    result = metric.compute("q", "ref", "ans", [])
    assert result["score"] == 0.5


def test_bleu_exception_returns_zero(monkeypatch):
    import sacrebleu

    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(sacrebleu, "metrics", None, raising=False)
    monkeypatch.setattr(sacrebleu, "sentence_bleu", _raise, raising=False)
    metric = BleuMetric()
    result = metric.compute("q", "ref", "ans", [])
    assert result["score"] == 0.0


def test_rouge_fallback_ratio(monkeypatch):
    # Force rouge_score import error
    monkeypatch.setitem(sys.modules, "rouge_score", None)
    metric = RougeLMetric()
    result = metric.compute("q", "a b c", "a b", [])
    assert 0.0 < result["score"] <= 1.0


def test_bertsim_fallback_custom_cosine(monkeypatch):
    class DummyModel:
        def encode(self, text, convert_to_tensor=True):
            return [[1.0, 0.0]]

    BertSimMetric._model = DummyModel()

    # Make util imports fail so custom cosine is used
    dummy_pkg = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_pkg)
    if "sentence_transformers.util" in sys.modules:
        monkeypatch.delitem(sys.modules, "sentence_transformers.util", raising=False)

    metric = BertSimMetric()
    result = metric.compute("q", "ref", "ans", [])
    assert 0.0 <= result["score"] <= 1.0


def test_context_relevancy_fallback_heuristic(monkeypatch):
    # Force model to None
    ContextRelevancyMetric._model = None
    import builtins

    real_import = builtins.__import__

    def _custom_import(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("blocked sentence_transformers")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _custom_import)
    metric = ContextRelevancyMetric()
    result = metric.compute("find", "", "", ["find this context"])
    assert 0.0 <= result["score"] <= 1.0


def test_context_relevancy_embedding_failure(monkeypatch):
    class DummyModel:
        def encode(self, text, convert_to_tensor=True):
            raise RuntimeError("encode fail")

    ContextRelevancyMetric._model = DummyModel()
    metric = ContextRelevancyMetric()
    result = metric.compute("query", "", "", ["context"])
    assert result["score"] in (0.0, 1.0)


def test_answer_relevancy_fallback_overlap(monkeypatch):
    AnswerRelevancyMetric._model = None
    metric = AnswerRelevancyMetric()
    result = metric.compute("what is ai", "", "ai is good", [])
    assert 0.0 <= result["score"] <= 1.0


def test_faithfulness_non_list_contexts():
    metric = FaithfulnessMetric()
    result = metric.compute("q", "", "answer", "context answer")
    assert result["score"] > 0.0
