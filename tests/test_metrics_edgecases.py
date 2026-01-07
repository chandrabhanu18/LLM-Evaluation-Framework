import sys
import types
import pytest
from llm_eval.metrics.reference import BleuMetric, RougeLMetric
from llm_eval.metrics.rag import FaithfulnessMetric, ContextRelevancyMetric


def test_bleu_handles_exception(monkeypatch):
    m = BleuMetric()

    # inject a fake sacrebleu module into sys.modules and then patch it
    fake = types.SimpleNamespace()

    def _ok(hyp, refs):
        class S:
            def __init__(self, score):
                self.score = score

        return S(50.0)

    fake.sentence_bleu = _ok
    monkeypatch.setitem(sys.modules, "sacrebleu", fake)
    import importlib
    sacrebleu = importlib.import_module("sacrebleu")

    def boom(hyp, refs):
        raise RuntimeError("boom")

    monkeypatch.setattr(sacrebleu, "sentence_bleu", boom)
    out = m.compute("q", "ref", "hyp", None)
    assert out["score"] == 0.0


def test_rouge_empty_and_valid():
    m = RougeLMetric()
    out = m.compute("q", "", "", None)
    assert 0 <= out["score"] <= 1
    out2 = m.compute("q", "the cat sat", "the cat sat on the mat", None)
    assert 0 <= out2["score"] <= 1


def test_faithfulness_overlap():
    m = FaithfulnessMetric()
    out = m.compute("q", "exp", "apple banana", ["banana pear"]) 
    assert 0 <= out["score"] <= 1


def test_context_relevancy_single_string():
    m = ContextRelevancyMetric()
    out = m.compute("what is x", "exp", "ans", "single context string")
    assert 0 <= out["score"] <= 1
