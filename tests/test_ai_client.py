import pytest

from ai_todo.core.models import AppSettings, Task
from ai_todo.services.ai_client import AIClient


def test_validate_config():
    client = AIClient()
    invalid = client.validate_config(AppSettings())
    assert not invalid.ok
    valid = client.validate_config(
        AppSettings(base_url="https://example.com/v1", model="gpt-4.1-mini", api_key="secret")
    )
    assert valid.ok


def test_parse_suggestion_from_markdown_json():
    client = AIClient()
    suggestion = client._parse_suggestion(
        """```json
{"summary":"test","priority":"high","execution_order":["a"],"subtasks":[{"title":"step 1","done":false}]}
```"""
    )
    assert suggestion.priority == "high"
    assert suggestion.subtasks[0].title == "step 1"


def test_parse_suggestion_falls_back_to_subtasks_when_execution_order_missing():
    client = AIClient()
    suggestion = client._parse_suggestion(
        '{"summary":"test","priority":"urgent","subtasks":[{"title":"step 1","done":false},{"title":"step 2","done":false}]}'
    )
    assert suggestion.priority == "medium"
    assert suggestion.execution_order == ["step 1", "step 2"]


def test_generate_task_plan_requires_config():
    client = AIClient()
    with pytest.raises(ValueError):
        client.generate_task_plan(Task.create("Demo"), AppSettings())


def test_parse_task_from_ai_response():
    client = AIClient()
    task = client._parse_task(
        '{"title":"测试豆包模型","description":"验证接入结果并记录","priority":"high","due_at":"","tags":["测试","模型"],"subtasks":[{"title":"准备测试环境","done":false}],"summary":"先完成验证再整理结果"}',
        "今天测一下模型",
    )
    assert task.title == "测试豆包模型"
    assert task.priority == "high"
    assert task.tags == ["测试", "模型"]
    assert task.subtasks[0].title == "准备测试环境"
