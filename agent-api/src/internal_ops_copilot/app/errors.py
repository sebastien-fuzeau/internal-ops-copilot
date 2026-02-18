from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorPayload:
    code: str
    message: str


def err(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}
