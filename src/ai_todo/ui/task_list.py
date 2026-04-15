from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ai_todo.core.models import Task


class TaskListPanel(ttk.Frame):
    def __init__(self, master, on_select, **kwargs):
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self.tasks: list[Task] = []

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="all")

        ttk.Label(
            self,
            text="任务列表",
            style="Section.TLabel",
        ).pack(anchor="w", padx=8, pady=(8, 4))
        search_entry = ttk.Entry(self, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=8)
        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.on_select(None, refresh_only=True),
        )

        status_box = ttk.Combobox(
            self,
            textvariable=self.status_var,
            values=["all", "todo", "doing", "done"],
            state="readonly",
        )
        status_box.pack(fill="x", padx=8, pady=8)
        status_box.bind(
            "<<ComboboxSelected>>",
            lambda _event: self.on_select(None, refresh_only=True),
        )

        self.listbox = tk.Listbox(self, activestyle="dotbox")
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._handle_select)

    def set_tasks(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.listbox.delete(0, tk.END)
        for task in tasks:
            due = f" [{task.due_at:%m-%d %H:%M}]" if task.due_at else ""
            self.listbox.insert(tk.END, f"{task.title} ({task.priority}){due}")

    def _handle_select(self, _event) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        self.on_select(self.tasks[selection[0]])
