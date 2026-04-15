from __future__ import annotations

import json
import os
from pathlib import Path

from ai_todo.core.models import AppSettings


class SettingsRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppSettings:
        if not self.file_path.exists():
            return self._apply_env_overrides(AppSettings())
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self._apply_env_overrides(AppSettings())
        return self._apply_env_overrides(AppSettings.from_dict(payload))

    def save(self, settings: AppSettings) -> AppSettings:
        self.file_path.write_text(
            json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return settings

    def _apply_env_overrides(self, settings: AppSettings) -> AppSettings:
        return settings.with_overrides(
            base_url=os.getenv("AI_TODO_BASE_URL"),
            model=os.getenv("AI_TODO_MODEL"),
            api_key=os.getenv("AI_TODO_API_KEY"),
        )
