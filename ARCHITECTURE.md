# LLM Evaluation Framework - Architecture Documentation

## System Overview

The LLM Evaluation Framework is a production-grade evaluation system for Large Language Models. It follows a modular, layered architecture that enables extensibility while maintaining clean separation of concerns.

```
┌───────────────────────────────────────────────────────────────┐
│                     CLI Layer (Typer)                         │
│         Config loading • Argument parsing • Logging            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Configuration Layer (Pydantic)                    │
│      Type validation • Schema enforcement • Defaults         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│          Evaluator (Orchestrator Layer)                     │
│  Dataset loading • Metric orchestration • Result aggregation │
└──────┬──────────────────┬──────────────────────┬───────────┘
       │                  │                      │
       ▼                  ▼                      ▼
┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐
│Data Utils   │  │Metrics Layer    │  │Reporting Layer   │
│  JSONL      │  │  Base Abstract  │  │  JSON export     │
│  CSV        │  │  Reference      │  │  Markdown tables │
│  Pandas     │  │  RAG            │  │  Visualizations  │
│  Validation │  │  LLM Judge      │  │  Histograms      │
└─────────────┘  └─────────────────┘  │  Radar charts    │
                                       └──────────────────┘
```

## Core Components

### 1. CLI Layer (`cli.py`)

**Responsibility**: User interface and command routing

**Key Classes/Functions**:
- `load_config(path: str) -> EvalConfig`: Loads YAML/JSON config files
- `main(...)`: Typer command handler with options:
  - `--config`: Configuration file path (required)
  - `--output-dir`: Output directory override (optional)
  - `--verbose`: Debug logging flag (optional)
  - `--models`: Comma-separated model filter (optional)
  - `--metrics`: Comma-separated metric filter (optional)
  - `--log-level`: Logging level (optional, default: INFO)

**Design Rationale**:
- Uses Typer for type-safe CLI definition
- Supports both positional and optional arguments
- Provides backwards-compatible `run` alias for tests

### 2. Configuration Layer (`config.py`)

**Responsibility**: Configuration validation and schema enforcement

**Key Classes**:
- `ModelConfig(BaseModel)`: Defines model evaluation specification
  - `name`: Unique model identifier
  - `outputs`: Path to model predictions (JSONL)

- `LLMJudgeConfig(BaseModel)`: LLM-as-a-Judge configuration
  - `provider`: API provider (openai/anthropic)
  - `model`: Model name
  - `api_key_env`: Environment variable for credentials
  - `temperature`: Sampling temperature
  - `rubric`: Evaluation dimensions (list of strings)
  - `max_retries`: Retry attempts on API failure
  - `failure_threshold`: Circuit breaker threshold
  - `max_tokens`: Token limit for responses

- `EvalConfig(BaseModel)`: Main configuration schema
  - `dataset`: Benchmark dataset path
  - `output_dir`: Results directory
  - `models`: List of models to evaluate
  - `metrics`: List of metrics to compute
  - `llm_judge`: Optional LLM judge configuration
  - `gates`: Optional quality gates (metric thresholds)

**Design Rationale**:
- Pydantic provides runtime type validation and helpful error messages
- Validator decorators enforce business rules (e.g., non-empty metrics list)
- Supports both YAML and JSON configurations
- Enables early error detection with clear feedback

### 3. Evaluator Layer (`evaluator.py`)

**Responsibility**: Orchestrates the evaluation pipeline

**Key Class**: `Evaluator`

**Workflow**:
1. **Initialization**: Load dataset, create output directory, set up logging
2. **Metric Instantiation**: Create metric instances from config
3. **Model Output Loading**: Load predictions for each model from JSONL files
4. **Evaluation Loop**: For each example in dataset:
   - Extract query, expected answer, and contexts
   - For each model:
     - Get model prediction
     - For each metric:
       - Compute metric score
       - Capture errors if they occur
5. **Aggregation**: Calculate statistics (mean, median, std, min, max) per metric
6. **Quality Gates**: Check against configured thresholds, fail if unmet
7. **Reporting**: Generate JSON, Markdown, and visualization outputs

**Design Rationale**:
- Centralized orchestration makes pipeline easy to understand
- Metric independence enables parallel processing in future versions
- Logging at debug level provides full visibility
- Error handling per-metric allows partial evaluation on failures

### 4. Metrics Layer (`metrics/`)

**Architecture**: Abstract factory with pluggable implementations

**Base Class** (`metrics/base.py`):
```python
class Metric(ABC):
    name: str
    @abstractmethod
    def compute(self, query: str, expected: str, answer: str, contexts: Any) -> Dict[str, Any]:
        """Compute metric. Returns dict with 'score' key (0.0-1.0)."""
        pass
```

**Metric Categories**:

#### Reference-Based Metrics (`metrics/reference.py`)
- **BLEU**: N-gram overlap between candidate and reference
  - Uses: `sacrebleu.sentence_bleu()`
  - Supports: Configurable n-gram order
  - Fallback: Returns 0.0 on library unavailability

