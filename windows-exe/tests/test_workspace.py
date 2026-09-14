from __future__ import annotations

import pytest

from app.workspace import FileManager, ProjectManager


def test_project_manager_creates_standard_project(tmp_path) -> None:
    manager = ProjectManager()
    root = manager.create_project(tmp_path, "我的项目")
    assert (root / "main.py").exists()
    assert (root / "README.md").exists()
    assert (root / ".gitignore").exists()
    assert manager.detect_entry_file(root) == root / "main.py"


def test_file_manager_supports_utf8_round_trip(tmp_path) -> None:
    path = tmp_path / "中文.py"
    FileManager.write_text(path, 'print("你好")\n')
    data = FileManager.read_text(path)
    assert data.text == 'print("你好")\n'
    assert data.encoding == "utf-8-sig" or data.encoding == "utf-8"


def test_file_manager_rejects_unsafe_rename(tmp_path) -> None:
    path = tmp_path / "main.py"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        FileManager.rename(path, "../escape.py")

