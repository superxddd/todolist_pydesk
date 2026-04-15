import os

from ai_todo.storage.settings_store import SettingsRepository


def test_settings_repository_applies_environment_overrides(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_TODO_BASE_URL", "https://api.deepseek.com/v1")
    monkeypatch.setenv("AI_TODO_MODEL", "deepseek-chat")
    monkeypatch.setenv("AI_TODO_API_KEY", "secret")
    repo = SettingsRepository(tmp_path / "settings.json")
    settings = repo.load()
    assert settings.base_url == "https://api.deepseek.com/v1"
    assert settings.model == "deepseek-chat"
    assert settings.api_key == "secret"
