#!/bin/bash
set -euo pipefail
python -m pip install 'pydantic<2.0,>=1.10' 'typer<0.10,>=0.9' pyyaml pandas numpy matplotlib requests sacrebleu rouge-score -q
python - <<'PY'
from llm_eval.cli import load_config
from llm_eval.evaluator import Evaluator
cfg = load_config('examples/config.yaml')
cfg.output_dir = '/tmp/out'
e = Evaluator(cfg, verbose=True)
e.run()
print('SMOKE_DONE')
PY
