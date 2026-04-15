from __future__ import annotations

from datetime import datetime, timedelta

from ai_todo.core.models import ReminderItem, Task


class SchedulerService:
    def __init__(self, now_provider=None) -> None:
        self._now_provider = now_provider or datetime.now

    def now(self) -> datetime:
        return self._now_provider().replace(microsecond=0)

    def due_today(self, tasks: list[Task]) -> list[Task]:
        today = self.now().date()
        return [task for task in tasks if task.due_at and task.due_at.date() == today]

    def overdue(self, tasks: list[Task]) -> list[Task]:
        now = self.now()
        return [task for task in tasks if task.due_at and task.due_at < now and task.status != "done"]

    def completed_today(self, tasks: list[Task]) -> list[Task]:
        today = self.now().date()
        return [task for task in tasks if task.status == "done" and task.updated_at.date() == today]

    def reminders(self, tasks: list[Task], minutes_before: int) -> list[ReminderItem]:
        now = self.now()
        future_limit = now + timedelta(minutes=minutes_before)
        result: list[ReminderItem] = []
        for task in tasks:
            if not task.due_at or task.status == "done":
                continue
            if now <= task.due_at <= future_limit or task.due_at < now:
                result.append(
                    ReminderItem(
                        task_id=task.id,
                        title=task.title,
                        due_at=task.due_at,
                        status="overdue" if task.due_at < now else "upcoming",
                    )
                )
        return result
