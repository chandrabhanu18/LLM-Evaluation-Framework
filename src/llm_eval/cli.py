import typer
import yaml
import json
from pathlib import Path
from typing import Optional
from .config import EvalConfig
from .evaluator import Evaluator

app = typer.Typer()


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


@app.command()
def run(
    config: str = typer.Option(..., help="Path to config YAML/JSON"),
    output_dir: Optional[str] = typer.Option(None, help="Override output directory"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose logging"),
    models: Optional[str] = typer.Option(None, help="Comma-separated model names to run"),
):
    cfg = load_config(config)
    if output_dir:
        cfg.output_dir = output_dir
    if models:
        selected = set([m.strip() for m in models.split(",")])
        cfg.models = [m for m in cfg.models if m.name in selected]

    evaluator = Evaluator(cfg, verbose=verbose)
    evaluator.run()


if __name__ == "__main__":
    app()
