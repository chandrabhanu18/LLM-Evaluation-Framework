"""Coverage tests for llm_judge provider paths."""
import builtins
import json
import sys
import types

import pytest

from llm_eval.metrics.llm_judge import LLMJudgeMetric


@pytest.fixture(autouse=True)
def _reset_llm_judge_cache():
    LLMJudgeMetric._cache = {}
    yield
    LLMJudgeMetric._cache = {}


def test_llm_judge_unsupported_provider():
    metric = LLMJudgeMetric({"provider": "other", "model": "x"})
    result = metric.compute("q", "e", "a", [])
    assert "Unsupported provider" in result["error"]


def test_llm_judge_anthropic_missing_key():
    metric = LLMJudgeMetric({"provider": "anthropic", "model": "x"})
    result = metric.compute("q", "e", "a", [])
    assert "API key" in result["error"]


def test_llm_judge_anthropic_success(monkeypatch):
    class DummyResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"content": [{"text": json.dumps({"coherence": 1.0, "relevance": 0.0})}]}

    def _post(*args, **kwargs):
        return DummyResp()

    monkeypatch.setenv("ANTHROPIC_KEY", "key")
    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(post=_post))

    metric = LLMJudgeMetric({
        "provider": "anthropic",
        "model": "claude",
        "api_key_env": "ANTHROPIC_KEY",
    })
    result = metric.compute("q", "e", "a", [])
    assert result["score"] == 0.5
    assert "detail" in result


def test_llm_judge_openai_import_missing(monkeypatch):
    real_import = builtins.__import__

    def _custom_import(name, *args, **kwargs):
        if name == "openai":
            raise ImportError("blocked openai")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _custom_import)
    monkeypatch.delitem(sys.modules, "openai", raising=False)
    metric = LLMJudgeMetric({"provider": "openai", "model": "gpt"})
    result = metric.compute("q", "e", "a", [])
    assert "openai package not available" in result.get("error", "")


def test_llm_judge_openai_v1_and_cache(monkeypatch):
    class DummyChoice:
        def __init__(self, content):
            self.message = types.SimpleNamespace(content=content)

    class DummyResp:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    class DummyCompletions:
        def create(self, **kwargs):
            return DummyResp('{"coherence": 1.0, "relevance": 1.0, "safety": 1.0}')

    class DummyChat:
        def __init__(self):
            self.completions = DummyCompletions()

    class DummyOpenAI:
        def __init__(self, api_key=None):
            self.chat = DummyChat()

    dummy_openai = types.SimpleNamespace(OpenAI=DummyOpenAI, api_key=None)
    monkeypatch.setitem(sys.modules, "openai", dummy_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "key")

    metric = LLMJudgeMetric({
        "provider": "openai",
        "model": "gpt",
        "api_key_env": "OPENAI_API_KEY",
    })
    result1 = metric.compute("q", "e", "a", [])
    result2 = metric.compute("q", "e", "a", [])

    assert result1["score"] == 1.0
    assert result2.get("cached") is True
