from datetime import datetime
from unittest.mock import MagicMock, patch

from ai_todo.ui.dialogs.task_dialog import TaskDialog


class TestTaskDialogDueDateValidation:
    """测试任务对话框的截止时间格式验证"""

    def test_apply_with_valid_due_date(self):
        """测试输入正确格式的截止时间"""
        parent = MagicMock()
        dialog = TaskDialog(parent, task=None)
        dialog.title_var = MagicMock()
        dialog.title_var.get.return_value = "测试任务"
        dialog.due_var = MagicMock()
        dialog.due_var.get.return_value = "2024-12-25 14:30"
        dialog.desc_text = MagicMock()
        dialog.desc_text.get.return_value = "描述"
        dialog.priority_var = MagicMock()
        dialog.priority_var.get.return_value = "medium"
        dialog.tags_var = MagicMock()
        dialog.tags_var.get.return_value = ""

        with patch.object(dialog, "destroy"):
            dialog.apply()

        assert dialog.result_task is not None
        assert dialog.result_task.due_at == datetime(2024, 12, 25, 14, 30)

    def test_apply_with_empty_due_date(self):
        """测试空截止时间（应允许保存，表示不设置截止时间）"""
        parent = MagicMock()
        dialog = TaskDialog(parent, task=None)
        dialog.title_var = MagicMock()
        dialog.title_var.get.return_value = "测试任务"
        dialog.due_var = MagicMock()
        dialog.due_var.get.return_value = "   "  # 只有空格
        dialog.desc_text = MagicMock()
        dialog.desc_text.get.return_value = "描述"
        dialog.priority_var = MagicMock()
        dialog.priority_var.get.return_value = "medium"
        dialog.tags_var = MagicMock()
        dialog.tags_var.get.return_value = ""

        with patch.object(dialog, "destroy"):
            dialog.apply()

        assert dialog.result_task is not None
        assert dialog.result_task.due_at is None

    def test_apply_with_invalid_due_date_format(self):
        """测试错误格式的截止时间（应显示错误提示，不保存任务）"""
        parent = MagicMock()
        dialog = TaskDialog(parent, task=None)
        dialog.title_var = MagicMock()
        dialog.title_var.get.return_value = "测试任务"
        dialog.due_var = MagicMock()
        dialog.due_var.get.return_value = "2024/12/25 14:30"  # 错误格式
        dialog.desc_text = MagicMock()
        dialog.desc_text.get.return_value = "描述"
        dialog.priority_var = MagicMock()
        dialog.priority_var.get.return_value = "medium"
        dialog.tags_var = MagicMock()
        dialog.tags_var.get.return_value = ""

        with patch("ai_todo.ui.dialogs.task_dialog.messagebox.showerror") as mock_error:
            dialog.apply()

        # 应该调用 showerror 显示错误
        mock_error.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")
        # result_task 应该为 None，因为 apply 被中断
        assert dialog.result_task is None

    def test_apply_with_incomplete_due_date(self):
        """测试不完整的截止时间（缺少时间部分）"""
        parent = MagicMock()
        dialog = TaskDialog(parent, task=None)
        dialog.title_var = MagicMock()
        dialog.title_var.get.return_value = "测试任务"
        dialog.due_var = MagicMock()
        dialog.due_var.get.return_value = "2024-12-25"  # 缺少时间
        dialog.desc_text = MagicMock()
        dialog.desc_text.get.return_value = "描述"
        dialog.priority_var = MagicMock()
        dialog.priority_var.get.return_value = "medium"
        dialog.tags_var = MagicMock()
        dialog.tags_var.get.return_value = ""

        with patch("ai_todo.ui.dialogs.task_dialog.messagebox.showerror") as mock_error:
            dialog.apply()

        mock_error.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")
        assert dialog.result_task is None

    def test_apply_with_invalid_date_values(self):
        """测试无效的日期值（如 13月）"""
        parent = MagicMock()
        dialog = TaskDialog(parent, task=None)
        dialog.title_var = MagicMock()
        dialog.title_var.get.return_value = "测试任务"
        dialog.due_var = MagicMock()
        dialog.due_var.get.return_value = "2024-13-01 12:00"  # 13月无效
        dialog.desc_text = MagicMock()
        dialog.desc_text.get.return_value = "描述"
        dialog.priority_var = MagicMock()
        dialog.priority_var.get.return_value = "medium"
        dialog.tags_var = MagicMock()
        dialog.tags_var.get.return_value = ""

        with patch("ai_todo.ui.dialogs.task_dialog.messagebox.showerror") as mock_error:
            dialog.apply()

        mock_error.assert_called_once_with("格式错误", "截止时间格式应为 YYYY-MM-DD HH:MM")
        assert dialog.result_task is None
