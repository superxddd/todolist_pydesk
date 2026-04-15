from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_todo.storage.paths import AppPaths, default_paths


@dataclass(slots=True)
class AppConfig:
    paths: AppPaths
    app_name: str = "AI Todo Manager"
    window_title: str = "AI Todo Manager"
    reminder_poll_ms: int = 60_000
    test_mode: bool = False

    @classmethod
    def for_runtime(cls, test_mode: bool = False, root: Path | None = None) -> "AppConfig":
        return cls(paths=default_paths(root=root), test_mode=test_mode)
