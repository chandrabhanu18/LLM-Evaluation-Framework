import pytest
from llm_eval.metrics.reference import BleuMetric, RougeLMetric, BertSimMetric
from llm_eval.metrics.rag import FaithfulnessMetric


def test_bleu_exact():
    m = BleuMetric()
    out = m.compute("q", "hello world", "hello world", None)
    assert out["score"] >= 0


def test_rouge_l():
    m = RougeLMetric()
    out = m.compute("q", "the cat sat", "the cat sat on the mat", None)
    assert 0 <= out["score"] <= 1


def test_bertsim():
    m = BertSimMetric()
    out = m.compute("q", "I like apples", "I enjoy apples", None)
    assert 0 <= out["score"] <= 1


def test_faithfulness_empty_answer():
    m = FaithfulnessMetric()
    out = m.compute("q", "ref", "", ["some context"])
    assert out["score"] == 0.0
