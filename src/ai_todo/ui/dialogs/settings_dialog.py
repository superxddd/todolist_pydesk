from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog

from ai_todo.core.models import AppSettings


class SettingsDialog(simpledialog.Dialog):
    def __init__(self, parent, settings: AppSettings):
        self.settings = settings
        self.result_settings: AppSettings | None = None
        super().__init__(parent, title="设置")

    def body(self, master):
        labels = ["Base URL", "Model", "API Key", "提醒提前分钟数"]
        for row, label in enumerate(labels):
            tk.Label(master, text=label).grid(row=row, column=0, sticky="w")
        self.base_var = tk.StringVar(value=self.settings.base_url)
        self.model_var = tk.StringVar(value=self.settings.model)
        self.key_var = tk.StringVar(value=self.settings.api_key)
        self.reminder_var = tk.StringVar(value=str(self.settings.reminder_minutes_before))
        tk.Entry(master, textvariable=self.base_var, width=44).grid(row=0, column=1, sticky="ew", pady=2)
        tk.Entry(master, textvariable=self.model_var, width=44).grid(row=1, column=1, sticky="ew", pady=2)
        tk.Entry(master, textvariable=self.key_var, width=44, show="*").grid(row=2, column=1, sticky="ew", pady=2)
        tk.Entry(master, textvariable=self.reminder_var, width=44).grid(row=3, column=1, sticky="ew", pady=2)
        self.tray_var = tk.BooleanVar(value=self.settings.tray_enabled)
        tk.Checkbutton(master, text="启用托盘", variable=self.tray_var).grid(row=4, column=1, sticky="w")
        return master

    def apply(self):
        self.result_settings = AppSettings(
            base_url=self.base_var.get().strip(),
            model=self.model_var.get().strip(),
            api_key=self.key_var.get().strip(),
            theme=self.settings.theme,
            window_width=self.settings.window_width,
            window_height=self.settings.window_height,
            reminder_minutes_before=int(self.reminder_var.get().strip() or "30"),
            tray_enabled=self.tray_var.get(),
        )
