import subprocess
import sys
from pathlib import Path


def test_cli_help():
    res = subprocess.run([sys.executable, "-m", "llm_eval", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "run" in res.stdout or "Usage" in res.stdout or "Usage" in res.stderr


def test_cli_smoke_run(tmp_path):
    out_dir = tmp_path / "smoke"
    cmd = [
        sys.executable,
        "-m",
        "llm_eval",
        "--config",
        "examples/config.yaml",
        "--output-dir",
        str(out_dir),
    ]
    # give the CLI a reasonable timeout for CI environments
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(res.stdout)
    print(res.stderr)
    assert res.returncode == 0
    # Expect at least one output artifact from the run
    assert (out_dir / "results.json").exists() or (out_dir / "results.md").exists() or any(out_dir.glob("*.png"))
