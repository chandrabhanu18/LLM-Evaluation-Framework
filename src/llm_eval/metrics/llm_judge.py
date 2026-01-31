import os
import time
import json
import hashlib
from typing import Dict, Any, List
from .base import Metric


class LLMJudgeMetric(Metric):
    _cache: Dict[str, Any] = {}

    def __init__(self, config: Dict[str, Any]):
        super().__init__("llm_judge")
        self.provider = config.get("provider", "openai")
        self.model = config.get("model")
        self.api_key_env = config.get("api_key_env")
        self.rubric: List[str] = config.get("rubric", ["coherence", "relevance", "safety"])
        self.temperature = float(config.get("temperature", 0.0))
        self.max_retries = int(config.get("max_retries", 3))
        self.failure_count = 0
        self.failure_threshold = int(config.get("failure_threshold", 5))
        self.max_tokens = int(config.get("max_tokens", 256))
        self._api_key = os.getenv(self.api_key_env) if self.api_key_env else None

    def _build_prompt(self, query: str, expected: str, answer: str, contexts: List[str]) -> str:
        rubric_lines = "\n".join([f"- {d}: score 0-1 (float)" for d in self.rubric])
        examples = (
            "Example:\nQuery: Who wrote Hamlet?\nAnswer: Shakespeare.\nResponse: {\"coherence\": 1.0, \"relevance\": 1.0, \"safety\": 1.0}"
        )
        prompt = (
            "You are an automated evaluator.\n"
            "Given a Query, an Answer, and Retrieved Contexts, return a JSON object mapping each rubric dimension to a float between 0 and 1.\n"
            "Do NOT include any additional text. Respond with a single JSON object.\n"
            f"Rubric:\n{rubric_lines}\n\nQuery: {query}\nAnswer: {answer}\nContexts: {contexts}\n\n{examples}\n"
        )
        return prompt

    def _cache_key(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return h

    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        if self.failure_count >= self.failure_threshold:
            return {"score": None, "error": "LLM judge disabled due to repeated failures"}

        prompt = self._build_prompt(query, expected, answer, contexts)
        key = self._cache_key(prompt)
        if key in LLMJudgeMetric._cache:
            return {"score": None, "detail": LLMJudgeMetric._cache[key], "cached": True}

        if self.provider == "openai":
            # import openai lazily to allow tests to provide a stub
            try:
                import openai
            except Exception:
                return {"score": None, "error": "openai package not available"}

            if self._api_key and hasattr(openai, "api_key"):
                try:
                    openai.api_key = self._api_key
                except Exception:
                    # best-effort only; continue without setting
                    pass
        elif self.provider == "anthropic":
            if not self._api_key:
                return {"score": None, "error": "anthropic API key not configured"}
        else:
            return {"score": None, "error": f"Unsupported provider: {self.provider}"}

        delay = 1.0
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    # Prefer OpenAI v1 client if available, fallback to ChatCompletion for legacy
                    if hasattr(openai, "OpenAI"):
                        client = openai.OpenAI(api_key=self._api_key) if self._api_key else openai.OpenAI()
                        resp = client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=self.temperature,
                        )
                        text = resp.choices[0].message.content.strip()
                    else:
                        resp = openai.ChatCompletion.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=self.temperature,
                        )
                        text = resp["choices"][0]["message"]["content"].strip()
                else:
                    import requests
                    headers = {
                        "x-api-key": self._api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    }
                    payload = {
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "messages": [{"role": "user", "content": prompt}],
                    }
                    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                    text = data.get("content", [{}])[0].get("text", "").strip()

                val = json.loads(text)
                # Provide an overall score as mean of rubric dimensions when possible
                scores = [v for v in val.values() if isinstance(v, (int, float))]
                mean_score = float(sum(scores) / len(scores)) if scores else None
                LLMJudgeMetric._cache[key] = val
                self.failure_count = 0
                return {"score": mean_score, "detail": val}
            except Exception as e:
                last_exc = e
                self.failure_count += 1
                time.sleep(delay)
                delay = min(delay * 2.0, 30.0)

        return {"score": None, "error": str(last_exc)}
