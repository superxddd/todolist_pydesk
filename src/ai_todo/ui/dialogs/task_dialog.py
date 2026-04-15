from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import simpledialog

from ai_todo.core.models import Task


class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, task: Task | None = None):
        self.task = task
        self.result_task: Task | None = None
        super().__init__(parent, title="任务编辑")

    def body(self, master):
        tk.Label(master, text="标题").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="描述").grid(row=1, column=0, sticky="w")
        tk.Label(master, text="优先级").grid(row=2, column=0, sticky="w")
        tk.Label(master, text="截止时间(YYYY-MM-DD HH:MM)").grid(row=3, column=0, sticky="w")
        tk.Label(master, text="标签(逗号分隔)").grid(row=4, column=0, sticky="w")

        self.title_var = tk.StringVar(value=self.task.title if self.task else "")
        self.desc_text = tk.Text(master, width=40, height=6)
        self.priority_var = tk.StringVar(value=self.task.priority if self.task else "medium")
        self.due_var = tk.StringVar(
            value=self.task.due_at.strftime("%Y-%m-%d %H:%M") if self.task and self.task.due_at else ""
        )
        self.tags_var = tk.StringVar(value=",".join(self.task.tags) if self.task else "")

        tk.Entry(master, textvariable=self.title_var, width=42).grid(row=0, column=1, sticky="ew", pady=2)
        self.desc_text.grid(row=1, column=1, sticky="ew", pady=2)
        self.desc_text.insert("1.0", self.task.description if self.task else "")
        tk.OptionMenu(master, self.priority_var, "high", "medium", "low").grid(row=2, column=1, sticky="w")
        tk.Entry(master, textvariable=self.due_var, width=42).grid(row=3, column=1, sticky="ew", pady=2)
        tk.Entry(master, textvariable=self.tags_var, width=42).grid(row=4, column=1, sticky="ew", pady=2)
        return master

    def apply(self):
        title = self.title_var.get().strip()
        if not title:
            return
        due_text = self.due_var.get().strip()
        due_at = datetime.strptime(due_text, "%Y-%m-%d %H:%M") if due_text else None
        task = self.task or Task.create(title=title)
        task.title = title
        task.description = self.desc_text.get("1.0", "end").strip()
        task.priority = self.priority_var.get()
        task.due_at = due_at
        task.tags = [item.strip() for item in self.tags_var.get().split(",") if item.strip()]
        task.touch()
        self.result_task = task
