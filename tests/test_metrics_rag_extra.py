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
    # Save the original model and force fallback by patching
    import unittest.mock as mock
    with mock.patch.object(ContextRelevancyMetric, '_model', None):
        # Create instance - it will try to load but should accept None
        m = ContextRelevancyMetric()
        # Force the model to remain None for this test
        m.model = None
        # list case where query appears in one context
        res = m.compute(query="findme", expected="", answer="", contexts=["nothing", "please findme here"]) 
        assert res["score"] == 1.0
        # string case
        res2 = m.compute(query="hello", expected="", answer="", contexts="say hello world")
        assert res2["score"] == 1.0


def test_answer_relevancy_fallback():
    # Properly isolate the mock state
    import unittest.mock as mock
    with mock.patch.object(AnswerRelevancyMetric, '_model', None):
        m = AnswerRelevancyMetric()
        # Force the model to remain None for this test
        m.model = None
        res = m.compute(query="a b c", expected="", answer="b c d", contexts=None)
        # overlap ratio with qset={'a','b','c'} and aset={'b','c','d'} => 2/3
        assert abs(res["score"] - (2.0 / 3.0)) < 1e-6
