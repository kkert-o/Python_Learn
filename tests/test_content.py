from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.data.content import ContentLoader, ContentValidationError, validate_content


def test_built_in_content_loads_complete_catalog(app_paths) -> None:
    result = ContentLoader(app_paths).load()
    assert result.content.version == 2
    assert result.content.stage_count == 16
    assert result.content.lesson_count == 56
    assert result.content.project_count == 13
    assert result.source == app_paths.built_in_content_path


def test_invalid_installed_content_falls_back_to_built_in(app_paths) -> None:
    app_paths.installed_content_path.write_text(
        '{"version": 0}',
        encoding="utf-8",
    )
    result = ContentLoader(app_paths).load()
    assert result.used_fallback is True
    assert result.content.lesson_count == 56
    assert result.warning is not None


def test_validator_rejects_invalid_quiz_answer() -> None:
    raw = {
        "version": 1,
        "updatedAt": "2026-09-13",
        "stages": [
            {
                "name": "基础",
                "lessons": [{"id": "intro", "title": "介绍"}],
            }
        ],
        "lessons": {
            "intro": {
                "id": "intro",
                "title": "介绍",
                "example": 'print("hello")',
                "quiz": {"options": ["A", "B"], "answerIndex": 2},
            }
        },
        "projects": [
            {
                "id": "demo",
                "title": "演示",
                "goal": "完成演示",
            }
        ],
    }
    with pytest.raises(ContentValidationError, match="答案下标"):
        validate_content(raw)


def test_installed_content_has_priority(app_paths) -> None:
    raw = json.loads(app_paths.built_in_content_path.read_text(encoding="utf-8"))
    raw["updatedAt"] = "2099-01-01"
    app_paths.installed_content_path.write_text(
        json.dumps(raw, ensure_ascii=False),
        encoding="utf-8",
    )
    result = ContentLoader(app_paths).load()
    assert result.source == app_paths.installed_content_path
    assert result.content.updated_at == "2099-01-01"

