import json
from pathlib import Path
import tempfile
import yaml
import pytest

from llm_eval import cli


def test_load_config_yaml_and_json(tmp_path):
    cfg = {
        "dataset": "benchmarks/rag_benchmark.jsonl",
        "output_dir": "out",
        "models": [{"name": "m","outputs": "examples/model_a_outputs.jsonl"}],
        "metrics": ["bleu"],
    }
    y = tmp_path / "c.yaml"
    j = tmp_path / "c.json"
    y.write_text(yaml.safe_dump(cfg))
    j.write_text(json.dumps(cfg))

    c1 = cli.load_config(str(y))
    c2 = cli.load_config(str(j))
    assert c1.dataset == cfg["dataset"]
    assert c2.output_dir == cfg["output_dir"]


def test_load_config_bad_extension(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("nope")
    with pytest.raises(Exception):
        cli.load_config(str(f))


def test_run_direct_invocation(tmp_path):
    # use existing example config but override output_dir to tmp
    cfg_path = Path("examples/config.yaml")
    out_dir = tmp_path / "out"
    # call run directly (not via subprocess) to exercise function body
    cli.run(config=str(cfg_path), output_dir=str(out_dir), verbose=True, models=None)
    assert out_dir.exists()
    assert (out_dir / "results.json").exists() or (out_dir / "results.md").exists()


def test_run_with_models_filter(tmp_path):
    cfg_path = Path("examples/config.yaml")
    out_dir = tmp_path / "out2"
    # filter to only model_a
    cli.run(config=str(cfg_path), output_dir=str(out_dir), verbose=False, models="model_a")
    # Ensure outputs exist and results reference only model_a in per_example
    import json
    data = json.loads((out_dir / "results.json").read_text(encoding="utf-8"))
    per = data.get("per_example", [])
    if per:
        for ex in per:
            assert set(ex["results"].keys()) <= {"model_a"}
