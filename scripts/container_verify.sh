#!/bin/bash
set -euo pipefail
echo "Installing wheel from /tmp/dist..."
python -m pip install --no-deps /tmp/dist/*.whl
echo "Verifying import..."
python -c "import llm_eval; print('IMPORT_OK', llm_eval.__name__)"
echo "Showing CLI help (truncated)..."
python -m llm_eval.cli --help | sed -n '1,120p'
echo "CONTAINER_VERIFY_DONE"
