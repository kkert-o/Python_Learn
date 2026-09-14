from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.data.models import ProjectInfo
from app.data.repositories import ProgressRepository
from app.projects import ProjectCatalog
from app.ui.components.common import clear_layout


class ProjectDetailScreen(QWidget):
    back_requested = Signal()
    workbench_requested = Signal(str)
    progress_changed = Signal()

    def __init__(
        self,
        catalog: ProjectCatalog,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.catalog = catalog
        self.progress_repository = progress_repository
        self.project: ProjectInfo | None = None
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(34, 24, 34, 34)
        self.container_layout.setSpacing(14)
        self.container_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setWidget(self.container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)

    def show_project(self, project_id: str) -> None:
        project = self.catalog.by_id(project_id)
        if project is None:
            return
        self.project = project
        self._render()
        self.scroll.verticalScrollBar().setValue(0)

    def _render(self) -> None:
        if self.project is None:
            return
        project = self.project
        completed = project.project_id in self.progress_repository.completed_project_ids()
        clear_layout(self.container_layout)

        back = QPushButton("返回项目")
        back.clicked.connect(self.back_requested.emit)
        self.container_layout.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

        level = QLabel(project.level)
        level.setObjectName("tagLabel")
        title = QLabel(project.title)
        title.setObjectName("pageTitle")
        self.container_layout.addWidget(level)
        self.container_layout.addWidget(title)

        goal = QFrame()
        goal.setObjectName("lessonSection")
        goal_layout = QVBoxLayout(goal)
        goal_title = QLabel("项目目标")
        goal_title.setObjectName("sectionTitle")
        goal_text = QLabel(project.goal)
        goal_text.setWordWrap(True)
        goal_layout.addWidget(goal_title)
        goal_layout.addWidget(goal_text)
        self.container_layout.addWidget(goal)

        requirements = QFrame()
        requirements.setObjectName("lessonSection")
        requirements_layout = QVBoxLayout(requirements)
        requirements_title = QLabel("验收要求")
        requirements_title.setObjectName("sectionTitle")
        requirements_layout.addWidget(requirements_title)
        for index, item in enumerate(project.requirements, start=1):
            requirement = QLabel(f"{index}. {item}")
            requirement.setWordWrap(True)
            requirements_layout.addWidget(requirement)
        self.container_layout.addWidget(requirements)

        hints = QFrame()
        hints.setObjectName("lessonSection")
        hints_layout = QVBoxLayout(hints)
        hints_title = QLabel("思路提示")
        hints_title.setObjectName("sectionTitle")
        hints_layout.addWidget(hints_title)
        for index, hint_text in enumerate(project.hints, start=1):
            toggle = QToolButton()
            toggle.setObjectName("hintToggle")
            toggle.setCheckable(True)
            toggle.setText(f"提示 {index}")
            toggle.setArrowType(Qt.ArrowType.RightArrow)
            toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            hint_label = QLabel(hint_text)
            hint_label.setWordWrap(True)
            hint_label.setObjectName("mutedText")
            hint_label.setVisible(False)

            def toggle_hint(
                checked: bool,
                button=toggle,
                label=hint_label,
            ) -> None:
                label.setVisible(checked)
                button.setArrowType(
                    Qt.ArrowType.DownArrow
                    if checked
                    else Qt.ArrowType.RightArrow
                )

            toggle.toggled.connect(toggle_hint)
            hints_layout.addWidget(toggle)
            hints_layout.addWidget(hint_label)
        self.container_layout.addWidget(hints)

        starter = QFrame()
        starter.setObjectName("lessonSection")
        starter_layout = QVBoxLayout(starter)
        starter_title = QLabel("起始代码")
        starter_title.setObjectName("sectionTitle")
        starter_layout.addWidget(starter_title)
        code_view = QPlainTextEdit()
        code_view.setReadOnly(True)
        code_view.setPlainText(project.starter)
        code_view.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        code_view.setMaximumHeight(240)
        starter_layout.addWidget(code_view)
        copy = QPushButton("复制起始代码")
        copy.clicked.connect(
            lambda _checked=False, value=project.starter: QGuiApplication.clipboard().setText(
                value
            )
        )
        starter_layout.addWidget(copy, alignment=Qt.AlignmentFlag.AlignLeft)
        self.container_layout.addWidget(starter)

        actions = QHBoxLayout()
        workspace = QPushButton("创建项目工作区并打开")
        workspace.setObjectName("primaryButton")
        workspace.clicked.connect(
            lambda _checked=False, project_id=project.project_id: self.workbench_requested.emit(
                project_id
            )
        )
        complete = QPushButton("项目已完成" if completed else "标记项目完成")
        complete.setEnabled(not completed)
        complete.clicked.connect(self._complete_project)
        actions.addWidget(workspace)
        actions.addWidget(complete)
        actions.addStretch(1)
        self.container_layout.addLayout(actions)
        self.container_layout.addStretch(1)

    def _complete_project(self) -> None:
        if self.project is None:
            return
        self.progress_repository.complete_project(self.project.project_id)
        self.progress_changed.emit()
        self._render()

