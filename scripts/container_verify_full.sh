#!/bin/bash
set -euo pipefail
echo "Installing runtime dependencies..."
# install required runtime libs used by the CLI and core features
python -m pip install --upgrade pip
python -m pip install 'pydantic<2.0,>=1.10' 'typer<0.10,>=0.9' pyyaml requests numpy matplotlib -q
echo "Installing wheel from /tmp/dist..."
python -m pip install --no-deps /tmp/dist/*.whl
echo "Verifying import..."
python -c "import llm_eval; print('IMPORT_OK', llm_eval.__name__)"
echo "Showing CLI help (truncated)..."
python -m llm_eval.cli --help | sed -n '1,120p'
echo "CONTAINER_FULL_VERIFY_DONE"
