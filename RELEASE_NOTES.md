LLM Evaluation Framework — Release notes
=====================================

Release: local build for submission
Date: 2026-01-07

Artifacts produced
------------------
- Wheel: dist/llm_eval-0.1.0-py3-none-any.whl
  - SHA256: C7773F02EF023E47959EE452813353CFA336B02B69F8ED7E0CD5F4CBB2D9DDBF
- Source: dist/llm_eval-0.1.0.tar.gz
  - SHA256: 329AF88A7F96D1673EF6EA4E47F3A80826E7D7B5AD4E8D064BACDC70E1981D67
- Clean repo ZIP: llm-eval-final-repo.zip
  - SHA256: 9c8fb52ad2610c1b321497a442f5d95279abd0ddcf0d7d0e7a3639b8c1a1fa81

Verification steps performed
----------------------------
1. Ran test suite: `pytest --cov=llm_eval` — 55 passed, coverage 100%.
2. Built sdist & wheel with `python -m build`.
3. Verified wheel import in temporary install and inside CI container.
4. Built `llm-eval-ci:local` (from `Dockerfile.ci`) and executed `scripts/container_run_smoke_pin_numpy.sh` which installed runtime deps, the wheel, and ran a full evaluation (SMOKE_COMPLETE).

Known considerations
--------------------
- LLM-judge requires API credentials to exercise in CI or locally; it is disabled unless configured.
- Some native wheels (e.g., numpy) may require suitable platform/build toolchain; CI used pinned wheels for reproducible smoke runs.

How to reproduce locally
------------------------
1. Create venv and install dev deps:

```bash
python -m venv .venv
.venv/bin/activate       # or .venv\Scripts\Activate.ps1 on Windows
pip install -U pip
pip install -e .[dev]
```

2. Run tests:

```bash
pytest --cov=llm_eval
```

3. Build artifacts:

```bash
python -m build
```

4. Run Docker smoke (example):

```bash
docker build -f Dockerfile.ci -t llm-eval-ci:local .
docker run --rm -v "$(pwd):/work" -v "$(pwd)/dist:/tmp/dist:ro" -w /work llm-eval-ci:local /work/scripts/container_run_smoke_pin_numpy.sh
```

Contact / Maintainers
---------------------
Please update `pyproject.toml` with the accurate `authors`, `repository`, and `homepage` entries before publishing to PyPI.
