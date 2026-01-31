# LLM Evaluation Framework - API Documentation

Complete API reference for the LLM Evaluation Framework.

## Module: `llm_eval.cli`

### `load_config(path: str) -> EvalConfig`

Load and validate configuration from YAML or JSON file.

**Parameters**:
- `path` (str): File path to config (`.yaml`, `.yml`, or `.json`)

**Returns**:
- `EvalConfig`: Validated configuration object

**Raises**:
- `typer.BadParameter`: If file not found or format unsupported
- `ValidationError`: If config doesn't match schema

**Example**:
```python
from llm_eval.cli import load_config

cfg = load_config("config.yaml")
print(cfg.dataset)  # "benchmarks/rag_benchmark.jsonl"
```

### `main(...)`

Main CLI entry point. Can be called directly or via Typer CLI.

**Parameters**:
- `config` (str, required): Path to config file
- `output_dir` (str, optional): Override output directory
- `verbose` (bool, optional): Enable debug logging
- `models` (str, optional): Comma-separated model names to run
- `metrics` (str, optional): Comma-separated metric names to run
- `log_level` (str, optional): Logging level (DEBUG/INFO/WARNING/ERROR)

**Returns**: None (exits with code 0 on success, 2 on quality gate failure)

**Example**:
```python
from llm_eval.cli import run

run(
    config="examples/config.yaml",
    output_dir="results",
    verbose=True,
    models="model_a,model_b",
    metrics="bleu,rouge_l,bertscore"
)
```

### `run(...)`

Backwards-compatible alias for `main()`. Provided for test compatibility.

**Identical to `main()`** - see above.

## Module: `llm_eval.config`

### `ModelConfig`

Pydantic model defining a model evaluation specification.

**Fields**:
- `name` (str): Unique model identifier
- `outputs` (str): Path to JSONL file with model predictions

**Example**:
```python
from llm_eval.config import ModelConfig

model = ModelConfig(name="gpt-4", outputs="outputs/gpt4.jsonl")
```

### `LLMJudgeConfig`

Pydantic model for LLM-as-a-Judge configuration.

**Fields**:
- `provider` (str): API provider ("openai" or "anthropic")
- `model` (str): Model name (e.g., "gpt-4o-mini", "claude-3-sonnet")
- `api_key_env` (str, optional): Environment variable for API key
- `temperature` (float, default=0.0): Sampling temperature (0.0-1.0)
- `rubric` (List[str], default=["coherence", "relevance", "safety"]): Evaluation dimensions
- `max_retries` (int, default=3): Retry attempts on API failure
- `failure_threshold` (int, default=5): Circuit breaker threshold
- `max_tokens` (int, default=256): Token limit for judge responses

**Example**:
```python
from llm_eval.config import LLMJudgeConfig

judge = LLMJudgeConfig(
    provider="openai",
    model="gpt-4o-mini",
    api_key_env="OPENAI_API_KEY",
    rubric=["coherence", "relevance", "safety", "factuality"]
)
```

### `EvalConfig`

Pydantic model for main evaluation configuration.

**Fields**:
- `dataset` (str): Path to benchmark dataset (JSONL or CSV)
- `output_dir` (str): Directory for output files
- `models` (List[ModelConfig]): Models to evaluate
- `metrics` (List[str]): Metrics to compute
- `llm_judge` (LLMJudgeConfig, optional): LLM judge configuration
- `gates` (dict, optional): Quality gates (metric name → threshold)

**Validators**:
- `metrics_not_empty`: Ensures metrics list is non-empty

**Example**:
```python
from llm_eval.config import EvalConfig, ModelConfig

cfg = EvalConfig(
    dataset="benchmarks/data.jsonl",
    output_dir="results",
    models=[
        ModelConfig(name="model_a", outputs="model_a.jsonl"),
        ModelConfig(name="model_b", outputs="model_b.jsonl")
    ],
    metrics=["bleu", "rouge_l", "bertscore", "faithfulness"],
    gates={"bleu": 0.5, "rouge_l": 0.6}
)
```

