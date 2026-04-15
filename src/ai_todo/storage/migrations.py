from __future__ import annotations

from typing import Any

TASKS_SCHEMA_VERSION = "0.1.0"


def normalize_tasks_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "app_version" not in payload:
        payload["app_version"] = TASKS_SCHEMA_VERSION
    if "tasks" not in payload:
        payload["tasks"] = []
    return payload
