from datetime import datetime, timedelta

from ai_todo.core.models import Task
from ai_todo.core.scheduler import SchedulerService


def test_scheduler_due_today_and_overdue():
    now = datetime(2026, 4, 14, 10, 0)
    scheduler = SchedulerService(now_provider=lambda: now)
    due_today = Task.create("Today task", due_at=now + timedelta(hours=2))
    overdue = Task.create("Old task", due_at=now - timedelta(hours=1))
    result_today = scheduler.due_today([due_today, overdue])
    result_overdue = scheduler.overdue([due_today, overdue])
    assert result_today[0].title == "Today task"
    assert result_overdue[0].title == "Old task"
