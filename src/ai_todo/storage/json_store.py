from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_todo.core.models import Task
from ai_todo.storage.migrations import TASKS_SCHEMA_VERSION, normalize_tasks_payload
from ai_todo.storage.sample_data import build_sample_tasks


class TaskRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_payload(
                {"app_version": TASKS_SCHEMA_VERSION, "tasks": [task.to_dict() for task in build_sample_tasks()]}
            )

    def _read_payload(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            payload = {"app_version": TASKS_SCHEMA_VERSION, "tasks": []}
        return normalize_tasks_payload(payload)

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def list(self) -> list[Task]:
        payload = self._read_payload()
        return [Task.from_dict(item) for item in payload["tasks"]]

    def get(self, task_id: str) -> Task | None:
        for task in self.list():
            if task.id == task_id:
                return task
        return None

    def save(self, task: Task) -> Task:
        tasks = self.list()
        replaced = False
        for index, current in enumerate(tasks):
            if current.id == task.id:
                tasks[index] = task
                replaced = True
                break
        if not replaced:
            tasks.append(task)
        self._write_payload({"app_version": TASKS_SCHEMA_VERSION, "tasks": [item.to_dict() for item in tasks]})
        return task

    def delete(self, task_id: str) -> None:
        tasks = [task for task in self.list() if task.id != task_id]
        self._write_payload({"app_version": TASKS_SCHEMA_VERSION, "tasks": [item.to_dict() for item in tasks]})

    def bulk_update(self, tasks: list[Task]) -> None:
        self._write_payload({"app_version": TASKS_SCHEMA_VERSION, "tasks": [item.to_dict() for item in tasks]})
