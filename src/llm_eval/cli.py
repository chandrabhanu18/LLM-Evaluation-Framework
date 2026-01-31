import sys
import logging
import typer
import yaml
import json
from pathlib import Path
from typing import Optional
from .config import EvalConfig
from .evaluator import Evaluator


def load_config(path: str) -> EvalConfig:
    p = Path(path)
    if not p.exists():
        raise typer.BadParameter(f"Config file not found: {path}")
    if p.suffix in (".yml", ".yaml"):
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    elif p.suffix == ".json":
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise typer.BadParameter("Config must be YAML or JSON")
    return EvalConfig(**data)


def main(
    config: str = typer.Option(..., "--config", help="Path to config YAML/JSON"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", help="Override output directory"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose logging"),
    models: Optional[str] = typer.Option(None, "--models", help="Comma-separated model names to run"),
    metrics: Optional[str] = typer.Option(None, "--metrics", help="Comma-separated metric names to run"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level (DEBUG, INFO, WARNING, ERROR)"),
):
    """LLM Evaluation Framework - Run evaluations against benchmark datasets."""
    if verbose:
        log_level = "DEBUG"
    # Convert log_level to string if it's OptionInfo
    if hasattr(log_level, "default"):
        log_level = log_level.default
    logging.basicConfig(
        level=getattr(logging, str(log_level).upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    cfg = load_config(config)
    if output_dir:
        cfg.output_dir = output_dir
    if models:
        # Handle both string and OptionInfo types
        models_str = models if isinstance(models, str) else None
        if models_str:
            selected = set([m.strip() for m in models_str.split(",")])
            cfg.models = [m for m in cfg.models if m.name in selected]
    if metrics:
        # Handle both string and OptionInfo types
        metrics_str = metrics if isinstance(metrics, str) else None
        if metrics_str:
            selected = [m.strip() for m in metrics_str.split(",") if m.strip()]
            if selected:
                cfg.metrics = selected

    evaluator = Evaluator(cfg, verbose=verbose)
    evaluator.run()


# Backwards-compatible alias for tests and direct invocation
run = main


app = typer.Typer()
app.command()(main)


if __name__ == "__main__":
    typer.run(main)
