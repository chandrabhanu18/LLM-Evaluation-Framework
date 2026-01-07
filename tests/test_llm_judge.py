import json
import llm_eval.metrics.llm_judge as lj


def test_llm_judge_success(monkeypatch):
    def fake_create(*args, **kwargs):
        return {"choices": [{"message": {"content": json.dumps({"coherence": 0.9, "relevance": 0.8, "safety": 1.0})}}]}

    monkeypatch.setattr("openai.ChatCompletion.create", fake_create)
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0}
    metric = lj.LLMJudgeMetric(cfg)
    res = metric.compute("q", "exp", "ans", ["ctx"])
    assert "detail" in res and res["detail"]["coherence"] == 0.9


def test_llm_judge_cache(monkeypatch):
    def fake_create(*args, **kwargs):
        return {"choices": [{"message": {"content": json.dumps({"coherence": 0.7})}}]}

    monkeypatch.setattr("openai.ChatCompletion.create", fake_create)
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0}
    metric = lj.LLMJudgeMetric(cfg)
    lj.LLMJudgeMetric._cache.clear()
    r1 = metric.compute("q1", "e", "a", ["c"])
    r2 = metric.compute("q1", "e", "a", ["c"])
    assert r2.get("cached") is True


def test_llm_judge_circuit_breaker(monkeypatch):
    def raise_exc(*args, **kwargs):
        raise RuntimeError("api down")

    monkeypatch.setattr("openai.ChatCompletion.create", raise_exc)
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0, "max_retries": 1, "failure_threshold": 2}
    metric = lj.LLMJudgeMetric(cfg)
    _ = metric.compute("q", "e", "a", ["c"])
    _ = metric.compute("q", "e", "a", ["c"])
    res = metric.compute("q", "e", "a", ["c"])
    assert res.get("error")
