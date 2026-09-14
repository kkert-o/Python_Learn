from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULTS: dict[str, Any] = {
    "theme_preference": "light",
    "accent_value": "#2563EB",
    "glass_effect": True,
    "wallpaper_path": "",
    "wallpaper_transparency": 35,
    "workbench_font_size": 11,
    "legal_region": "中国大陆",
    "favorites": [],
    "ai_free_challenges": [],
    "ai_prompt_count": 0,
    "ai_endpoint": "https://api.deepseek.com/chat/completions",
    "ai_model": "deepseek-chat",
    "_settings_version": 4,
}


class SettingsService:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._values = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8-sig") as handle:
                raw = json.load(handle)
            if isinstance(raw, dict):
                migrated = False
                version = int(raw.get("_settings_version", 1))
                if version < 2 and raw.get("theme_preference", "system") == "system":
                    raw["theme_preference"] = "light"
                    migrated = True
                if "wallpaper_transparency" not in raw:
                    raw["wallpaper_transparency"] = 35
                    migrated = True
                if "workbench_font_size" not in raw:
                    raw["workbench_font_size"] = 11
                    migrated = True
                raw["_settings_version"] = 4
                self._values.update(raw)
                if migrated:
                    self.save()
        except (OSError, json.JSONDecodeError):
            return

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value
        self.save()

    def update(self, values: dict[str, Any]) -> None:
        self._values.update(values)
        self.save()

    def as_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".json.tmp")
        with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(self._values, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(self.path)
