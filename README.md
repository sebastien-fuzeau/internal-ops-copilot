# internal-ops-copilot
# Internal Ops Copilot (FastAPI prod + Spring Boot integration)

Monorepo:
- `agent-api/` : service Python FastAPI (prod-ready)
- `java-demo/` : démonstrateur Spring Boot (intégration, propagation correlation-id, gestion erreurs)

## Pré-requis
- Python 3.11+ (recommandé 3.12)
- Java 17 (Spring Boot)
- Git Bash (Windows) ou terminal Linux/macOS

## Démarrage rapide (Python)
```bash
cd agent-api
python -m venv .venv
source .venv/Scripts/activate  # Git Bash (Windows)
# ou PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
./scripts/dev.sh
