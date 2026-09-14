from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from app.config import AppPaths


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture()
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def app_paths(tmp_path: Path, project_root: Path) -> AppPaths:
    resource_root = tmp_path / "resources"
    shutil.copytree(project_root / "content", resource_root / "content")
    shutil.copytree(project_root / "assets", resource_root / "assets")
    paths = AppPaths(
        project_root=project_root,
        resource_root=resource_root,
        local_data_root=tmp_path / "local",
    )
    paths.ensure()
    return paths
