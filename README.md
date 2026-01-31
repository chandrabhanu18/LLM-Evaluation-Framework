# LLM Evaluation Framework

A production-grade evaluation framework for Large Language Models (LLMs). This framework provides comprehensive metric evaluation, automated reporting, and CI/CD integration for assessing RAG pipelines, chatbots, and question-answering systems.

## Key Features

- **Command-line tool** for reproducible evaluations against benchmark datasets
- **Reference metrics**: BLEU, ROUGE-L, BERTScore (embedding-based similarity)
- **RAG-specific metrics**: Faithfulness, Context Relevancy, Answer Relevancy
- **LLM-as-a-Judge**: Multi-dimensional scoring with caching and retry logic
- **Automated reporting**: JSON, Markdown, and PNG visualizations (histograms, radar charts)
- **Docker support**: Production-ready containerization with health checks
- **CI/CD integration**: GitHub Actions workflow with coverage requirements
- **Extensible architecture**: Plugin system for custom metrics

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Metrics Reference](#metrics-reference)
- [Configuration](#configuration)
- [Custom Metrics](#custom-metrics)
- [Docker Usage](#docker-usage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Contributing](#contributing)

### Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system design, component interactions, and design patterns
- **[API_DOCS.md](API_DOCS.md)** - Complete API reference for all classes and functions

---

## Quick Start

### Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
```

2. Install the package in editable mode:

```bash
pip install -U pip
pip install -e .
```

### Running Your First Evaluation

```bash
llm-eval run --config examples/config.yaml --output-dir results --verbose
```

Optional filters:

```bash
llm-eval run --config examples/config.yaml --output-dir results --models model_a --metrics bleu,rouge_l
```

Logging control:

```bash
llm-eval run --config examples/config.yaml --output-dir results --log-level DEBUG
```

This will:
- Load the benchmark dataset from `benchmarks/rag_benchmark.jsonl`
- Evaluate model outputs using all configured metrics
- Generate reports in `results/` (JSON, Markdown, PNG charts)

---

## Architecture

The framework follows a modular, extensible design:

```
┌─────────────────────────────────────────┐
│         CLI Layer (Typer)               │
│  - Config loading (YAML/JSON)           │
│  - Argument parsing                     │
├─────────────────────────────────────────┤
│   Configuration (Pydantic)              │
│  - Type validation                      │
│  - Required field checks                │
├─────────────────────────────────────────┤
│      Evaluator (Orchestrator)           │
│  - Dataset loading                      │
│  - Metric instantiation                 │
│  - Result aggregation                   │
├──────────────┬──────────────────────────┤
│  Data Utils  │  Metrics (Abstract Base) │
│              │  - compute() interface   │
├──────────────┴──────────────────────────┤
│  Reference  │  RAG     │  LLM Judge     │
│  Metrics    │  Metrics │                │
├─────────────────────────────────────────┤
│  Reporting & Visualization              │
│  - JSON export                          │
│  - Markdown formatting                  │
│  - matplotlib plotting                  │
└─────────────────────────────────────────┘
```

### Core Components

- **CLI (`cli.py`)**: User interface, config loading, command execution
- **Configuration (`config.py`)**: Pydantic models for type-safe configuration
- **Evaluator (`evaluator.py`)**: Orchestrates evaluation pipeline
- **Metrics (`metrics/`)**: Pluggable metric implementations
  - `base.py`: Abstract Metric class defining interface
  - `reference.py`: BLEU, ROUGE-L, BERTScore
  - `rag.py`: Faithfulness, Context Relevancy, Answer Relevancy
  - `llm_judge.py`: LLM-as-a-Judge with retries and caching
- **Reporting (`reporting.py`)**: Output formatting and visualization
- **Utils (`utils.py`)**: Data loading, dataset validation

---

## Metrics Reference

### Reference-Based Metrics

#### BLEU (Bilingual Evaluation Understudy)
Measures n-gram overlap between candidate and reference answers.

- **Use case**: Machine translation, text generation quality
- **Range**: 0.0 to 1.0 (higher is better)
- **Implementation**: Uses `sacrebleu` library with 4-gram default
- **Strengths**: Fast, interpretable, widely used
- **Limitations**: Doesn't capture semantic similarity

#### ROUGE-L (Longest Common Subsequence)
Measures longest common subsequence between candidate and reference.

- **Use case**: Summarization, sequence matching
- **Range**: 0.0 to 1.0 (higher is better)
- **Implementation**: Uses `rouge_score` with stemming
- **Strengths**: Captures word order, flexible matching
- **Limitations**: May miss paraphrases

#### BERTScore (Embedding Similarity)
Computes cosine similarity between sentence embeddings.

- **Use case**: Semantic similarity, paraphrase detection
- **Range**: 0.0 to 1.0 (higher is better)
- **Implementation**: Uses `sentence-transformers` with MiniLM-L6-v2
- **Strengths**: Captures semantic meaning, handles paraphrases
- **Limitations**: Slower, requires neural model

### RAG-Specific Metrics

#### Faithfulness
Measures whether the answer is grounded in the retrieved context.

- **Purpose**: Detect hallucinations
- **Range**: 0.0 to 1.0 (higher = more faithful)
- **Calculation**: Token overlap between answer and contexts
- **Use case**: Ensuring RAG systems don't fabricate information

#### Context Relevancy
Evaluates how relevant retrieved contexts are to the query.

- **Purpose**: Assess retrieval quality
- **Range**: 0.0 to 1.0 (higher = more relevant)
- **Calculation**: Semantic similarity between query and contexts
- **Use case**: Debugging poor retrieval in RAG pipelines

#### Answer Relevancy
Measures how well the answer addresses the query.

- **Purpose**: Assess answer quality
- **Range**: 0.0 to 1.0 (higher = more relevant)
- **Calculation**: Semantic similarity between query and answer
- **Use case**: Ensuring answers are on-topic

### LLM-as-a-Judge

Multi-dimensional quality assessment using GPT-4 or Claude.

- **Dimensions**: Configurable rubric (default: coherence, relevance, safety)
- **Features**:
  - **Caching**: SHA256-based cache to reduce API calls
  - **Retry logic**: Exponential backoff (1s → 30s max)
  - **Circuit breaker**: Disables after 5 consecutive failures
  - **Temperature**: Configurable (default: 0.0 for consistency)
- **Output**: JSON object with scores per dimension
- **Use case**: Nuanced quality assessment beyond keyword matching

---

## Configuration

### Configuration File Format

The framework supports both YAML and JSON configurations. Example `config.yaml`:

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

llm_judge:
  provider: openai
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
  temperature: 0.0
  rubric:
    - coherence
    - relevance
    - safety
```

### Configuration Options

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset` | string | Yes | Path to benchmark dataset (JSONL or CSV) |
| `output_dir` | string | Yes | Directory for output files |
| `models` | list | Yes | List of models to evaluate |
| `models[].name` | string | Yes | Model identifier |
| `models[].outputs` | string | Yes | Path to model predictions (JSONL) |
| `metrics` | list | Yes | Metrics to compute |
| `llm_judge` | object | No | LLM-as-a-Judge configuration |
| `llm_judge.provider` | string | No | API provider (openai/anthropic) |
| `llm_judge.model` | string | No | Model name (gpt-4o-mini, claude-3-sonnet) |
| `llm_judge.api_key_env` | string | No | Environment variable for API key |
| `llm_judge.rubric` | list | No | Evaluation dimensions |
| `llm_judge.max_retries` | int | No | Retry attempts for API errors |
| `llm_judge.failure_threshold` | int | No | Circuit breaker threshold |
| `llm_judge.max_tokens` | int | No | Max tokens for judge responses |

### Dataset Format

Benchmark datasets must be JSONL or CSV with these required fields:

```json
{
  "query": "What is the capital of France?",
  "expected_answer": "Paris.",
  "retrieved_contexts": [
    "France's capital is Paris.",
    "Paris is known for the Eiffel Tower."
  ]
}
```

---

## Custom Metrics

### Creating a Custom Metric

1. **Define your metric class**:

```python
from llm_eval.metrics import Metric, register_metric

class MyCustomMetric(Metric):
    def __init__(self, name: str = "my_metric"):
        super().__init__(name)
        # Initialize any resources
    
    def compute(self, query: str, expected: str, answer: str, contexts):
        """
        Compute your metric.
        
        Args:
            query: User query
            expected: Reference answer
            answer: Model prediction
            contexts: Retrieved contexts (list or Any)
        
        Returns:
            Dict with 'score' key and optional details
        """
        # Your implementation
        score = your_calculation(query, expected, answer, contexts)
        return {"score": float(score)}

# Register the metric
register_metric("my_metric", MyCustomMetric)
```

2. **Use in configuration**:

```yaml
metrics:
  - my_metric
```

3. **Import before evaluation**:

```python
# In your code before loading config
from llm_eval.metrics import register_metric
from my_metrics import MyCustomMetric

register_metric("my_metric", MyCustomMetric)
```

### Metric Interface

All metrics must:
- Inherit from `Metric` base class
- Implement `compute(query, expected, answer, contexts)` method
- Return a dict with at least a `'score'` key (float between 0.0 and 1.0)
- Handle errors gracefully (return `{'error': 'message'}` on failure)

---

## Docker Usage

### Using Docker Compose

```bash
# Build and start
docker-compose up --build

# Run evaluation
docker-compose exec llm-eval llm-eval run --config examples/config.yaml --output-dir results

# Run tests
docker-compose exec llm-eval pytest tests/ --cov=llm_eval
```

### Building Docker Image

```bash
docker build -t llm-eval:latest .
docker run -v $(pwd)/results:/app/results llm-eval:latest \
  llm-eval run --config examples/config.yaml --output-dir results
```

---

## Testing

### Running Tests

```bash
# All tests with coverage
pytest --cov=llm_eval --cov-report=term-missing

# Specific test file
pytest tests/test_metrics.py -v

# With verbose output
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x
```

### Test Structure

```
tests/
├── conftest.py                     # Fixtures and configuration
├── test_cli_*.py                   # CLI testing
├── test_metrics*.py                # Metric implementations
├── test_evaluator*.py              # Evaluation pipeline
├── test_reporting.py               # Output generation
└── test_utils*.py                  # Utility functions
```

---

## Troubleshooting

### Common Issues

#### Tests Failing

**Symptom**: Some tests fail with tensor or import errors

**Solutions**:
```bash
# Ensure sentence-transformers is installed
pip install sentence-transformers

# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -e .[dev]
```

#### Docker Build Issues

**Symptom**: Docker build fails or takes too long

**Solutions**:
```bash
# Clear Docker cache
docker system prune -a

# Build with no cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs llm-eval
```

#### LLM Judge Not Working

**Symptom**: LLM-as-a-Judge returns errors or empty results

**Solutions**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Review rate limits
# OpenAI free tier: 3 requests/minute
# Consider adding delays or upgrading plan
```

#### Low Coverage

**Symptom**: Coverage below 80%

**Solutions**:
```bash
# Generate detailed coverage report
pytest --cov=llm_eval --cov-report=html
open htmlcov/index.html  # View coverage details

# Focus on missing lines
pytest --cov=llm_eval --cov-report=term-missing

# Add tests for uncovered code paths
```

#### Import Errors

**Symptom**: `ModuleNotFoundError` when running evaluation

**Solutions**:
```bash
# Install in editable mode
pip install -e .

# Verify installation
pip list | grep llm-eval

# Check Python path
python -c "import llm_eval; print(llm_eval.__file__)"
```

---

## Performance

### Benchmark Performance

Approximate computation time per 100 examples (on standard hardware):

| Metric | Time | Notes |
|--------|------|-------|
| BLEU | ~1s | Fast, regex-based |
| ROUGE-L | ~2s | Text processing |
| BERTScore | ~15s | Neural model inference |
| Faithfulness | ~3s | Token matching |
| Context Relevancy | ~30s | Embedding computation |
| Answer Relevancy | ~30s | Embedding computation |
| LLM Judge (API) | ~2-5min | Depends on API latency and rate limits |

**Total**: ~80-100 seconds for all metrics (excluding LLM Judge)

### Optimization Tips

1. **Parallel Processing**: Metrics are independent and can run in parallel
2. **Caching**: LLM Judge caches results to avoid redundant API calls
3. **Batch Processing**: BERTScore supports batch encoding (not implemented yet)
4. **GPU Acceleration**: sentence-transformers benefits from CUDA if available

---

## Development Notes

- **API Keys**: LLM-as-a-Judge requires `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- **Heavy Dependencies**: sentence-transformers (~500MB) loaded lazily
- **Test Fallbacks**: Tests include lightweight stubs for CI without heavy deps
- **Python Version**: Requires Python 3.10+ for type hints and pattern matching

---

## License

This project is MIT licensed — see `LICENSE` for details.

---

## Contributing

Contributions are welcome! Please:

1. Open an issue for bugs or feature requests
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes with tests
5. Ensure tests pass (`pytest tests/`)
6. Maintain >80% code coverage
7. Submit a pull request

### Coding Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public APIs
- Include unit tests for new features
- Keep functions focused and concise

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/llm-eval/issues)
- **Documentation**: This README and inline code comments
- **Examples**: See `examples/` directory for working configurations

---

**Version**: 0.1.0  
**Last Updated**: January 2026  
**Maintainers**: Your Team
