from __future__ import annotations

from datetime import timedelta

from ai_todo.core.models import SubTask, Task, utc_now


def build_sample_tasks() -> list[Task]:
    now = utc_now()
    task = Task.create(
        title="准备 GitHub 发布版桌面 Todo",
        description="整理 README、截图、标签和发布说明。",
        priority="high",
        due_at=now + timedelta(days=1),
        tags=["发布", "桌面应用"],
    )
    task.subtasks = [
        SubTask(title="补充 README"),
        SubTask(title="检查 GitHub Actions"),
        SubTask(title="打一个 v0.1.0 tag"),
    ]
    return [
        task,
        Task.create(
            title="配置 AI 接口",
            description="在设置页填写 Base URL、Model 和 API Key。",
            priority="medium",
            due_at=now + timedelta(days=2),
            tags=["AI"],
        ),
    ]
