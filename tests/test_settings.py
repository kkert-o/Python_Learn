from __future__ import annotations

import json

from app.services.settings import SettingsService


def test_legacy_system_theme_migrates_to_light(tmp_path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "theme_preference": "system",
                "_settings_version": 1,
            }
        ),
        encoding="utf-8",
    )
    settings = SettingsService(path)
    assert settings.get("theme_preference") == "light"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["theme_preference"] == "light"
    assert saved["_settings_version"] == 4
    assert saved["wallpaper_transparency"] == 35
    assert saved["workbench_font_size"] == 11


def test_new_settings_default_to_light(tmp_path) -> None:
    settings = SettingsService(tmp_path / "settings.json")
    assert settings.get("theme_preference") == "light"
