from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ModelConfig(BaseModel):
    name: str
    outputs: str


class LLMJudgeConfig(BaseModel):
    provider: str = Field(...)
    model: str = Field(...)
    api_key_env: Optional[str] = None
    temperature: float = 0.0
    rubric: List[str] = Field(default_factory=lambda: ["coherence", "relevance", "safety"])
    max_retries: int = 3
    failure_threshold: int = 5
    max_tokens: int = 256


class EvalConfig(BaseModel):
    dataset: str
    output_dir: str
    models: List[ModelConfig]
    metrics: List[str]
    llm_judge: Optional[LLMJudgeConfig] = None
    gates: Optional[dict] = None

    @validator("metrics")
    def metrics_not_empty(cls, v):
        if not v:
            raise ValueError("metrics must be non-empty")
        return v
