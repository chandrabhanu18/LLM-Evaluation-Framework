from llm_eval.metrics.rag import (
    FaithfulnessMetric,
    ContextRelevancyMetric,
    AnswerRelevancyMetric,
)


def test_faithfulness_empty_answer():
    m = FaithfulnessMetric()
    res = m.compute(query="q", expected="e", answer="", contexts=["some context"])
    assert isinstance(res, dict) and res["score"] == 0.0


def test_faithfulness_overlap():
    m = FaithfulnessMetric()
    res = m.compute(query="q", expected="e", answer="token1 token2", contexts=["token2 other"])
    assert 0.0 <= res["score"] <= 1.0


def test_context_relevancy_fallback_list_and_str():
    # force fallback by resetting class model
    ContextRelevancyMetric._model = None
    m = ContextRelevancyMetric()
    # list case where query appears in one context
    res = m.compute(query="findme", expected="", answer="", contexts=["nothing", "please findme here"]) 
    assert res["score"] == 1.0
    # string case
    res2 = m.compute(query="hello", expected="", answer="", contexts="say hello world")
    assert res2["score"] == 1.0


def test_answer_relevancy_fallback():
    AnswerRelevancyMetric._model = None
    m = AnswerRelevancyMetric()
    res = m.compute(query="a b c", expected="", answer="b c d", contexts=None)
    # overlap ratio with qset={'a','b','c'} and aset={'b','c','d'} => 2/3
    assert abs(res["score"] - (2.0 / 3.0)) < 1e-6
