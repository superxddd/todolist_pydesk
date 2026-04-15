from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppPaths:
    root_dir: Path
    tasks_file: Path
    settings_file: Path
    backups_dir: Path

    def ensure(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)


def default_paths(root: Path | None = None) -> AppPaths:
    base = root or Path.home() / "AppData" / "Local" / "AITodoManager"
    return AppPaths(
        root_dir=base,
        tasks_file=base / "tasks.json",
        settings_file=base / "settings.json",
        backups_dir=base / "backups",
    )
