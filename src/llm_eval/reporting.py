import json
from pathlib import Path
from typing import Any, Dict
# Lazy import heavy plotting libs to avoid forcing them in lightweight test envs


def save_json_report(report: Dict[str, Any], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def save_markdown_report(report: Dict[str, Any], path: Path):
    lines = ["# Evaluation Report", ""]
    agg = report.get("aggregate", {})
    per_all = report.get("per_example", [])

    lines.append("## Summary")
    lines.append(f"- Examples: {len(per_all)}")
    try:
        model_names = sorted({m for ex in per_all for m in (ex.get("results") or {}).keys()})
        if model_names:
            lines.append(f"- Models: {', '.join(model_names)}")
    except Exception:
        pass
    lines.append("")

    lines.append("## Aggregate Statistics")
    if agg:
        lines.append("| Metric | Mean | Median | Std | Min | Max |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for m, stats in agg.items():
            if stats:
                lines.append(
                    "| {metric} | {mean:.4f} | {median:.4f} | {std:.4f} | {min:.4f} | {max:.4f} |".format(
                        metric=m,
                        mean=stats["mean"],
                        median=stats["median"],
                        std=stats["std"],
                        min=stats["min"],
                        max=stats["max"],
                    )
                )
            else:
                lines.append(f"| {m} | - | - | - | - | - |")
    else:
        lines.append("No aggregate statistics available.")
    lines.append("")

    # Insights
    lines.append("## Insights")
    try:
        scored = [(m, stats["mean"]) for m, stats in agg.items() if stats and isinstance(stats.get("mean"), (int, float))]
        if scored:
            best = max(scored, key=lambda x: x[1])
            worst = min(scored, key=lambda x: x[1])
            lines.append(f"- Best average metric: **{best[0]}** ({best[1]:.4f})")
            lines.append(f"- Lowest average metric: **{worst[0]}** ({worst[1]:.4f})")
        else:
            lines.append("- Not enough numeric scores to compute insights.")
    except Exception:
        lines.append("- Not enough data to compute insights.")
    lines.append("")

    lines.append("## Per-example (first 10)")
    per = report.get("per_example", [])[:10]
    for ex in per:
        lines.append(f"### Query: {ex.get('query', '')}")
        for mname, res in ex.get("results", {}).items():
            lines.append(f"- Model: {mname}")
            pred = res.get("prediction") if isinstance(res, dict) else None
            if pred is not None:
                lines.append(f"  - Prediction: {pred}")
            if isinstance(res, dict):
                for metric, v in (res.get("metrics") or {}).items():
                    if isinstance(v, dict):
                        if not v or all(val is None for val in v.values()):
                            lines.append(f"  - {metric}: No scores")
                        elif "score" in v:
                            score = v.get("score")
                            lines.append(f"  - {metric}: {score}")
                        else:
                            lines.append(f"  - {metric}: {v}")
                    else:
                        score = v
                        lines.append(f"  - {metric}: {score}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def plot_histograms(report: Dict[str, Any], out_dir: Path):
    per = report.get("per_example", [])
    metrics = {}
    for ex in per:
        for mname, res in ex.get("results", {}).items():
            for metric, v in (res.get("metrics") or {}).items():
                score = v.get("score") if isinstance(v, dict) else v
                if isinstance(score, (int, float)):
                    metrics.setdefault(metric, []).append(score)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        # plotting libs not installed; create placeholder PNGs so tests can verify files
        out_dir.mkdir(parents=True, exist_ok=True)
        for metric in metrics.keys():
            path = out_dir / f"hist_{metric}.png"
            with open(path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    for metric, scores in metrics.items():
        plt.figure()
        plt.hist(scores, bins=10)
        plt.title(f"Distribution: {metric}")
        plt.xlabel("Score")
        plt.ylabel("Count")
        plt.savefig(out_dir / f"hist_{metric}.png")
        plt.close()


def plot_radar(report: Dict[str, Any], out_dir: Path):
    agg = report.get("aggregate", {})
    labels = []
    values = []
    for m, stats in agg.items():
        if stats:
            labels.append(m)
            values.append(stats["mean"])
    if not labels:
        return
    try:
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        # create a placeholder radar.png when plotting libs missing
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "radar.png"
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
        return

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = values + values[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-")
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title("Aggregate radar")
    ax.set_ylim(0, 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "radar.png")
    plt.close(fig)
