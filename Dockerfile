FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev || true
COPY . /app
RUN pip install -e .

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD python -c "import importlib; importlib.import_module('llm_eval'); print('ok')"

CMD ["llm-eval", "--help"]
