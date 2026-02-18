#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-}:/$(pwd)/src"
uvicorn internal_ops_copilot.main:app --host 0.0.0.0 --port 8000 --reload
