from llm_eval.metrics.reference import BleuMetric, RougeLMetric, BertSimMetric


def test_bleu_compute_returns_float():
    m = BleuMetric()
    res = m.compute(query="q", expected="this is a test", answer="this is a test", contexts=None)
    assert isinstance(res, dict) and isinstance(res.get("score"), float)


def test_rouge_fallback_empty_and_overlap():
    m = RougeLMetric()
    # force fallback by clearing scorer
    m.scorer = None
    res_empty = m.compute(query="q", expected="", answer="", contexts=None)
    assert res_empty["score"] == 0.0
    res_overlap = m.compute(query="q", expected="the quick brown", answer="quick brown fox", contexts=None)
    assert 0.0 <= res_overlap["score"] <= 1.0


def test_bertsim_fallback_no_model():
    # ensure model is not present to trigger fallback
    BertSimMetric._model = None
    m = BertSimMetric()
    res = m.compute(query="q", expected="a b c", answer="a b", contexts=None)
    assert isinstance(res, dict) and isinstance(res.get("score"), float)
