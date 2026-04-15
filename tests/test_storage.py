from pathlib import Path

from ai_todo.core.models import Task
from ai_todo.storage.json_store import TaskRepository
from ai_todo.storage.settings_store import SettingsRepository


def test_task_repository_save_and_delete(tmp_path: Path):
    repo = TaskRepository(tmp_path / "tasks.json")
    task = Task.create("Ship release")
    repo.save(task)
    assert repo.get(task.id) is not None
    repo.delete(task.id)
    assert repo.get(task.id) is None


def test_settings_repository_roundtrip(tmp_path: Path):
    repo = SettingsRepository(tmp_path / "settings.json")
    settings = repo.load()
    settings.model = "test-model"
    repo.save(settings)
    assert repo.load().model == "test-model"
