$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "$pwd\src"
uvicorn internal_ops_copilot.main:app --host 0.0.0.0 --port 8000 --reload
