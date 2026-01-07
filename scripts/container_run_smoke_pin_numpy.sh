#!/bin/bash
set -euo pipefail
echo "Upgrading pip and installing runtime deps (pin numpy)..."
python -m pip install --upgrade pip
python -m pip install "pydantic<2.0,>=1.10" "typer<0.10,>=0.9" pyyaml requests pandas numpy==1.26.3 matplotlib sacrebleu rouge-score -q
echo "Installing wheel from /tmp/dist..."
python -m pip install --no-deps /tmp/dist/*.whl -q
echo "Running smoke evaluation..."
python -c "from llm_eval.cli import load_config; from llm_eval.evaluator import Evaluator; cfg=load_config('examples/config.yaml'); cfg.output_dir='/tmp/out'; Evaluator(cfg, verbose=True).run(); print('SMOKE_COMPLETE')"