## Module: `llm_eval.evaluator`

### `Evaluator`

Main evaluation orchestrator.

**Constructor**:
```python
__init__(config: EvalConfig, verbose: bool = False)
```

**Parameters**:
- `config` (EvalConfig): Evaluation configuration
- `verbose` (bool, default=False): Enable debug logging

**Attributes**:
- `logger` (logging.Logger): Logger instance
- `config` (EvalConfig): Configuration
- `verbose` (bool): Verbosity flag
- `dataset`: Loaded benchmark dataset
- `dataset_size` (int): Number of examples in dataset

**Methods**:

#### `run() -> dict`

Execute complete evaluation pipeline.

**Returns**:
```python
{
    "aggregate": {
        "metric_name": {
            "mean": float,
            "median": float,
            "std": float,
            "min": float,
            "max": float
        },
        ...
    },
    "per_example": [
        {
            "query": str,
            "expected_answer": str,
            "results": {
                "model_name": {
                    "prediction": str,
                    "metrics": {
                        "metric_name": {"score": float, ...}
                    }
                }
            }
        },
        ...
    ]
}
```

**Raises**:
- `SystemExit(2)`: If quality gates fail
- `ValueError`: If metric instantiation fails

**Side Effects**:
- Writes JSON report to `output_dir/results.json`
- Writes Markdown report to `output_dir/results.md`
- Writes histograms to `output_dir/hist_*.png`
- Writes radar chart to `output_dir/radar.png`

**Example**:
```python
from llm_eval.config import EvalConfig
from llm_eval.evaluator import Evaluator

cfg = EvalConfig(...)
evaluator = Evaluator(cfg, verbose=True)
report = evaluator.run()
print(f"BLEU mean: {report['aggregate']['bleu']['mean']:.4f}")
```

## Module: `llm_eval.metrics.base`

### `Metric` (Abstract Base Class)

All metrics must inherit from this class.

**Attributes**:
- `name` (str): Metric identifier

**Methods**:

#### `__init__(name: str)`

Initialize metric with identifier.

#### `compute(query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]`

**Abstract method** - must be implemented by subclasses.

**Parameters**:
- `query` (str): User query
- `expected` (str): Reference/expected answer
- `answer` (str): Model prediction
- `contexts` (Any): Retrieved contexts (list of strings or single string)

**Returns**:
```python
{
    "score": float,  # Required: score between 0.0-1.0
    "error": str,    # Optional: error message if computation failed
    ...              # Optional: additional fields (e.g., "cached": True)
}
```

**Example**:
```python
from llm_eval.metrics.base import Metric

class CustomMetric(Metric):
    def __init__(self):
        super().__init__("custom")
    
    def compute(self, query, expected, answer, contexts):
        score = len(answer) / max(1, len(expected))
        return {"score": float(score)}
```

## Module: `llm_eval.metrics.reference`

### `BleuMetric`

BLEU (Bilingual Evaluation Understudy) score implementation.

**Constructor**:
```python
__init__(name: str = "bleu", ngram: int = 4)
```

**Parameters**:
- `name` (str, default="bleu"): Metric identifier
- `ngram` (int, default=4): N-gram order (1-4 typical)

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

### `RougeLMetric`

ROUGE-L (Longest Common Subsequence) implementation.

**Constructor**:
```python
__init__(name: str = "rouge_l")
```

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

### `BertSimMetric`

Semantic similarity via BERTScore (embedding-based).

**Constructor**:
```python
__init__(name: str = "bertscore", model_name: str = "all-MiniLM-L6-v2")
```

**Parameters**:
- `name` (str, default="bertscore"): Metric identifier
- `model_name` (str, default="all-MiniLM-L6-v2"): Sentence transformer model

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

## Module: `llm_eval.metrics.rag`

### `FaithfulnessMetric`

Measures answer grounding in retrieved contexts.

**Constructor**:
```python
__init__(name: str = "faithfulness")
```

**Algorithm**: Jaccard similarity of answer tokens vs context tokens

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

### `ContextRelevancyMetric`

