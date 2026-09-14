from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.bootstrap import AppContext
from app.ui.components import CircularProgress, MilestoneRow
from app.workspace import FileManager


MILESTONES = (
    ("requirements", "需求文档", "明确用户、场景、目标和明确不做的范围。"),
    ("design", "架构与数据设计", "完成模块划分、数据表、接口和错误结构设计。"),
    ("mvp", "最小可运行版本", "完成一条端到端核心流程，而不是空页面。"),
    ("testing", "测试与失败路径", "覆盖核心逻辑、边界输入、失败路径和端到端流程。"),
    ("security", "安全与隐私", "检查密钥、输入校验、权限、日志和数据保存期限。"),
    ("documentation", "运行文档", "README 能让陌生用户从零安装、运行并验证。"),
    ("release", "发布版本", "生成可分发版本，记录已知限制和发布说明。"),
)


class GraduationProjectScreen(QWidget):
    workbench_requested = Signal(str)
    progress_changed = Signal()

    def __init__(
        self,
        context: AppContext,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.context = context
        self.project = context.project_catalog.by_id("graduation-project")
        self.checkboxes: dict[str, MilestoneRow] = {}

        title = QLabel("毕业项目")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "毕业项目不按页面数量验收，而是按可运行、可测试、可维护和可交付验收。"
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        self.progress = CircularProgress()
        self.progress_label = QLabel()
        self.progress_label.setObjectName("projectTitle")
        self.progress_detail = QLabel(
            "按里程碑推进，只有可运行、可测试、可交付的结果才算完成。"
        )
        self.progress_detail.setObjectName("mutedText")
        self.progress_detail.setWordWrap(True)
        hero_copy = QVBoxLayout()
        hero_copy.addStretch(1)
        hero_copy.addWidget(self.progress_label)
        hero_copy.addWidget(self.progress_detail)
        hero_copy.addStretch(1)
        hero = QHBoxLayout()
        hero.addWidget(self.progress)
        hero.addSpacing(18)
        hero.addLayout(hero_copy, 1)

        milestone_card = QFrame()
        milestone_card.setObjectName("lessonSection")
        milestone_layout = QVBoxLayout(milestone_card)
        milestone_title = QLabel("里程碑验收")
        milestone_title.setObjectName("sectionTitle")
        milestone_layout.addWidget(milestone_title)
        for index, (key, label, description) in enumerate(MILESTONES, start=1):
            checkbox = MilestoneRow(index, label, description)
            checkbox.toggled.connect(
                lambda checked, milestone_key=key: self._set_milestone(
                    milestone_key,
                    checked,
                )
            )
            milestone_layout.addWidget(checkbox)
            self.checkboxes[key] = checkbox

        workspace = QPushButton("创建毕业项目工作区")
        workspace.setObjectName("primaryButton")
        workspace.clicked.connect(self._create_workspace)
        actions = QHBoxLayout()
        actions.addWidget(workspace)
        actions.addStretch(1)

        requirements_text = QLabel(
            "毕业要求包含：需求分析、界面、数据库、API、测试、安全、文档和发布。"
            "完整要求可在项目列表中打开“Python 综合毕业项目”查看。"
        )
        requirements_text.setWordWrap(True)
        requirements_text.setObjectName("mutedText")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 26, 32, 30)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(hero)
        layout.addWidget(milestone_card)
        layout.addWidget(requirements_text)
        layout.addLayout(actions)
        layout.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        if self.project is None:
            return
        states = self.context.progress_repository.graduation_milestones(
            self.project.project_id
        )
        completed_count = 0
        for key, checkbox in self.checkboxes.items():
            completed = bool(states.get(key, False))
            checkbox.blockSignals(True)
            checkbox.setChecked(completed)
            checkbox.blockSignals(False)
            completed_count += int(completed)
        self.progress.setValue(completed_count)
        self.progress_label.setText(
            f"{completed_count} / {len(MILESTONES)} 个里程碑已完成"
        )

    def set_theme(self, dark: bool, accent: str) -> None:
        self.progress.set_theme(dark, accent)
        for checkbox in self.checkboxes.values():
            checkbox.set_theme(dark, accent)

    def _set_milestone(self, key: str, completed: bool) -> None:
        if self.project is None:
            return
        self.context.progress_repository.set_graduation_milestone(
            self.project.project_id,
            key,
            completed,
        )
        states = self.context.progress_repository.graduation_milestones(
            self.project.project_id
        )
        if len(states) >= len(MILESTONES) and all(states.values()):
            self.context.progress_repository.complete_project(
                self.project.project_id
            )
        self.progress_changed.emit()
        self.refresh()

    def _create_workspace(self) -> None:
        if self.project is None:
            return
        root = self.context.project_workspace.ensure(self.project)
        (root / "src").mkdir(exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "docs").mkdir(exist_ok=True)
        files = {
            root / "src" / "main.py": (
                'def main():\n    print("毕业项目最小版本")\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            ),
            root / "tests" / "test_main.py": (
                "from pathlib import Path\n\n\n"
                "def test_project_has_readme():\n"
                "    assert Path('README.md').exists()\n"
            ),
            root / "docs" / "requirements.md": (
                "# 需求文档\n\n## 用户与场景\n\n## 目标\n\n"
                "## 明确不做\n\n## 验收标准\n"
            ),
            root / "requirements-dev.txt": "pytest\n",
        }
        for path, content in files.items():
            if not path.exists():
                FileManager.write_text(path, content)
        self.workbench_requested.emit(str(root))
