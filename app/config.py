from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "PythonLearner"
APP_DISPLAY_NAME = "Python 学习器"
APP_VERSION = "1.1.0"
ORGANIZATION_NAME = "PythonLearner"


@dataclass(frozen=True, slots=True)
class AppPaths:
    project_root: Path
    resource_root: Path
    local_data_root: Path

    @classmethod
    def discover(cls, local_data_root: Path | None = None) -> "AppPaths":
        project_root = Path(__file__).resolve().parents[1]
        resource_root = Path(getattr(sys, "_MEIPASS", project_root))
        if local_data_root is None:
            base = Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    Path.home() / "AppData" / "Local",
                )
            )
            local_data_root = base / APP_NAME
        else:
            local_data_root = Path(local_data_root).expanduser().resolve()
        return cls(
            project_root=project_root,
            resource_root=resource_root,
            local_data_root=local_data_root,
        )

    @property
    def database_path(self) -> Path:
        return self.local_data_root / "data" / "learning.db"

    @property
    def settings_path(self) -> Path:
        return self.local_data_root / "settings.json"

    @property
    def installed_content_path(self) -> Path:
        return self.local_data_root / "content" / "course_content.json"

    @property
    def built_in_content_path(self) -> Path:
        return self.resource_root / "content" / "course_content.json"

    @property
    def logs_dir(self) -> Path:
        return self.local_data_root / "logs"

    @property
    def cache_dir(self) -> Path:
        return self.local_data_root / "cache"

    @property
    def runs_dir(self) -> Path:
        return self.local_data_root / "runs"

    @property
    def projects_dir(self) -> Path:
        return self.local_data_root / "projects"

    @property
    def packages_dir(self) -> Path:
        return self.local_data_root / "packages"

    def ensure(self) -> None:
        for path in (
            self.local_data_root,
            self.database_path.parent,
            self.installed_content_path.parent,
            self.logs_dir,
            self.cache_dir,
            self.runs_dir,
            self.projects_dir,
            self.packages_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)
