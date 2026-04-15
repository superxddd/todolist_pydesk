from ai_todo.core.models import AppSettings, SubTask, Task


def test_task_roundtrip():
    task = Task.create("Write docs", "Prepare docs", tags=["docs"])
    task.subtasks = [SubTask(title="README")]
    clone = Task.from_dict(task.to_dict())
    assert clone.title == "Write docs"
    assert clone.subtasks[0].title == "README"


def test_settings_defaults():
    settings = AppSettings.from_dict({"model": "gpt-4.1-mini"})
    assert settings.model == "gpt-4.1-mini"
    assert settings.theme == "light"
