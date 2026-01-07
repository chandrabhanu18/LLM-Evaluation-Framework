from pathlib import Path
from llm_eval.reporting import save_json_report, save_markdown_report, plot_histograms, plot_radar


def test_reporting_and_plots(tmp_path):
    report = {
        "aggregate": {"bleu": {"mean": 0.9, "median": 0.9, "std": 0.01, "min": 0.8, "max": 1.0}},
        "per_example": [
            {"query": "q1", "expected_answer": "a1", "results": {"m": {"metrics": {"bleu": {"score": 0.9}}}}}
        ],
    }
    out_json = tmp_path / "r.json"
    out_md = tmp_path / "r.md"
    save_json_report(report, out_json)
    save_markdown_report(report, out_md)
    assert out_json.exists()
    assert out_md.exists()

    plot_histograms(report, tmp_path)
    plot_radar(report, tmp_path)
    assert any(p.suffix == ".png" for p in tmp_path.iterdir())
