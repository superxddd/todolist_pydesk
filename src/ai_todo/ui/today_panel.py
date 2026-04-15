from __future__ import annotations

from tkinter import ttk

from ai_todo.core.models import Task


class TodayPanel(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="今日视图", style="Section.TLabel").pack(anchor="w", padx=8, pady=(8, 4))
        self.summary = ttk.Label(self, text="今日概览")
        self.summary.pack(anchor="w", padx=8, pady=(0, 8))
        self.today_box = ttk.Label(self, text="", justify="left")
        self.today_box.pack(anchor="w", fill="x", padx=8)

    def update_sections(self, due_today: list[Task], overdue: list[Task], completed: list[Task]) -> None:
        text = [
            f"今日到期：{len(due_today)}",
            f"已逾期：{len(overdue)}",
            f"今日完成：{len(completed)}",
            "",
            "建议先做：",
        ]
        top = overdue[:2] + due_today[:3]
        if top:
            text.extend([f"- {task.title}" for task in top])
        else:
            text.append("- 暂无")
        self.today_box.configure(text="\n".join(text))
