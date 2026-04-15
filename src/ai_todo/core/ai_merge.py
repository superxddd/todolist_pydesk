from __future__ import annotations

from ai_todo.core.models import AIPlanSuggestion, Task


def apply_ai_suggestion(
    task: Task,
    suggestion: AIPlanSuggestion,
    overwrite_priority: bool = True,
) -> Task:
    task.subtasks = suggestion.subtasks
    task.ai_notes = suggestion.summary
    if overwrite_priority and suggestion.priority:
        task.priority = suggestion.priority
    task.touch()
    return task
