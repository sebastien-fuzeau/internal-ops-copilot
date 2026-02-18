# agent-api (FastAPI)

## Objectifs
- API stable `/v1`
- logs structurés + correlation-id
- auth: API key + JWT (JWT activé)
- quotas/rate-limit (à venir)
- mode mock déterministe CI (à venir)

## Lancer en dev
```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash
pip install -e ".[dev]"
./scripts/dev.sh
