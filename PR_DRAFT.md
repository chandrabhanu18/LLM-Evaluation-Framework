Title: Add production-ready LLM evaluation framework (ci-run)

Description
-----------
This PR prepares the `ci-run` branch for review and submission. It includes:

- Full implementation of the LLM evaluation framework under `src/llm_eval`.
- CLI (`llm-eval`) with Typer-based commands and example config in `examples/config.yaml`.
- Reference metrics (BLEU, ROUGE-L, embedding sim), RAG metrics, and LLM-as-a-judge integration.
- Reporting (JSON, Markdown) and PNG visualizations.
- Tests with coverage tooling; current test suite passes locally with 100% coverage.
- CI-focused Dockerfile (`Dockerfile.ci`) and container smoke scripts in `scripts/`.
- Packaging metadata (`pyproject.toml`) and built artifacts in `dist/`.

Checklist (to verify before merging)
-----------------------------------
- [ ] Project metadata reviewed (authors, repository URL) in `pyproject.toml`.
- [ ] Confirm license and contribution guidelines are acceptable (`LICENSE`).
- [ ] Local tests: `pytest --cov=llm_eval` — 100% coverage (verified locally).
- [ ] Built artifacts present in `dist/` and verified import from wheel.
    - Wheel: `dist/llm_eval-0.1.0-py3-none-any.whl` (SHA256: C7773F02EF023E47959EE452813353CFA336B02B69F8ED7E0CD5F4CBB2D9DDBF)
    - Sdist: `dist/llm_eval-0.1.0.tar.gz` (SHA256: 329AF88A7F96D1673EF6EA4E47F3A80826E7D7B5AD4E8D064BACDC70E1981D67)
- [ ] Clean repository ZIP created: `llm-eval-final-repo.zip` (SHA256: 9c8fb52ad2610c1b321497a442f5d95279abd0ddcf0d7d0e7a3639b8c1a1fa81)
- [ ] Docker CI smoke: `Dockerfile.ci` builds and `scripts/container_run_smoke_pin_numpy.sh` runs end-to-end (verified: SMOKE_COMPLETE).
- [ ] Confirm no test-only stubs remain at repo root (tests use monkeypatch where needed).
- [ ] Confirm README and `pyproject.toml` metadata updated (authors/repo/homepage).

Notes for reviewers
-------------------
- The LLM-judge requires an API key (e.g., `OPENAI_API_KEY`) to be set in the environment when used. The judge is optional and gated via config.
- Heavy optional dependencies are loaded lazily; CI installation may choose to install runtime deps as shown in container scripts.
- I did not push this branch remotely; please review and let me know if you want me to push `ci-run` and open the PR.
