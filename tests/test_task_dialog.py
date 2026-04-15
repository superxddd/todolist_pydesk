from __future__ import annotations

import tkinter as tk
from datetime import datetime
from unittest.mock import patch

import pytest

from ai_todo.core.models import Task
from ai_todo.ui.dialogs.task_dialog import TaskDialog


class TestTaskDialogValidation:
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        yield root
        root.destroy()

    def test_validate_empty_title(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("")

        with patch("tkinter.messagebox.showwarning") as mock_msg:
            result = dialog.validate()

        assert result is False
        mock_msg.assert_called_once_with("验证失败", "标题不能为空")

    def test_validate_correct_date_format(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("Test Task")
        dialog.due_var.set("2026-04-15 14:30")

        result = dialog.validate()

        assert result is True

    def test_validate_empty_date_allowed(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("Test Task")
        dialog.due_var.set("")

        result = dialog.validate()

        assert result is True

    def test_validate_invalid_date_format(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("Test Task")
        dialog.due_var.set("2026/04/15")

        with patch("tkinter.messagebox.showerror") as mock_msg:
            result = dialog.validate()

        assert result is False
        mock_msg.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")

    def test_validate_wrong_date_format(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("Test Task")
        dialog.due_var.set("15-04-2026 14:30")

        with patch("tkinter.messagebox.showerror") as mock_msg:
            result = dialog.validate()

        assert result is False
        mock_msg.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")

    def test_validate_invalid_date_value(self, root):
        dialog = TaskDialog(root)
        dialog.title_var.set("Test Task")
        dialog.due_var.set("2026-02-30 14:30")

        with patch("tkinter.messagebox.showerror") as mock_msg:
            result = dialog.validate()

        assert result is False
        mock_msg.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")

    def test_apply_with_valid_date(self, root):
        task = Task.create(title="Old Title")
        dialog = TaskDialog(root, task=task)
        dialog.title_var.set("New Title")
        dialog.due_var.set("2026-04-15 14:30")
        dialog.desc_text.insert("1.0", "Test description")

        dialog.apply()

        assert dialog.result_task.title == "New Title"
        assert dialog.result_task.due_at == datetime(2026, 4, 15, 14, 30)
        assert dialog.result_task.description == "Test description"

    def test_apply_with_empty_date(self, root):
        task = Task.create(title="Test Task")
        dialog = TaskDialog(root, task=task)
        dialog.due_var.set("")

        dialog.apply()

        assert dialog.result_task.due_at is None
