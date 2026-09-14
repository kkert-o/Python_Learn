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
from app.training import TrainingCatalog, TrainingType
from app.ui.components.common import clear_layout


class TrainingCenterScreen(QWidget):
    start_type_requested = Signal(object)
    review_requested = Signal()

    def __init__(
        self,
        catalog: TrainingCatalog,
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
        completed = self.progress_repository.completed_training_ids()
        needs_review = self.progress_repository.training_needs_review_ids()
        total = len(self.catalog.all)
        percent = round(len(completed) * 100 / total) if total else 0

        title = QLabel("专项训练")
        title.setObjectName("pageTitle")
        subtitle = QLabel("用四类训练把“看懂”推进到“能改、能写、能调试”。")
        subtitle.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)

        summary = QFrame()
        summary.setObjectName("summaryCard")
        summary_layout = QVBoxLayout(summary)
        header = QHBoxLayout()
        header.addWidget(QLabel("训练完成度"))
        header.addStretch(1)
        percent_label = QLabel(f"{percent}%")
        percent_label.setObjectName("progressValue")
        header.addWidget(percent_label)
        summary_layout.addLayout(header)
        detail = QLabel(
            f"已完成 {len(completed)} / {total} 题 · 待复习 {len(needs_review)} 题"
        )
        detail.setObjectName("mutedText")
        summary_layout.addWidget(detail)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(percent)
        progress.setTextVisible(False)
        summary_layout.addWidget(progress)
        self.container_layout.addWidget(summary)

        if needs_review:
            review = QFrame()
            review.setObjectName("summaryCard")
            review_layout = QHBoxLayout(review)
            review_text = QLabel(
                f"有 {len(needs_review)} 道错题需要复习。\n"
                "复习答对后会自动移出错题记录。"
            )
            review_text.setWordWrap(True)
            review_button = QPushButton("复习错题")
            review_button.setObjectName("primaryButton")
            review_button.clicked.connect(self.review_requested.emit)
            review_layout.addWidget(review_text, 1)
            review_layout.addWidget(review_button)
            self.container_layout.addWidget(review)

        for training_type in TrainingType:
            exercises = self.catalog.by_type(training_type)
            completed_count = sum(
                exercise.exercise_id in completed for exercise in exercises
            )
            card = QFrame()
            card.setObjectName("stageCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 15, 18, 16)
            top = QHBoxLayout()
            name = QLabel(training_type.label)
            name.setObjectName("sectionTitle")
            count = QLabel(f"{completed_count} / {len(exercises)}")
            count.setObjectName("progressValue")
            top.addWidget(name)
            top.addStretch(1)
            top.addWidget(count)
            card_layout.addLayout(top)
            description = QLabel(training_type.description)
            description.setObjectName("mutedText")
            card_layout.addWidget(description)
            bar = QProgressBar()
            bar.setRange(0, len(exercises))
            bar.setValue(completed_count)
            bar.setTextVisible(False)
            card_layout.addWidget(bar)
            start = QPushButton("开始训练")
            start.setObjectName("primaryButton")
            start.clicked.connect(
                lambda _checked=False, value=training_type: self.start_type_requested.emit(
                    value
                )
            )
            card_layout.addWidget(start, alignment=Qt.AlignmentFlag.AlignLeft)
            self.container_layout.addWidget(card)
        self.container_layout.addStretch(1)

