from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil


class BackupService:
    def __init__(self, backups_dir: Path) -> None:
        self.backups_dir = backups_dir
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, source: Path) -> Path | None:
        if not source.exists():
            return None
        target = self.backups_dir / f"{source.stem}-{datetime.now():%Y%m%d-%H%M%S}{source.suffix}"
        shutil.copy2(source, target)
        return target