Measures relevance of retrieved contexts to query.

**Constructor**:
```python
__init__(name: str = "context_relevancy", model_name: str = "all-MiniLM-L6-v2")
```

**Algorithm**: Cosine similarity between query and context embeddings

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

### `AnswerRelevancyMetric`

Measures how well answer addresses the query.

**Constructor**:
```python
__init__(name: str = "answer_relevancy", model_name: str = "all-MiniLM-L6-v2")
```

**Algorithm**: Cosine similarity between query and answer embeddings

**Returns** (from `compute()`):
```python
{"score": float}  # 0.0-1.0
```

## Module: `llm_eval.metrics.llm_judge`

### `LLMJudgeMetric`

Multi-dimensional evaluation using GPT-4 or Claude.

**Constructor**:
```python
__init__(config: Dict[str, Any])
```

**Parameters**:
- `config` (dict): LLMJudgeConfig as dictionary

**Attributes**:
- `provider` (str): API provider
- `model` (str): Model name
- `rubric` (List[str]): Evaluation dimensions
- `temperature` (float): Sampling temperature
- `max_retries` (int): Retry attempts
- `failure_count` (int): Current failure count
- `failure_threshold` (int): Circuit breaker threshold
- `max_tokens` (int): Token limit

**Returns** (from `compute()`):
```python
{
    "score": float,  # Mean of rubric dimension scores
    "detail": {
        "coherence": float,
        "relevance": float,
        "safety": float,
        ...
    },
    "cached": bool,  # True if result from cache
    "error": str     # Error message if failed
}
```

**Features**:
- **Caching**: SHA256-based prompt caching
- **Retries**: Exponential backoff (1s → 30s)
- **Circuit Breaker**: Disables after N failures
- **Providers**: OpenAI (v1 client) and Anthropic (HTTP API)

## Module: `llm_eval.metrics`

### `register_metric(name: str, constructor: Callable)`

Register custom metric for plugin system.

**Parameters**:
- `name` (str): Metric identifier
- `constructor` (Callable): Callable that returns metric instance

**Example**:
```python
from llm_eval.metrics import register_metric

class MyMetric:
    def __init__(self):
        self.name = "my_metric"
    
    def compute(self, query, expected, answer, contexts):
        return {"score": 0.5}

register_metric("my_metric", MyMetric)
```

### `get_custom(name: str) -> Callable`

Retrieve registered custom metric constructor.

**Parameters**:
- `name` (str): Metric identifier

**Returns**:
- Constructor callable or None if not found

## Module: `llm_eval.utils`

### `load_jsonl(path: str) -> Iterable[Dict[str, Any]]`

Streaming JSONL file loader.

**Parameters**:
- `path` (str): Path to JSONL file

**Yields**:
- Dict: Each line parsed as JSON

**Raises**:
- `FileNotFoundError`: If file not found
- `json.JSONDecodeError`: If line is invalid JSON

**Example**:
```python
from llm_eval.utils import load_jsonl

for item in load_jsonl("data.jsonl"):
    print(item["query"])
```

### `load_dataset(path: str) -> Any`

Dataset loader with format detection and validation.

**Parameters**:
- `path` (str): Path to dataset (`.jsonl` or `.csv`)

**Returns**:
- Pandas DataFrame or lightweight _LiteDF object

**Required Fields**:
- `query` (str): User query
- `expected_answer` (str): Reference answer
- `retrieved_contexts` (list): Retrieved context documents

**Raises**:
- `FileNotFoundError`: If file not found
- `ValueError`: If file format unsupported or required fields missing

**Example**:
```python
from llm_eval.utils import load_dataset

df = load_dataset("benchmarks/data.jsonl")
print(f"Loaded {df.shape[0]} examples")
```

## Module: `llm_eval.reporting`

### `save_json_report(report: Dict[str, Any], path: Path)`

Save evaluation results as JSON.

**Parameters**:
- `report` (dict): Report dictionary from `Evaluator.run()`
- `path` (Path): Output file path

