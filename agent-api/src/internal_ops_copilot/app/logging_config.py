from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    fmt: str  # "json" ou "kv"


class _KVFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # champs optionnels attachés via extra
        for k in ("correlation_id", "trace_id", "path", "method", "status_code", "duration_ms"):
            v = getattr(record, k, None)
            if v is not None:
                base[k] = v
        return " ".join(f"{k}={base[k]}" for k in base)


class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": int(record.created * 1000),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for k in ("correlation_id", "trace_id", "path", "method", "status_code", "duration_ms"):
            v = getattr(record, k, None)
            if v is not None:
                payload[k] = v
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(cfg: LoggingConfig) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(cfg.level)

    handler = logging.StreamHandler(sys.stdout)
    formatter: logging.Formatter = _JSONFormatter() if cfg.fmt.lower() == "json" else _KVFormatter()
    handler.setFormatter(formatter)
    root.addHandler(handler)
