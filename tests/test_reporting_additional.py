"""Additional reporting coverage tests."""
import builtins
from pathlib import Path

import pytest

from llm_eval import reporting


def test_save_markdown_report_empty_aggregate(tmp_path):
    report = {
        "aggregate": {},
        "per_example": [
            {
                "query": "Q1",
                "results": {
                    "model_a": {
                        "prediction": "A1",
                        "metrics": {
                            "m1": {"score": 0.5},
                            "m2": {},
                            "m3": {"x": None},
                            "m4": 0.2,
                        },
                    }
                },
            }
        ],
    }
    path = tmp_path / "report.md"
    reporting.save_markdown_report(report, path)
    text = path.read_text(encoding="utf-8")
    assert "No aggregate statistics available." in text
    assert "No scores" in text


def _block_imports(monkeypatch, names):
    real_import = builtins.__import__

    def _custom_import(name, *args, **kwargs):
        if name in names or any(name.startswith(n + ".") for n in names):
            raise ImportError(f"blocked {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _custom_import)


def test_plot_histograms_placeholder(monkeypatch, tmp_path):
    _block_imports(monkeypatch, {"matplotlib"})
    report = {
        "per_example": [
            {"results": {"model_a": {"metrics": {"m1": {"score": 0.1}}}}}
        ]
    }
    reporting.plot_histograms(report, tmp_path)
    assert (tmp_path / "hist_m1.png").exists()


def test_plot_radar_placeholder(monkeypatch, tmp_path):
    _block_imports(monkeypatch, {"numpy", "matplotlib"})
    report = {"aggregate": {"m1": {"mean": 0.2}}}
    reporting.plot_radar(report, tmp_path)
    assert (tmp_path / "radar.png").exists()
