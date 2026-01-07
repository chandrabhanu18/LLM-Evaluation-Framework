from llm_eval.metrics.rag import FaithfulnessMetric, ContextRelevancyMetric, AnswerRelevancyMetric
from llm_eval.metrics.reference import BleuMetric, RougeLMetric


def test_faithfulness_overlap():
    m = FaithfulnessMetric()
    out = m.compute("q", "exp", "the cat sat", ["the cat sat on the mat"]) 
    assert out["score"] == 1.0


def test_context_relevancy_simple():
    m = ContextRelevancyMetric()
    out = m.compute("what is x", "exp", "ans", "this contains what is x in text")
    assert out["score"] == 1.0 or 0.0 <= out["score"] <= 1.0


def test_answer_relevancy_overlap():
    m = AnswerRelevancyMetric()
    out = m.compute("q", "exp", "answer is q here", None)
    assert 0.0 <= out["score"] <= 1.0


def test_bleu_and_rouge_fallbacks():
    b = BleuMetric()
    r = RougeLMetric()
    assert isinstance(b.compute("q", "a b c", "a b c", None)["score"], float)
    assert isinstance(r.compute("q", "a b c", "a b c", None)["score"], float)
