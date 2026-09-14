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
from app.learning import CourseCatalog
from app.ui.components.common import clear_layout


class LearningHubScreen(QWidget):
    back_requested = Signal()
    lesson_requested = Signal(str)

    def __init__(
        self,
        catalog: CourseCatalog,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.catalog = catalog
        self.progress_repository = progress_repository
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(34, 24, 34, 34)
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
        completed = self.progress_repository.completed_lesson_ids()
        summary = self.catalog.overall_summary(completed)
        due_reviews = self.progress_repository.due_review_count()
        completed_training = len(
            self.progress_repository.completed_training_ids()
        )
        completed_projects = len(
            self.progress_repository.completed_project_ids()
        )

        top = QHBoxLayout()
        back = QPushButton("返回课程")
        back.clicked.connect(self.back_requested.emit)
        top.addWidget(back)
        top.addStretch(1)
        self.container_layout.addLayout(top)

        title = QLabel("学习中心")
        title.setObjectName("pageTitle")
        subtitle = QLabel("查看整体进度、阶段完成度和下一步推荐。")
        subtitle.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)

        metrics = QHBoxLayout()
        metrics.addWidget(self._metric("总体进度", f"{summary.percent}%"), 1)
        metrics.addWidget(
            self._metric("已完成知识点", f"{summary.completed} / {summary.total}"),
            1,
        )
        metrics.addWidget(
            self._metric("已完成训练", str(completed_training)),
            1,
        )
        metrics.addWidget(
            self._metric("已完成项目", str(completed_projects)),
            1,
        )
        metrics.addWidget(self._metric("到期复习", str(due_reviews)), 1)
        self.container_layout.addLayout(metrics)

        recommendation = QFrame()
        recommendation.setObjectName("summaryCard")
        recommendation_layout = QVBoxLayout(recommendation)
        rec_title = QLabel("下一步推荐")
        rec_title.setObjectName("sectionTitle")
        recommendation_layout.addWidget(rec_title)
        next_lesson = (
            self.catalog.lesson(summary.next_lesson_id)
            if summary.next_lesson_id is not None
            else None
        )
        if next_lesson is None:
            rec_text = "全部知识点已经完成，可以进入项目实战。"
            button = None
        else:
            rec_text = (
                f"{next_lesson.stage} · {next_lesson.title}\n"
                f"预计 {next_lesson.minutes} 分钟"
            )
            button = QPushButton("继续学习")
            button.setObjectName("primaryButton")
            button.clicked.connect(
                lambda _checked=False, lesson_id=next_lesson.lesson_id: self.lesson_requested.emit(
                    lesson_id
                )
            )
        rec_label = QLabel(rec_text)
        rec_label.setWordWrap(True)
        recommendation_layout.addWidget(rec_label)
        if button is not None:
            recommendation_layout.addWidget(
                button,
                alignment=Qt.AlignmentFlag.AlignLeft,
            )
        self.container_layout.addWidget(recommendation)

        stage_title = QLabel("阶段进度")
        stage_title.setObjectName("sectionTitle")
        self.container_layout.addWidget(stage_title)
        for stage in self.catalog.content.stages:
            stage_progress = self.catalog.stage_progress(stage, completed)
            row = QFrame()
            row.setObjectName("progressRow")
            row_layout = QVBoxLayout(row)
            header = QHBoxLayout()
            name = QLabel(f"{stage.label} · {stage.name}")
            name.setObjectName("progressRowTitle")
            value = QLabel(f"{stage_progress}%")
            value.setObjectName("progressValue")
            header.addWidget(name)
            header.addStretch(1)
            header.addWidget(value)
            row_layout.addLayout(header)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(stage_progress)
            bar.setTextVisible(False)
            row_layout.addWidget(bar)
            self.container_layout.addWidget(row)
        self.container_layout.addStretch(1)

    @staticmethod
    def _metric(label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        label_widget = QLabel(label)
        label_widget.setObjectName("metricLabel")
        layout.addWidget(value_label)
        layout.addWidget(label_widget)
        return card
