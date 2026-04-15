from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests

from ai_todo.core.models import AIPlanSuggestion, AppSettings, SubTask, Task


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    message: str


class AIClient:
    def validate_config(self, settings: AppSettings) -> ValidationResult:
        if not settings.base_url.strip():
            return ValidationResult(False, "Base URL 不能为空。")
        if not settings.model.strip():
            return ValidationResult(False, "Model 不能为空。")
        if not settings.api_key.strip():
            return ValidationResult(False, "API Key 不能为空。")
        return ValidationResult(True, "配置有效。")

    def generate_task_plan(self, task: Task, settings: AppSettings) -> AIPlanSuggestion:
        validation = self.validate_config(settings)
        if not validation.ok:
            raise ValueError(validation.message)

        payload = {
            "model": settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一个严谨的任务规划助手。"
                        "你的目标不是概括任务，而是把任务拆成可以立刻执行的细粒度步骤。"
                        "输出必须是严格 JSON，不要输出 Markdown，不要输出解释。"
                    ),
                },
                {"role": "user", "content": self._build_plan_prompt(task)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        content = self._chat_completion(payload, settings)
        return self._parse_suggestion(content)

    def generate_task_from_input(self, user_input: str, settings: AppSettings) -> Task:
        validation = self.validate_config(settings)
        if not validation.ok:
            raise ValueError(validation.message)
        if not user_input.strip():
            raise ValueError("请输入你接下来要做什么。")

        payload = {
            "model": settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一个 Todo 助手。"
                        "用户会用自然语言说自己接下来要做什么。"
                        "你要把它整理成一条可直接加入待办列表的任务。"
                        "输出必须是严格 JSON。"
                    ),
                },
                {"role": "user", "content": self._build_capture_prompt(user_input)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        content = self._chat_completion(payload, settings)
        return self._parse_task(content, user_input)

    def prioritize_tasks(self, tasks: list[Task], settings: AppSettings) -> AIPlanSuggestion:
        pseudo_task = Task.create(
            title="今日任务排序",
            description="\n".join(
                f"- 标题: {task.title} | 优先级: {task.priority} | 截止: {task.due_at or '未设置'}"
                for task in tasks
            ),
        )
        return self.generate_task_plan(pseudo_task, settings)

    def _chat_completion(self, payload: dict[str, Any], settings: AppSettings) -> str:
        response = requests.post(
            settings.base_url.rstrip("/") + "/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _build_plan_prompt(self, task: Task) -> str:
        due_text = task.due_at.strftime("%Y-%m-%d %H:%M") if task.due_at else "未设置"
        tags_text = "、".join(task.tags) if task.tags else "无标签"
        description = task.description.strip() or "无补充描述"
        return f"""
请把下面这个任务拆解成足够细的执行计划。

要求：
1. 子任务必须具体、可直接执行，避免空泛表达。
2. 如果任务较复杂，至少拆成 5 到 8 个子任务；如果任务较简单，也至少给 3 个子任务。
3. 子任务标题要用行动导向的短句，比如“整理需求清单”“列出测试场景”。
4. execution_order 要给出推荐执行顺序，内容应与 subtasks 对应。
5. priority 只能是 high、medium、low 之一。
6. summary 要简洁说明推进策略，控制在 2 到 4 句。
7. 返回 JSON，结构必须为：
{{
  "summary": "string",
  "priority": "high|medium|low",
  "execution_order": ["步骤1", "步骤2"],
  "subtasks": [
    {{"title": "子任务标题", "done": false}}
  ]
}}

任务信息：
- 标题：{task.title}
- 描述：{description}
- 当前优先级：{task.priority}
- 截止时间：{due_text}
- 标签：{tags_text}
""".strip()

    def _build_capture_prompt(self, user_input: str) -> str:
        return f"""
用户原话：
{user_input}

请把它整理成一条 Todo 任务，并返回 JSON。

要求：
1. title 要简洁明确，适合放在待办列表里。
2. description 要补充上下文，但不要太长。
3. priority 只能是 high、medium、low。
4. due_at 如果用户没有明确提到时间，就返回空字符串。
5. tags 返回简短数组，没有就返回空数组。
6. subtasks 只在非常明显需要拆分时给出 2 到 5 个，否则返回空数组。
7. summary 用 1 到 2 句解释为什么这么整理。

JSON 结构必须为：
{{
  "title": "string",
  "description": "string",
  "priority": "high|medium|low",
  "due_at": "YYYY-MM-DD HH:MM or empty string",
  "tags": ["tag1", "tag2"],
  "subtasks": [
    {{"title": "子任务标题", "done": false}}
  ],
  "summary": "string"
}}
""".strip()

    def _parse_task(self, content: str, fallback_input: str) -> Task:
        payload = self._extract_json(content)
        title = str(payload.get("title", "")).strip() or fallback_input.strip()[:40]
        description = str(payload.get("description", "")).strip()
        priority = str(payload.get("priority", "medium")).strip().lower()
        if priority not in {"high", "medium", "low"}:
            priority = "medium"
        due_at = self._parse_due_at(payload.get("due_at"))
        tags = [str(item).strip() for item in payload.get("tags", []) if str(item).strip()]
        subtasks = [
            SubTask.from_dict(item)
            for item in payload.get("subtasks", [])
            if isinstance(item, dict) and item.get("title")
        ]
        task = Task.create(title=title, description=description, priority=priority, due_at=due_at, tags=tags)
        task.subtasks = subtasks
        task.ai_notes = str(payload.get("summary", "")).strip()
        return task

    def _parse_due_at(self, value: Any) -> datetime | None:
        if not value:
            return None
        text = str(value).strip()
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None

    def _parse_suggestion(self, content: str) -> AIPlanSuggestion:
        payload = self._extract_json(content)
        subtasks = [
            SubTask.from_dict(item)
            for item in payload.get("subtasks", [])
            if isinstance(item, dict) and item.get("title")
        ]
        if not subtasks:
            raise ValueError("AI 没有返回可用的子任务。")

        priority = payload.get("priority", "medium")
        if priority not in {"high", "medium", "low"}:
            priority = "medium"

        execution_order = [str(item).strip() for item in payload.get("execution_order", []) if str(item).strip()]
        if not execution_order:
            execution_order = [item.title for item in subtasks]

        return AIPlanSuggestion(
            summary=str(payload.get("summary", "")).strip(),
            priority=priority,
            execution_order=execution_order,
            subtasks=subtasks,
        )

    def _extract_json(self, raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and start < end:
                return json.loads(cleaned[start : end + 1])
            raise ValueError("AI 返回内容不是合法 JSON。")
