from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from typing import Any
from uuid import uuid4

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def utc_now() -> datetime:
    return datetime.now().replace(microsecond=0)


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.strftime(ISO_FORMAT) if value else None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, ISO_FORMAT)


@dataclass(slots=True)
class SubTask:
    title: str
    done: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SubTask:
        return cls(title=payload["title"], done=payload.get("done", False))


@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: str
    status: str
    priority: str
    due_at: datetime | None
    tags: list[str] = field(default_factory=list)
    subtasks: list[SubTask] = field(default_factory=list)
    ai_notes: str = ""
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_at: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        return cls(
            id=str(uuid4()),
            title=title,
            description=description,
            status="todo",
            priority=priority,
            due_at=due_at,
            tags=tags or [],
        )

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_at": _serialize_datetime(self.due_at),
            "tags": self.tags,
            "subtasks": [item.to_dict() for item in self.subtasks],
            "ai_notes": self.ai_notes,
            "created_at": _serialize_datetime(self.created_at),
            "updated_at": _serialize_datetime(self.updated_at),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Task:
        return cls(
            id=payload["id"],
            title=payload["title"],
            description=payload.get("description", ""),
            status=payload.get("status", "todo"),
            priority=payload.get("priority", "medium"),
            due_at=_parse_datetime(payload.get("due_at")),
            tags=list(payload.get("tags", [])),
            subtasks=[SubTask.from_dict(item) for item in payload.get("subtasks", [])],
            ai_notes=payload.get("ai_notes", ""),
            created_at=_parse_datetime(payload.get("created_at")) or utc_now(),
            updated_at=_parse_datetime(payload.get("updated_at")) or utc_now(),
        )


@dataclass(slots=True)
class AIPlanSuggestion:
    summary: str
    priority: str
    execution_order: list[str]
    subtasks: list[SubTask]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "priority": self.priority,
            "execution_order": self.execution_order,
            "subtasks": [item.to_dict() for item in self.subtasks],
        }


@dataclass(slots=True)
class ReminderItem:
    task_id: str
    title: str
    due_at: datetime
    status: str


@dataclass(slots=True)
class AppSettings:
    base_url: str = ""
    model: str = ""
    api_key: str = ""
    theme: str = "light"
    window_width: int = 1300
    window_height: int = 760
    reminder_minutes_before: int = 30
    tray_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> AppSettings:
        return cls(**{**cls().to_dict(), **payload})

    def with_overrides(self, **overrides: Any) -> AppSettings:
        filtered = {
            key: value
            for key, value in overrides.items()
            if value not in (None, "")
        }
        return replace(self, **filtered)
