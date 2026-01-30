FROM python:3.10-slim

WORKDIR /app

# Copy only essentials
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY examples ./examples
COPY benchmarks ./benchmarks

# Install minimal dependencies with pre-built wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --only-binary :all: \
    pydantic typer pyyaml pandas matplotlib requests && \
    pip install --no-cache-dir sacrebleu rouge-score && \
    pip install --no-cache-dir -e . || true

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:$PYTHONPATH

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from llm_eval.cli import load_config; print('ok')" || exit 1

CMD ["python", "-m", "llm_eval.cli", "--help"]
