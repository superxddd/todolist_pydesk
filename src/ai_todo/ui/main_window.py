from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from ai_todo.core.ai_merge import apply_ai_suggestion
from ai_todo.core.filters import filter_tasks
from ai_todo.core.models import AppSettings, Task
from ai_todo.ui.detail_panel import DetailPanel
from ai_todo.ui.dialogs.ai_suggestions_dialog import AISuggestionDialog
from ai_todo.ui.dialogs.settings_dialog import SettingsDialog
from ai_todo.ui.dialogs.task_dialog import TaskDialog
from ai_todo.ui.task_list import TaskListPanel
from ai_todo.ui.today_panel import TodayPanel


class MainWindow:
    def __init__(
        self,
        root: tk.Tk,
        repository,
        settings_repository,
        scheduler,
        ai_client,
        notification_service,
        tray_service,
        settings: AppSettings,
    ) -> None:
        self.root = root
        self.repository = repository
        self.settings_repository = settings_repository
        self.scheduler = scheduler
        self.ai_client = ai_client
        self.notification_service = notification_service
        self.tray_service = tray_service
        self.settings = settings
        self.current_task: Task | None = None
        self._last_notified: set[str] = set()

        self.root.title("AI Todo Manager")
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        self._setup_styles()
        self._build_layout()
        self.refresh()

    def _setup_styles(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Section.TLabel", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x", padx=8, pady=8)
        actions = [
            ("AI 快速添加", self.ai_quick_add),
            ("新建任务", self.create_task),
            ("编辑任务", self.edit_task),
            ("完成任务", self.mark_done),
            ("删除任务", self.delete_task),
            ("AI 拆解", self.generate_ai_plan),
            ("设置", self.open_settings),
        ]
        for text, command in actions:
            ttk.Button(toolbar, text=text, command=command).pack(side="left", padx=(0, 6))

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=2)
        body.rowconfigure(0, weight=1)

        self.task_list = TaskListPanel(body, self.select_task)
        self.task_list.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))
        self.detail_panel = DetailPanel(body)
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=4, pady=(0, 8))
        self.today_panel = TodayPanel(body)
        self.today_panel.grid(row=0, column=2, sticky="nsew", padx=(4, 8), pady=(0, 8))

        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status_label.pack(fill="x", padx=8, pady=(0, 8))

    def refresh(self) -> None:
        tasks = self.repository.list()
        filtered = filter_tasks(
            tasks,
            query=self.task_list.search_var.get(),
            status=self.task_list.status_var.get(),
        )
        self.task_list.set_tasks(filtered)
        if self.current_task:
            self.current_task = self.repository.get(self.current_task.id)
        self.detail_panel.show_task(self.current_task)
        self.today_panel.update_sections(
            self.scheduler.due_today(tasks),
            self.scheduler.overdue(tasks),
            self.scheduler.completed_today(tasks),
        )
        self._notify_due_items(tasks)
        self.status_var.set(f"任务总数：{len(tasks)}")

    def _notify_due_items(self, tasks: list[Task]) -> None:
        for item in self.scheduler.reminders(tasks, self.settings.reminder_minutes_before):
            if item.task_id in self._last_notified:
                continue
            self.notification_service.notify(item)
            self._last_notified.add(item.task_id)

    def select_task(self, task: Task | None, refresh_only: bool = False) -> None:
        if refresh_only:
            self.refresh()
            return
        self.current_task = task
        self.detail_panel.show_task(task)

    def create_task(self) -> None:
        dialog = TaskDialog(self.root)
        if dialog.result_task:
            self.repository.save(dialog.result_task)
            self.refresh()

    def ai_quick_add(self) -> None:
        prompt = (
            "直接告诉 AI 你接下来要做什么。\n"
            "例如：今天下午把 trae 的豆包模型接入测完，并整理一份结果。"
        )
        user_input = simpledialog.askstring("AI 快速添加", prompt, parent=self.root)
        if not user_input:
            return
        try:
            task = self.ai_client.generate_task_from_input(user_input, self.settings)
        except Exception as exc:
            messagebox.showerror("AI 生成失败", str(exc))
            return

        preview = [
            f"标题：{task.title}",
            f"优先级：{task.priority}",
            f"截止时间：{task.due_at.strftime('%Y-%m-%d %H:%M') if task.due_at else '未设置'}",
            f"标签：{', '.join(task.tags) if task.tags else '无'}",
            "",
            f"描述：{task.description or '无'}",
        ]
        if task.subtasks:
            preview.extend(["", "子任务：", *[f"- {item.title}" for item in task.subtasks]])
        if task.ai_notes:
            preview.extend(["", f"AI 备注：{task.ai_notes}"])

        confirm_text = "\n".join(preview) + "\n\n是否加入待办列表？"
        if messagebox.askyesno("确认添加任务", confirm_text):
            self.repository.save(task)
            self.current_task = task
            self.refresh()

    def edit_task(self) -> None:
        if not self._require_selection():
            return
        dialog = TaskDialog(self.root, task=self.current_task)
        if dialog.result_task:
            self.repository.save(dialog.result_task)
            self.current_task = dialog.result_task
            self.refresh()

    def mark_done(self) -> None:
        if not self._require_selection():
            return
        self.current_task.status = "done"
        self.current_task.touch()
        self.repository.save(self.current_task)
        self.refresh()

    def delete_task(self) -> None:
        if not self._require_selection():
            return
        if messagebox.askyesno("确认删除", f"确定删除任务“{self.current_task.title}”吗？"):
            self.repository.delete(self.current_task.id)
            self.current_task = None
            self.refresh()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.root, self.settings)
        if dialog.result_settings:
            self.settings = self.settings_repository.save(dialog.result_settings)
            self.status_var.set("设置已保存")

    def generate_ai_plan(self) -> None:
        if not self._require_selection():
            return
        try:
            suggestion = self.ai_client.generate_task_plan(self.current_task, self.settings)
        except Exception as exc:
            messagebox.showerror("AI 调用失败", str(exc))
            return
        dialog = AISuggestionDialog(self.root, suggestion)
        if dialog.accepted:
            final_suggestion = dialog.edited_suggestion or suggestion
            apply_ai_suggestion(self.current_task, final_suggestion)
            self.repository.save(self.current_task)
            self.refresh()

    def _require_selection(self) -> bool:
        if self.current_task:
            return True
        messagebox.showinfo("提示", "请先选择任务。")
        return False
