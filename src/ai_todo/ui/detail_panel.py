from __future__ import annotations

from tkinter import ttk

from ai_todo.core.models import Task


class DetailPanel(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(
            self,
            text="任务详情",
            style="Section.TLabel",
        ).pack(anchor="w", padx=8, pady=(8, 4))
        self.title_label = ttk.Label(self, text="请选择任务", font=("Segoe UI", 13, "bold"))
        self.title_label.pack(anchor="w", padx=8)
        self.meta_label = ttk.Label(self, text="", foreground="#666666")
        self.meta_label.pack(anchor="w", padx=8, pady=(0, 6))
        self.description = ttk.Label(self, text="", wraplength=420, justify="left")
        self.description.pack(anchor="w", fill="x", padx=8)
        ttk.Label(
            self,
            text="子任务",
            style="Section.TLabel",
        ).pack(anchor="w", padx=8, pady=(12, 4))
        self.subtasks = ttk.Label(self, text="", justify="left")
        self.subtasks.pack(anchor="w", fill="x", padx=8)
        ttk.Label(
            self,
            text="AI 备注",
            style="Section.TLabel",
        ).pack(anchor="w", padx=8, pady=(12, 4))
        self.ai_notes = ttk.Label(self, text="", wraplength=420, justify="left")
        self.ai_notes.pack(anchor="w", fill="x", padx=8)

    def show_task(self, task: Task | None) -> None:
        if not task:
            self.title_label.configure(text="请选择任务")
            self.meta_label.configure(text="")
            self.description.configure(text="")
            self.subtasks.configure(text="")
            self.ai_notes.configure(text="")
            return

        due = task.due_at.strftime("%Y-%m-%d %H:%M") if task.due_at else "未设置"
        tags = ", ".join(task.tags) if task.tags else "无标签"
        meta = f"状态：{task.status}  优先级：{task.priority}  截止：{due}  标签：{tags}"

        self.title_label.configure(text=task.title)
        self.meta_label.configure(text=meta)
        self.description.configure(text=task.description or "无描述")

        lines = [
            f"{'✓' if item.done else '•'} {item.title}"
            for item in task.subtasks
        ] or ["暂无子任务"]
        self.subtasks.configure(text="\n".join(lines))
        self.ai_notes.configure(text=task.ai_notes or "暂无 AI 备注")
