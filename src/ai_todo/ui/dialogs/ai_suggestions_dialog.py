from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk

from ai_todo.core.models import AIPlanSuggestion, SubTask


class AISuggestionDialog(simpledialog.Dialog):
    def __init__(self, parent, suggestion: AIPlanSuggestion):
        self.suggestion = suggestion
        self.accepted = False
        self.edited_suggestion: AIPlanSuggestion | None = None
        super().__init__(parent, title="AI 建议")

    def body(self, master):
        master.columnconfigure(1, weight=1)

        ttk.Label(master, text="摘要").grid(row=0, column=0, sticky="nw", padx=(0, 8), pady=(0, 8))
        self.summary_text = tk.Text(master, width=70, height=5)
        self.summary_text.grid(row=0, column=1, sticky="nsew", pady=(0, 8))
        self.summary_text.insert("1.0", self.suggestion.summary)

        ttk.Label(master, text="优先级").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 8))
        self.priority_var = tk.StringVar(value=self.suggestion.priority)
        self.priority_combo = ttk.Combobox(
            master,
            textvariable=self.priority_var,
            values=["high", "medium", "low"],
            state="readonly",
            width=12,
        )
        self.priority_combo.grid(row=1, column=1, sticky="w", pady=(0, 8))

        ttk.Label(master, text="执行顺序").grid(
            row=2,
            column=0,
            sticky="nw",
            padx=(0, 8),
            pady=(0, 8),
        )
        self.execution_text = tk.Text(master, width=70, height=6)
        self.execution_text.grid(row=2, column=1, sticky="nsew", pady=(0, 8))
        self.execution_text.insert("1.0", "\n".join(self.suggestion.execution_order))

        ttk.Label(master, text="子任务").grid(
            row=3,
            column=0,
            sticky="nw",
            padx=(0, 8),
            pady=(0, 8),
        )
        self.subtasks_text = tk.Text(master, width=70, height=10)
        self.subtasks_text.grid(row=3, column=1, sticky="nsew", pady=(0, 8))
        self.subtasks_text.insert("1.0", "\n".join(item.title for item in self.suggestion.subtasks))

        helper = "每行一项。你可以直接改写、删减或补充内容，再点“采纳全部”。"
        ttk.Label(master, text=helper, foreground="#666666").grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
        )
        return self.summary_text

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(
            box,
            text="采纳全部",
            width=10,
            command=self._accept,
        ).pack(side="left", padx=5, pady=5)
        tk.Button(box, text="关闭", width=10, command=self.cancel).pack(side="left", padx=5, pady=5)
        box.pack()

    def _accept(self):
        summary = self.summary_text.get("1.0", "end").strip()
        priority = self.priority_var.get().strip() or "medium"
        execution_order = [
            line.strip()
            for line in self.execution_text.get("1.0", "end").splitlines()
            if line.strip()
        ]
        subtasks = [
            SubTask(title=line.strip(), done=False)
            for line in self.subtasks_text.get("1.0", "end").splitlines()
            if line.strip()
        ]
        if not subtasks:
            return
        if not execution_order:
            execution_order = [item.title for item in subtasks]
        self.edited_suggestion = AIPlanSuggestion(
            summary=summary,
            priority=priority,
            execution_order=execution_order,
            subtasks=subtasks,
        )
        self.accepted = True
        self.ok()
