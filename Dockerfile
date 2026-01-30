FROM python:3.10-slim

WORKDIR /app

# Copy only essentials
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY examples ./examples
COPY benchmarks ./benchmarks

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    pydantic typer pyyaml pandas matplotlib requests \
    sacrebleu rouge-score sentence-transformers openai && \
    pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "-m", "llm_eval.cli", "--help"]
