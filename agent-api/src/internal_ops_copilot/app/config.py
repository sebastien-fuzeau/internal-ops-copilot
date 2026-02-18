from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    log_format: str = "json"  # "json" ou "kv"
    log_level: str = "INFO"

    # Auth
    api_keys: str = "dev-key-1"
    jwt_enabled: bool = True
    jwt_issuer: str = "internal-ops"
    jwt_audience: str = "internal-users"
    jwt_jwks_url: str = ""
    jwt_secret: str = "dev-secret-change-me"

    def api_key_set(self) -> set[str]:
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}


def get_settings() -> Settings:
    # Pas de cache global ici (on gardera cela explicite plus tard si utile)
    return Settings()
