import json
import pytest
import os
import llm_eval.metrics.llm_judge as lj

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_llm_judge_success(monkeypatch):
    # Mock OpenAI v2 client
    class MockChoice:
        def __init__(self):
            self.message = type('obj', (object,), {
                'content': json.dumps({"coherence": 0.9, "relevance": 0.8, "safety": 1.0})
            })()
    
    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
    
    class MockCompletions:
        def create(self, *args, **kwargs):
            return MockResponse()
    
    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()
    
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.chat = MockChat()
    
    monkeypatch.setattr("openai.OpenAI", MockClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0}
    metric = lj.LLMJudgeMetric(cfg)
    res = metric.compute("q", "exp", "ans", ["ctx"])
    assert "detail" in res and res["detail"]["coherence"] == 0.9


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_llm_judge_cache(monkeypatch):
    # Mock OpenAI v2 client
    class MockChoice:
        def __init__(self):
            self.message = type('obj', (object,), {
                'content': json.dumps({"coherence": 0.7})
            })()
    
    class MockResponse:
        def __init__(self):
            self.choices = [MockChoice()]
    
    class MockCompletions:
        def create(self, *args, **kwargs):
            return MockResponse()
    
    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()
    
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.chat = MockChat()
    
    monkeypatch.setattr("openai.OpenAI", MockClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0}
    metric = lj.LLMJudgeMetric(cfg)
    lj.LLMJudgeMetric._cache.clear()
    r1 = metric.compute("q1", "e", "a", ["c"])
    r2 = metric.compute("q1", "e", "a", ["c"])
    assert r2.get("cached") is True


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai package not installed")
def test_llm_judge_circuit_breaker(monkeypatch):
    # Mock OpenAI v2 client that raises errors
    class MockCompletions:
        def create(self, *args, **kwargs):
            raise RuntimeError("api down")
    
    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()
    
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.chat = MockChat()
    
    monkeypatch.setattr("openai.OpenAI", MockClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    cfg = {"provider": "openai", "model": "gpt-test", "temperature": 0.0, "max_retries": 1, "failure_threshold": 2}
    metric = lj.LLMJudgeMetric(cfg)
    _ = metric.compute("q", "e", "a", ["c"])
    _ = metric.compute("q", "e", "a", ["c"])
    res = metric.compute("q", "e", "a", ["c"])
    assert res.get("error")
