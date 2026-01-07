# LLM Evaluation Framework

A lightweight, production-oriented evaluation framework for Large Language Models (LLMs). This project provides a CLI to run reproducible evaluations, reference and RAG-focused metrics, LLM-as-a-judge integration, reporting in JSON/Markdown, and visualization outputs.

Key features
- Command-line tool to run evaluations against benchmark datasets and model outputs.
- Reference metrics: BLEU, ROUGE-L, embedding-based similarity.
- RAG-focused metrics: faithfulness, context relevancy, answer relevancy.
- LLM-as-a-judge support with caching and retries (configure via API key).
- JSON/Markdown export and PNG visualizations (histograms, radar charts).
- Dockerfile and CI-friendly image for reproducible smoke tests.

Quick start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
```

2. Install the package in editable mode and dev tools:

```bash
pip install -U pip
pip install -e .[dev]
```

3. Run the example evaluation (writes outputs to `results/`):

```bash
llm-eval run --config examples/config.yaml --output-dir results --verbose
```

Docker (CI smoke)

The repository includes `Dockerfile.ci` and a convenience script `scripts/docker_smoke.sh` that installs runtime dependencies inside the CI image and runs a smoke evaluation using the example config.

```bash
docker build -f Dockerfile.ci -t llm-eval-ci:local .
docker run --rm -v "$(pwd):/work" -w /work llm-eval-ci:local /work/scripts/docker_smoke.sh
```

Testing

Run the full test suite with coverage:

```bash
pytest --cov=llm_eval --cov-report=term-missing
```

Development notes
- To enable the LLM-as-a-judge metric, set your provider API key (e.g. `OPENAI_API_KEY`) and configure the `llm_judge` block in the example config.
- Heavy optional dependencies (sentence-transformers, large native wheels) are loaded lazily; tests include lightweight fallbacks so CI can run on minimal images.

License

This project is MIT licensed — see `LICENSE` for details.

Contributing

Contributions are welcome. Please open issues for bugs or feature requests, and submit PRs for improvements. Maintain coding and test coverage standards when adding modules.
# LLM Evaluation Framework

This repository contains a production-ready LLM evaluation framework. Use the CLI `llm-eval` to run evaluations with example configs and benchmarks.

Quick start:

```bash
pip install -e .
llm-eval run --config examples/config.yaml --output-dir results
```

Or with Docker Compose:

```bash
docker-compose up --build
```
 
Notes:
- To enable the LLM-as-a-judge feature, set the environment variable specified in your `examples/config.yaml` (e.g. `OPENAI_API_KEY`) and configure the `llm_judge` model block.
- Tests are run with `pytest tests/` and require Python 3.10+.
