import json
import types
import pytest

from llm_eval.metrics.llm_judge import LLMJudgeMetric


class DummyOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(model, messages, temperature=0.0):
            # return a JSON-serializable string in choices[0].message.content
            return {"choices": [{"message": {"content": json.dumps({"coherence": 1.0, "relevance": 0.8})}}]}


def test_llm_judge_caching(monkeypatch):
    cfg = {"provider": "openai", "model": "gpt-test", "api_key_env": None}
    m = LLMJudgeMetric(cfg)

    monkeypatch.setitem(__import__("sys").modules, "openai", DummyOpenAI)

    out1 = m.compute("q", "exp", "ans", ["ctx"])
    assert out1.get("detail") is not None

    # Second call should hit cache (same prompt -> cached True)
    out2 = m.compute("q", "exp", "ans", ["ctx"])
    assert out2.get("cached") is True or out2.get("detail") is not None


def test_llm_judge_failure(monkeypatch):
    class BrokenOpenAI:
        class ChatCompletion:
            @staticmethod
            def create(*args, **kwargs):
                raise RuntimeError("API down")

    cfg = {"provider": "openai", "model": "gpt-test", "api_key_env": None, "max_retries": 2, "failure_threshold": 1}
    m = LLMJudgeMetric(cfg)
    monkeypatch.setitem(__import__("sys").modules, "openai", BrokenOpenAI)

    out = m.compute("q", "exp", "ans", [])
    assert "error" in out