- **ROUGE-L**: Longest common subsequence overlap
  - Uses: `rouge_score.RougeScorer` with stemming
  - Fallback: Token-based overlap ratio

- **BERTScore**: Semantic similarity via embeddings
  - Uses: `sentence_transformers.SentenceTransformer`
  - Model: all-MiniLM-L6-v2 (lightweight, 90MB)
  - Fallback: Returns 0.5 when embeddings unavailable

#### RAG-Specific Metrics (`metrics/rag.py`)
- **Faithfulness**: Answer grounding in context
  - Algorithm: Jaccard similarity of answer tokens vs context tokens
  - Detects hallucinations (unsupported claims)

- **Context Relevancy**: Retrieved context relevance to query
  - Algorithm: Cosine similarity between query and context embeddings
  - Identifies retrieval quality issues

- **Answer Relevancy**: Query-answer alignment
  - Algorithm: Cosine similarity between query and answer embeddings
  - Detects off-topic responses

#### LLM-as-a-Judge (`metrics/llm_judge.py`)
- **Multi-Dimensional Assessment**: Configurable rubric (default: coherence, relevance, safety)
- **Features**:
  - **Caching**: SHA256-based prompt caching reduces API calls
  - **Retry Logic**: Exponential backoff (1s → 30s) with configurable max retries
  - **Circuit Breaker**: Disables after N consecutive failures
  - **Provider Support**: OpenAI v1 client + Anthropic HTTP API
  - **Token Control**: Configurable max_tokens for responses

**Design Rationale**:
- Abstract base enables custom metric plugins
- Factory pattern (`get_custom()`) allows dynamic metric registration
- Metric registry (`METRIC_REGISTRY`) enables centralized discovery
- Fallbacks ensure robustness even when dependencies unavailable

### 5. Data Utils Layer (`utils.py`)

**Key Functions**:
- `load_jsonl(path: str)`: Streaming JSONL file loader
- `load_dataset(path: str)`: Dataset loader with format detection
  - Supports: JSONL and CSV formats
  - Validation: Checks for required fields (query, expected_answer, retrieved_contexts)
  - Fallback: _LiteDF class provides pandas-compatible interface when pandas unavailable

**Design Rationale**:
- Lazy pandas import avoids forcing heavy dependency
- Lightweight fallback DataFrame supports offline/lightweight tests
- Consistent interface via duck typing and wrapper classes

### 6. Reporting Layer (`reporting.py`)

**Responsibilities**: Result formatting and visualization

**Functions**:
- `save_json_report(report, path)`: Structured JSON export
  - Contains: aggregate statistics + per-example results
  - Format: Programmatic parsing friendly

- `save_markdown_report(report, path)`: Human-readable markdown
  - Includes: Summary, aggregate table, insights, per-example breakdown
  - Format: Well-formatted for documentation

- `plot_histograms(report, out_dir)`: Score distribution visualization
  - One histogram per metric
  - Fallback: Creates placeholder PNG when matplotlib unavailable

- `plot_radar(report, out_dir)`: Multi-metric comparison radar chart
  - Visualizes: Aggregate mean scores per metric
  - Fallback: Creates placeholder PNG when matplotlib unavailable

**Design Rationale**:
- Separation from evaluation logic enables easy format addition
- Lazy matplotlib import avoids forcing visualization dependency
- Placeholder PNGs ensure tests pass even without plotting libraries

## Data Flow

```
┌─────────────┐
│Config (YAML)│
└──────┬──────┘
       │ load_config()
       ▼
┌──────────────────┐
│ EvalConfig       │ (validated, typed)
└──────┬───────────┘
       │
       ├─→ Dataset loading → _LiteDF or pandas DataFrame
       │
       ├─→ Model outputs loading → Dict[model_name -> predictions]
       │
       ▼
┌──────────────────────┐
│ Evaluator.run()      │
└──────┬───────────────┘
       │
       ├─→ Instantiate metrics (7 types)
       │
       ├─→ For each example:
       │    ├─→ For each model:
       │    │    ├─→ Get prediction
       │    │    └─→ For each metric: compute(query, expected, answer, contexts)
       │    └─→ Store result with error handling
       │
       ├─→ Aggregate statistics (mean, median, std, min, max)
       │
       ├─→ Check quality gates (if configured)
       │
       └─→ Generate reports (JSON, Markdown, PNG)
```

## Design Patterns

### 1. Abstract Factory (Metrics)
```python
# Plugin registration
register_metric("custom_metric", CustomMetricClass)

# Dynamic instantiation
metric = get_custom("custom_metric")()
```

**Benefits**: Extensibility without modifying core code

### 2. Dependency Injection
```python
class Evaluator:
    def __init__(self, config: EvalConfig, verbose: bool = False):
        # Config injected, enables testing with mock configs
```

**Benefits**: Testability, flexibility, loose coupling

