import sys
import types
import json
from llm_eval.metrics.llm_judge import LLMJudgeMetric


def make_openai_success():
    mod = types.SimpleNamespace()

    class ChatCompletion:
        @staticmethod
        def create(model, messages, temperature):
            return {
                "choices": [
                    {"message": {"content": json.dumps({"coherence": 0.9, "relevance": 0.8})}}
                ]
            }

    mod.ChatCompletion = ChatCompletion
    return mod


def make_openai_fail():
    mod = types.SimpleNamespace()

    class ChatCompletion:
        @staticmethod
        def create(model, messages, temperature):
            raise RuntimeError("api error")

    mod.ChatCompletion = ChatCompletion
    return mod


def test_llm_judge_success_and_cache(monkeypatch):
    sys.modules["openai"] = make_openai_success()
    cfg = {"provider": "openai", "model": "m"}
    m = LLMJudgeMetric(cfg)
    r1 = m.compute("q", "e", "a", ["c1"])
    assert "detail" in r1 or r1.get("score") is None
    # second call should hit cache
    r2 = m.compute("q", "e", "a", ["c1"])
    assert r2.get("cached", False) or isinstance(r2.get("detail"), dict)


def test_llm_judge_failure_retries(monkeypatch):
    sys.modules["openai"] = make_openai_fail()
    # reduce retry delay by patching time.sleep
    import time

    monkeypatch.setattr(time, "sleep", lambda s: None)
    cfg = {"provider": "openai", "model": "m", "max_retries": 1}
    m = LLMJudgeMetric(cfg)
    r = m.compute("q", "e", "a", [])
    assert "error" in r
