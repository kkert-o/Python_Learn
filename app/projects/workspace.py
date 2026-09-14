from __future__ import annotations

from pathlib import Path

from app.config import AppPaths
from app.data.models import ProjectInfo
from app.workspace import FileManager


class CourseProjectWorkspace:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def ensure(self, project: ProjectInfo) -> Path:
        root = (
            self.paths.projects_dir
            / "course_projects"
            / project.project_id
        )
        root.mkdir(parents=True, exist_ok=True)
        main_path = root / "main.py"
        readme_path = root / "README.md"
        gitignore_path = root / ".gitignore"
        if not main_path.exists():
            FileManager.write_text(main_path, project.starter.rstrip() + "\n")
        requirements = "\n".join(
            f"- [ ] {item}" for item in project.requirements
        )
        FileManager.write_text(
            readme_path,
            f"# {project.title}\n\n"
            f"级别：{project.level}\n\n"
            f"## 项目目标\n\n{project.goal}\n\n"
            f"## 验收要求\n\n{requirements}\n",
        )
        if not gitignore_path.exists():
            FileManager.write_text(
                gitignore_path,
                "__pycache__/\n.venv/\n*.py[cod]\n",
            )
        return root