### 3. Lazy Import Pattern
```python
try:
    import pandas
except ImportError:
    # Use lightweight fallback
```

**Benefits**: Graceful degradation, reduced startup time

### 4. Circuit Breaker (LLM Judge)
```python
if self.failure_count >= self.failure_threshold:
    return {"error": "disabled due to repeated failures"}
```

**Benefits**: Prevents cascading failures, improves resilience

### 5. Exponential Backoff (LLM Judge)
```python
delay = 1.0
for attempt in range(max_retries):
    try:
        # API call
    except:
        time.sleep(delay)
        delay = min(delay * 2.0, 30.0)
```

**Benefits**: Handles transient API failures gracefully

## Error Handling Strategy

### Configuration Errors
- **Detection**: Pydantic validation at config load time
- **Handling**: Raises clear exceptions with field names and constraints
- **Recovery**: Fail fast with helpful error message

### Runtime Errors
- **Per-Metric**: Try-catch around `compute()` captures metric-specific errors
- **Strategy**: Continue evaluation with error recorded, don't abort
- **Reporting**: Errors included in JSON/Markdown reports for analysis

### API Errors (LLM Judge)
- **Transient**: Retry with exponential backoff (1s → 30s)
- **Rate Limits**: Backoff handles 429 responses
- **Persistent**: Circuit breaker disables after N failures

### Data Errors
- **Missing Fields**: Validation during dataset load
- **Malformed JSON**: Exception caught during JSONL parsing
- **Missing Files**: File not found exceptions during loading

## Testing Strategy

**Coverage**: >80% gate enforced

**Test Categories**:
- **Unit**: Individual metric implementations with known inputs/outputs
- **Integration**: End-to-end evaluation pipeline
- **CLI**: Config loading, argument parsing, command execution
- **Data**: Dataset loading with various formats and error conditions
- **Reporting**: Output generation and formatting

**Test Fixtures** (`tests/conftest.py`):
- Mock sentence transformers (lightweight stubs)
- Mock sacrebleu (returns fixed scores)
- Mock rouge_score (returns fixed scores)

## Performance Considerations

**Metric Computation Times** (per 100 examples):
- BLEU: ~1s (regex-based)
- ROUGE-L: ~2s (string processing)
- BERTScore: ~15s (neural model)
- Faithfulness: ~3s (token matching)
- Context Relevancy: ~30s (embeddings)
- Answer Relevancy: ~30s (embeddings)
- LLM Judge: ~2-5min (API-dependent)

**Total**: ~80-100 seconds for all non-LLM metrics

**Optimization Opportunities**:
1. Parallel metric computation (metrics are independent)
2. Batch embedding computation for BERTScore
3. GPU acceleration via CUDA for sentence-transformers
4. Result caching for repeated evaluations

## Security Considerations

1. **API Keys**: Sourced from environment variables, never hardcoded
2. **Input Validation**: All configs validated at load time
3. **Dependency Isolation**: Heavy dependencies imported lazily
4. **Error Messages**: Sanitized to avoid leaking sensitive data

## Extensibility Guide

### Adding a Custom Metric

1. **Create metric class**:
```python
from llm_eval.metrics import Metric, register_metric

class MyMetric(Metric):
    def __init__(self):
        super().__init__("my_metric")
    
    def compute(self, query, expected, answer, contexts):
        score = your_calculation(...)
        return {"score": float(score)}

register_metric("my_metric", MyMetric)
```

2. **Use in config**:
```yaml
metrics:
  - my_metric
```

3. **Import before evaluation**:
```python
from my_metrics import MyMetric
```

### Adding a Custom Output Format

1. **Create formatter function**:
```python
def save_custom_report(report, path):
    # Format and write report
```

2. **Call from evaluator**:
```python
save_custom_report(report, output_path)
```

## Deployment Architecture

### Local Installation
```bash
pip install -e .
llm-eval run --config config.yaml
```

### Docker Deployment
```bash
docker-compose up
docker-compose exec llm-eval llm-eval run --config config.yaml
```

**Compose Stack**:
- Single service: `llm-eval`
- Health check: Verifies module importability
- Volume mounts: Benchmarks, examples, results
- Environment: API keys, configuration paths

## CI/CD Integration

**GitHub Actions Workflow**:
1. **Test Stage**: Run pytest with coverage gate (≥80%)
2. **Evaluation Stage**: Execute CLI on example dataset
3. **Artifacts**: Upload results for inspection
4. **Quality Gate**: Fail build if coverage < 80%

**Triggers**: Push to main/ci-run branches, PRs

## Future Enhancements

1. **Parallel Processing**: Use `multiprocessing` or `asyncio` for metric computation
2. **Distributed Evaluation**: Redis-based result aggregation for large datasets
3. **Real-time Streaming**: WebSocket API for live evaluation progress
4. **Advanced Visualization**: Interactive dashboards with Plotly
5. **Metric Composition**: Weighted combinations of base metrics
6. **Automated Benchmarking**: Performance regression detection
