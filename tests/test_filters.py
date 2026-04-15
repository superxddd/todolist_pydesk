from ai_todo.core.filters import filter_tasks
from ai_todo.core.models import Task


def test_filter_tasks_by_query_and_status():
    tasks = [
        Task.create("Prepare release", tags=["github"]),
        Task.create("Buy snacks", tags=["life"]),
    ]
    tasks[0].status = "doing"
    result = filter_tasks(tasks, query="release", status="doing")
    assert len(result) == 1
    assert result[0].title == "Prepare release"