**File Format**:
```json
{
  "aggregate": {
    "bleu": {"mean": 0.75, "median": 0.80, "std": 0.1, "min": 0.5, "max": 0.95}
  },
  "per_example": [
    {
      "query": "...",
      "expected_answer": "...",
      "results": {
        "model_a": {
          "prediction": "...",
          "metrics": {"bleu": {"score": 0.75}}
        }
      }
    }
  ]
}
```

### `save_markdown_report(report: Dict[str, Any], path: Path)`

Save evaluation results as formatted Markdown.

**Parameters**:
- `report` (dict): Report dictionary from `Evaluator.run()`
- `path` (Path): Output file path

**Includes**:
- Summary (example count, models)
- Aggregate statistics table
- Insights (best/worst metrics)
- Per-example breakdown (first 10)

### `plot_histograms(report: Dict[str, Any], out_dir: Path)`

Generate histogram visualizations for each metric.

**Parameters**:
- `report` (dict): Report dictionary from `Evaluator.run()`
- `out_dir` (Path): Output directory

**Output**:
- PNG files: `out_dir/hist_{metric_name}.png`

**Fallback**: Creates placeholder PNG if matplotlib unavailable

### `plot_radar(report: Dict[str, Any], out_dir: Path)`

Generate radar chart comparing metrics.

**Parameters**:
- `report` (dict): Report dictionary from `Evaluator.run()`
- `out_dir` (Path): Output directory

**Output**:
- PNG file: `out_dir/radar.png`

**Fallback**: Creates placeholder PNG if matplotlib unavailable

## Configuration File Examples

### Minimal Configuration (YAML)

```yaml
dataset: benchmarks/data.jsonl
output_dir: results
models:
  - name: model_a
    outputs: model_a_outputs.jsonl
metrics:
  - bleu
  - rouge_l
```

### Complete Configuration with LLM Judge (YAML)

```yaml
dataset: benchmarks/rag_benchmark.jsonl
output_dir: results

models:
  - name: model_a
    outputs: examples/model_a_outputs.jsonl
  - name: model_b
    outputs: examples/model_b_outputs.jsonl

metrics:
  - bleu
  - rouge_l
  - bertscore
  - faithfulness
  - context_relevancy
  - answer_relevancy
  - llm_judge

llm_judge:
  provider: openai
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
  temperature: 0.0
  rubric:
    - coherence
    - relevance
    - safety
  max_retries: 3
  max_tokens: 256

gates:
  bleu: 0.5
  rouge_l: 0.6
```

## Error Handling

### Configuration Errors

**Cause**: Invalid configuration file

**Example Error**:
```
ValidationError: 1 validation error for EvalConfig
metrics
  ensure this value has at least 1 item (type=value_error.list.min_items)
```

**Solution**: Verify config.yaml has all required fields

### Metric Errors

**Cause**: Metric computation failure

**Handling**: Error is captured, metric marked as failed

**Example Output**:
```json
{
  "bleu": {"error": "sacrebleu library not installed"}
}
```

### Quality Gate Failures

**Cause**: Aggregate metric below threshold

**Example Error**: Exit code 2 when metric mean < threshold

**Solution**: Adjust gates or improve model performance

### API Errors (LLM Judge)

**Cause**: API rate limit, auth failure, or service outage

**Handling**:
1. Retry with exponential backoff (1s → 30s)
2. After N failures, disable LLM judge (circuit breaker)
3. Return `{"error": "API error message"}`

## Performance Tips

1. **Cache Results**: LLM judge caches based on prompt SHA256
2. **Batch Processing**: Use multiple models to amortize overhead
3. **Metric Filtering**: Run only needed metrics with `--metrics` flag
4. **GPU Support**: sentence-transformers uses CUDA if available

## Testing Utilities

All tests use fixtures from `tests/conftest.py`:

```python
# Mock sentence transformers
DummySTModel: Lightweight embedding model returning fixed vectors

# Mock external libraries
fake_sacre: Returns fixed BLEU scores
fake_rouge: Returns fixed ROUGE scores
```

Tests should not require actual models or API keys.
