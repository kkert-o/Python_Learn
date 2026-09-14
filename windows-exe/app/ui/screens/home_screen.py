from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.data.models import CourseContent
from app.data.repositories import ProgressRepository, WorkspaceRepository
from app.learning import CourseCatalog
import qtawesome as qta


class HomeScreen(QWidget):
    open_workbench_requested = Signal()
    open_project_requested = Signal(str)
    continue_learning_requested = Signal(str)

    def __init__(
        self,
        content: CourseContent,
        catalog: CourseCatalog,
        progress_repository: ProgressRepository,
        workspace_repository: WorkspaceRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.content = content
        self.catalog = catalog
        self.progress_repository = progress_repository
        self.workspace_repository = workspace_repository

        title = QLabel("Python 学习器")
        title.setObjectName("pageTitle")
        subtitle = QLabel("从写一行代码开始，运行、理解错误，再把它改对。")
        subtitle.setObjectName("pageSubtitle")
        start_button = QPushButton("进入 Python 工作台")
        start_button.setObjectName("primaryButton")
        start_button.setIcon(qta.icon("fa5s.play", color="#FFFFFF"))
        start_button.setIconSize(QSize(16, 16))
        start_button.clicked.connect(self.open_workbench_requested.emit)

        self.continue_card = QFrame()
        self.continue_card.setObjectName("summaryCard")
        self.continue_layout = QVBoxLayout(self.continue_card)
        self.continue_title = QLabel("下一步推荐")
        self.continue_title.setObjectName("sectionTitle")
        self.continue_text = QLabel()
        self.continue_text.setWordWrap(True)
        self.continue_button = QPushButton("继续学习")
        self.continue_button.setObjectName("primaryButton")
        self.continue_button.clicked.connect(self._continue_learning)
        self.continue_layout.addWidget(self.continue_title)
        self.continue_layout.addWidget(self.continue_text)
        self.continue_layout.addWidget(
            self.continue_button,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )

        metrics = QHBoxLayout()
        self.stage_value = self._metric(metrics, "课程阶段")
        self.lesson_value = self._metric(metrics, "知识点")
        self.project_value = self._metric(metrics, "项目实战")
        self.completed_value = self._metric(metrics, "已完成知识点")

        self.recent_projects = QListWidget()
        self.recent_projects.setMinimumHeight(180)
        self.recent_projects.itemDoubleClicked.connect(self._open_recent_project)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(34, 28, 34, 28)
        content_layout.setSpacing(18)
        content_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.continue_card)
        content_layout.addLayout(metrics)
        recent_title = QLabel("最近项目")
        recent_title.setObjectName("sectionTitle")
        content_layout.addWidget(recent_title)
        content_layout.addWidget(self.recent_projects)
        content_layout.addStretch(1)

        inner = QWidget()
        inner.setLayout(content_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(inner)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)
        self.refresh()

    @staticmethod
    def _metric(layout: QHBoxLayout, label_text: str) -> QLabel:
        card = QFrame()
        card.setObjectName("metricCard")
        card_layout = QVBoxLayout(card)
        value = QLabel("0")
        value.setObjectName("metricValue")
        label = QLabel(label_text)
        label.setObjectName("metricLabel")
        card_layout.addWidget(value)
        card_layout.addWidget(label)
        layout.addWidget(card, 1)
        return value

    def refresh(self) -> None:
        progress = self.progress_repository.snapshot()
        completed = self.progress_repository.completed_lesson_ids()
        summary = self.catalog.overall_summary(completed)
        self.stage_value.setText(str(self.content.stage_count))
        self.lesson_value.setText(str(self.content.lesson_count))
        self.project_value.setText(str(self.content.project_count))
        self.completed_value.setText(str(progress.completed_lessons))
        next_lesson = (
            self.catalog.lesson(summary.next_lesson_id)
            if summary.next_lesson_id is not None
            else None
        )
        if next_lesson is None:
            self.continue_text.setText("全部知识点已经完成，可以进入项目实战。")
            self.continue_button.setVisible(False)
        else:
            self.continue_text.setText(
                f"{next_lesson.stage} · {next_lesson.title}\n"
                f"总体进度 {summary.percent}% · 预计 {next_lesson.minutes} 分钟"
            )
            self.continue_button.setVisible(True)

        self.recent_projects.clear()
        projects = self.workspace_repository.list_projects(limit=8)
        if not projects:
            item = QListWidgetItem("还没有打开过项目。进入工作台后可以新建或打开项目。")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.recent_projects.addItem(item)
            return
        for project in projects:
            path = Path(project.root_path)
            item = QListWidgetItem(f"{project.name}    {path}")
            item.setData(Qt.ItemDataRole.UserRole, project.root_path)
            self.recent_projects.addItem(item)

    def _open_recent_project(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.open_project_requested.emit(str(path))

    def _continue_learning(self) -> None:
        completed = self.progress_repository.completed_lesson_ids()
        lesson_id = self.catalog.overall_summary(completed).next_lesson_id
        if lesson_id is not None:
            self.continue_learning_requested.emit(lesson_id)
