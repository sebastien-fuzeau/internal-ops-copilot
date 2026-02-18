from __future__ import annotations

import logging
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from internal_ops_copilot.app.config import Settings, get_settings

log_auth = logging.getLogger("auth")


@dataclass(frozen=True)
class AuthContext:
    subject: str
    auth_type: str  # "api_key" | "jwt"


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail)


def _forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=403, detail=detail)


_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    api_key: str | None = Security(_api_key_header),
    bearer: HTTPAuthorizationCredentials | None = Security(_bearer),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    if not api_key:
        log_auth.info("auth_failed", extra={"reason": "missing_api_key"})
        raise _unauthorized("Missing API key")

    if api_key not in settings.api_key_set():
        log_auth.info("auth_failed", extra={"reason": "invalid_api_key"})
        raise _forbidden("Invalid API key")

    if settings.jwt_enabled and bearer and bearer.credentials:
        token = bearer.credentials
        try:
            payload = jwt.decode(
                token,
                key=settings.jwt_secret,
                algorithms=[settings.jwt_alg],
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience,
                options={"require": ["exp", "sub", "iss", "aud"]},
            )
        except jwt.ExpiredSignatureError:
            log_auth.info("auth_failed", extra={"reason": "jwt_expired"})
            raise _unauthorized("JWT expired") from None
        except jwt.InvalidTokenError:
            log_auth.info("auth_failed", extra={"reason": "jwt_invalid"})
            raise _unauthorized("Invalid JWT") from None

        sub = str(payload.get("sub"))
        log_auth.info("auth_ok", extra={"auth_type": "jwt", "subject": sub})
        return AuthContext(subject=sub, auth_type="jwt")

    subj = f"api_key:{api_key[-6:]}"
    log_auth.info("auth_ok", extra={"auth_type": "api_key", "subject": subj})
    return AuthContext(subject=subj, auth_type="api_key")
