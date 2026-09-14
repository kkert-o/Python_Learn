from __future__ import annotations

import re
from pathlib import Path

from app.workspace.file_manager import FileManager


class ProjectManager:
    ENTRY_CANDIDATES = ("main.py", "app.py", "run.py")
    SUPPORTED_EXTENSIONS = {
        ".py",
        ".txt",
        ".json",
        ".csv",
        ".md",
        ".toml",
        ".yaml",
        ".yml",
        ".ini",
    }

    def create_project(
        self,
        parent_directory: str | Path,
        name: str,
        *,
        template: str = "basic",
        overwrite: bool = False,
    ) -> Path:
        clean_name = self._clean_project_name(name)
        root = Path(parent_directory).expanduser().resolve() / clean_name
        if root.exists() and any(root.iterdir()) and not overwrite:
            raise FileExistsError(f"项目目录不是空的：{root}")
        root.mkdir(parents=True, exist_ok=True)
        main_path = root / "main.py"
        readme_path = root / "README.md"
        gitignore_path = root / ".gitignore"
        main_content = {
            "blank": "",
            "basic": (
                'def main():\n    print("Hello Python")\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            ),
            "quality": (
                'def main():\n    print("Hello Python")\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            ),
        }.get(template)
        if main_content is None:
            raise ValueError(f"不支持的项目模板：{template}")
        if overwrite or not main_path.exists():
            FileManager.write_text(
                main_path,
                main_content,
            )
        if overwrite or not readme_path.exists():
            FileManager.write_text(
                readme_path,
                f"# {clean_name}\n\n用 Python 学习器完成这个项目。\n",
            )
        if overwrite or not gitignore_path.exists():
            FileManager.write_text(
                gitignore_path,
                "__pycache__/\n.venv/\n*.py[cod]\n",
            )
        if template == "quality":
            test_dir = root / "tests"
            test_dir.mkdir(exist_ok=True)
            test_path = test_dir / "test_main.py"
            if overwrite or not test_path.exists():
                FileManager.write_text(
                    test_path,
                    "from pathlib import Path\n\n\n"
                    "def test_project_files_exist():\n"
                    "    assert Path('main.py').exists()\n",
                )
            requirements_path = root / "requirements-dev.txt"
            if overwrite or not requirements_path.exists():
                FileManager.write_text(requirements_path, "pytest\n")
        return root

    def detect_entry_file(self, project_root: str | Path) -> Path | None:
        root = Path(project_root)
        for name in self.ENTRY_CANDIDATES:
            candidate = root / name
            if candidate.is_file():
                return candidate
        py_files = sorted(
            path
            for path in root.glob("*.py")
            if path.is_file() and not path.name.startswith(".")
        )
        return py_files[0] if py_files else None

    def is_supported_file(self, path: str | Path) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED_EXTENSIONS

    @staticmethod
    def _clean_project_name(name: str) -> str:
        cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name.strip())
        cleaned = cleaned.rstrip(". ")
        if not cleaned:
            raise ValueError("项目名称不能为空")
        return cleaned
