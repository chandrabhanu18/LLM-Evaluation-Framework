"""Tests for module entrypoint."""
import runpy
import typer


def test_module_entrypoint_runs_typer(monkeypatch):
    called = []

    def _fake_run(fn):
        called.append(fn)

    monkeypatch.setattr(typer, "run", _fake_run)
    runpy.run_module("llm_eval.__main__", run_name="__main__")
    assert called, "typer.run should be invoked"
