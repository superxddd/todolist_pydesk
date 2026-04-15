from __future__ import annotations

from collections.abc import Iterable

from ai_todo.core.models import Task

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def filter_tasks(
    tasks: Iterable[Task],
    query: str = "",
    status: str = "all",
    tag: str = "",
) -> list[Task]:
    lowered = query.strip().lower()
    result: list[Task] = []
    for task in tasks:
        if status != "all" and task.status != status:
            continue
        if tag and tag not in task.tags:
            continue
        haystack = " ".join([task.title, task.description, " ".join(task.tags)]).lower()
        if lowered and lowered not in haystack:
            continue
        result.append(task)
    return sorted(result, key=sort_key)


def sort_key(task: Task) -> tuple[int, int, str]:
    due_rank = 0 if task.due_at else 1
    return (PRIORITY_ORDER.get(task.priority, 99), due_rank, task.title.lower())
