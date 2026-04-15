from ai_todo.core.ai_merge import apply_ai_suggestion
from ai_todo.core.models import AIPlanSuggestion, SubTask, Task


def test_apply_ai_suggestion():
    task = Task.create("Launch project", priority="low")
    suggestion = AIPlanSuggestion(
        summary="Need to split work",
        priority="high",
        execution_order=["Define scope"],
        subtasks=[SubTask(title="Define scope"), SubTask(title="Prepare demo")],
    )
    updated = apply_ai_suggestion(task, suggestion)
    assert updated.priority == "high"
    assert len(updated.subtasks) == 2
