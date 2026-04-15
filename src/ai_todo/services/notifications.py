from __future__ import annotations

from tkinter import messagebox

from ai_todo.core.models import ReminderItem


class NotificationService:
    def notify(self, item: ReminderItem) -> None:
        message = f"任务：{item.title}\n截止时间：{item.due_at:%Y-%m-%d %H:%M}"
        if item.status == "overdue":
            message = "任务已逾期\n" + message
        else:
            message = "任务即将到期\n" + message
        try:
            messagebox.showinfo("AI Todo 提醒", message)
        except Exception:
            pass
