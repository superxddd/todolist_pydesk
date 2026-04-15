from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path

from ai_todo.app.config import AppConfig
from ai_todo.core.scheduler import SchedulerService
from ai_todo.services.ai_client import AIClient
from ai_todo.services.backup import BackupService
from ai_todo.services.logging_service import configure_logging
from ai_todo.services.notifications import NotificationService
from ai_todo.services.tray import TrayCallbacks, TrayService
from ai_todo.storage.json_store import TaskRepository
from ai_todo.storage.settings_store import SettingsRepository
from ai_todo.ui.main_window import MainWindow


@dataclass(slots=True)
class ApplicationContext:
    config: AppConfig
    repository: TaskRepository
    settings_repository: SettingsRepository
    scheduler: SchedulerService
    ai_client: AIClient
    notification_service: NotificationService
    tray_service: TrayService
    backup_service: BackupService


def build_application(test_mode: bool = False, data_root: Path | None = None) -> ApplicationContext:
    config = AppConfig.for_runtime(test_mode=test_mode, root=data_root)
    config.paths.ensure()
    logger = configure_logging()
    logger.info("Starting AI Todo application")
    return ApplicationContext(
        config=config,
        repository=TaskRepository(config.paths.tasks_file),
        settings_repository=SettingsRepository(config.paths.settings_file),
        scheduler=SchedulerService(),
        ai_client=AIClient(),
        notification_service=NotificationService(),
        tray_service=TrayService(),
        backup_service=BackupService(config.paths.backups_dir),
    )


def create_main_window(context: ApplicationContext) -> tuple[tk.Tk, MainWindow]:
    root = tk.Tk()
    settings = context.settings_repository.load()
    window = MainWindow(
        root=root,
        repository=context.repository,
        settings_repository=context.settings_repository,
        scheduler=context.scheduler,
        ai_client=context.ai_client,
        notification_service=context.notification_service,
        tray_service=context.tray_service,
        settings=settings,
    )
    root.protocol("WM_DELETE_WINDOW", lambda: _shutdown(root, context.tray_service))
    if settings.tray_enabled:
        context.tray_service.start(
            TrayCallbacks(
                show_main_window=lambda: root.after(0, _restore_window, root),
                quit_application=lambda: root.after(0, root.destroy),
            )
        )
    return root, window


def _restore_window(root: tk.Tk) -> None:
    root.deiconify()
    root.lift()
    root.focus_force()


def _shutdown(root: tk.Tk, tray_service: TrayService) -> None:
    tray_service.stop()
    root.destroy()
