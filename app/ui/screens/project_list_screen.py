from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.data.repositories import ProgressRepository
from app.projects import ProjectCatalog
from app.ui.components.common import clear_layout


class ProjectListScreen(QWidget):
    project_requested = Signal(str)

    def __init__(
        self,
        catalog: ProjectCatalog,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.catalog = catalog
        self.progress_repository = progress_repository
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(32, 26, 32, 32)
        self.container_layout.setSpacing(14)
        self.container_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.refresh()

    def refresh(self) -> None:
        clear_layout(self.container_layout)
        completed = self.progress_repository.completed_project_ids()
        total = len(self.catalog.all)
        percent = round(len(completed) * 100 / total) if total else 0

        title = QLabel("项目实战")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "从 Lv.1 小项目逐步过渡到完整交付，项目要求不等于完整答案。"
        )
        subtitle.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)

        summary = QFrame()
        summary.setObjectName("summaryCard")
        summary_layout = QVBoxLayout(summary)
        header = QHBoxLayout()
        header.addWidget(QLabel("项目完成度"))
        header.addStretch(1)
        value = QLabel(f"{percent}%")
        value.setObjectName("progressValue")
        header.addWidget(value)
        summary_layout.addLayout(header)
        detail = QLabel(f"已完成 {len(completed)} / {total} 个项目")
        detail.setObjectName("mutedText")
        summary_layout.addWidget(detail)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(percent)
        progress.setTextVisible(False)
        summary_layout.addWidget(progress)
        self.container_layout.addWidget(summary)

        for level in self.catalog.levels:
            level_label = QLabel(level)
            level_label.setObjectName("sectionTitle")
            self.container_layout.addWidget(level_label)
            for project in self.catalog.by_level(level):
                card = QFrame()
                card.setObjectName("stageCard")
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(18, 15, 18, 16)
                top = QHBoxLayout()
                name = QLabel(project.title)
                name.setObjectName("projectTitle")
                status = QLabel(
                    "已完成"
                    if project.project_id in completed
                    else "待完成"
                )
                status.setObjectName("tagLabel")
                top.addWidget(name)
                top.addStretch(1)
                top.addWidget(status)
                card_layout.addLayout(top)
                goal = QLabel(project.goal)
                goal.setWordWrap(True)
                goal.setObjectName("mutedText")
                card_layout.addWidget(goal)
                knowledge = QLabel(" · ".join(project.knowledge))
                knowledge.setObjectName("mutedText")
                knowledge.setWordWrap(True)
                card_layout.addWidget(knowledge)
                open_button = QPushButton("查看项目要求")
                open_button.setObjectName("primaryButton")
                open_button.clicked.connect(
                    lambda _checked=False, project_id=project.project_id: self.project_requested.emit(
                        project_id
                    )
                )
                card_layout.addWidget(
                    open_button,
                    alignment=Qt.AlignmentFlag.AlignLeft,
                )
                self.container_layout.addWidget(card)
        self.container_layout.addStretch(1)

