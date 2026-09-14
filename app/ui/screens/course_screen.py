from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.data.models import CourseStage, LessonState
from app.data.repositories import ProgressRepository
from app.learning import CourseCatalog
from app.ui.components.common import clear_layout
import qtawesome as qta


class CourseScreen(QWidget):
    lesson_requested = Signal(str)
    practice_requested = Signal()
    learning_hub_requested = Signal()

    def __init__(
        self,
        catalog: CourseCatalog,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.catalog = catalog
        self.progress_repository = progress_repository
        self._last_refresh_key: tuple[frozenset[str], frozenset[str]] | None = None
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
        completed = self.progress_repository.completed_lesson_ids()
        started = self.progress_repository.started_lesson_ids()
        refresh_key = (frozenset(completed), frozenset(started))
        if refresh_key == self._last_refresh_key:
            return
        self._last_refresh_key = refresh_key
        clear_layout(self.container_layout)
        summary = self.catalog.overall_summary(completed)

        title = QLabel("课程")
        title.setObjectName("pageTitle")
        subtitle = QLabel("按顺序学习，完成当前知识点后自动解锁下一节。")
        subtitle.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)

        route_card = QFrame()
        route_card.setObjectName("summaryCard")
        route_layout = QVBoxLayout(route_card)
        route_header = QHBoxLayout()
        route_title = QLabel("Python 学习路线")
        route_title.setObjectName("sectionTitle")
        route_value = QLabel(f"{summary.percent}%")
        route_value.setObjectName("progressValue")
        route_header.addWidget(route_title)
        route_header.addStretch(1)
        route_header.addWidget(route_value)
        route_layout.addLayout(route_header)
        route_detail = QLabel(
            f"已完成 {summary.completed} / {summary.total} 个知识点"
            if completed
            else f"共 {len(self.catalog.content.stages)} 个阶段、{summary.total} 个知识点，尚未开始"
        )
        route_detail.setObjectName("mutedText")
        route_layout.addWidget(route_detail)
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(summary.percent)
        progress.setTextVisible(False)
        route_layout.addWidget(progress)
        self.container_layout.addWidget(route_card)

        tools = QHBoxLayout()
        practice = QPushButton("进入综合练习")
        learning_hub = QPushButton("查看学习进度")
        practice.setObjectName("secondaryButton")
        learning_hub.setObjectName("secondaryButton")
        practice.setIcon(qta.icon("fa5s.play-circle", color="#2563EB"))
        learning_hub.setIcon(qta.icon("fa5s.chart-line", color="#64748B"))
        practice.setIconSize(QSize(17, 17))
        learning_hub.setIconSize(QSize(17, 17))
        practice.clicked.connect(self.practice_requested.emit)
        learning_hub.clicked.connect(self.learning_hub_requested.emit)
        tools.addWidget(practice)
        tools.addWidget(learning_hub)
        tools.addStretch(1)
        self.container_layout.addLayout(tools)

        for index, stage in enumerate(self.catalog.content.stages):
            card = self._stage_card(
                stage,
                completed,
                started,
                expanded=index == self._first_incomplete_stage(completed),
            )
            self.container_layout.addWidget(card)
        self.container_layout.addStretch(1)

    def _first_incomplete_stage(self, completed: set[str]) -> int:
        for index, stage in enumerate(self.catalog.content.stages):
            if any(lesson.lesson_id not in completed for lesson in stage.lessons):
                return index
        return 0

    def _stage_card(
        self,
        stage: CourseStage,
        completed: set[str],
        started: set[str],
        *,
        expanded: bool,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("stageCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(4)

        header = QToolButton()
        header.setObjectName("stageHeader")
        header.setCheckable(True)
        header.setChecked(expanded)
        header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        progress_value = self.catalog.stage_progress(stage, completed)
        special = " · 安全与合规" if stage.special else ""
        header.setText(
            f"{stage.label}  {stage.name}\n"
            f"{progress_value}% · {len(stage.lessons)} 个知识点{special}"
        )
        header.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        card_layout.addWidget(header)

        lesson_buttons: list[QPushButton] = []
        for lesson in stage.lessons:
            state = self.catalog.lesson_state(lesson.lesson_id, completed, started)
            button = QPushButton()
            button.setObjectName("lessonRow")
            state_text = {
                LessonState.COMPLETED: "已完成",
                LessonState.LEARNING: "学习中",
                LessonState.TODO: "开始学习",
                LessonState.LOCKED: "未解锁",
            }[state]
            button.setText(f"{lesson.title}\n{lesson.minutes} 分钟 · {state_text}")
            button.setIcon(
                self.style().standardIcon(
                    {
                        LessonState.COMPLETED: QStyle.StandardPixmap.SP_DialogApplyButton,
                        LessonState.LEARNING: QStyle.StandardPixmap.SP_ArrowRight,
                        LessonState.TODO: QStyle.StandardPixmap.SP_ArrowRight,
                        LessonState.LOCKED: QStyle.StandardPixmap.SP_MessageBoxWarning,
                    }[state]
                )
            )
            button.setEnabled(state is not LessonState.LOCKED)
            button.clicked.connect(
                lambda _checked=False, lesson_id=lesson.lesson_id: self.lesson_requested.emit(
                    lesson_id
                )
            )
            card_layout.addWidget(button)
            lesson_buttons.append(button)
        for button in lesson_buttons:
            button.setVisible(expanded)

        def toggle(checked: bool) -> None:
            for lesson_button in lesson_buttons:
                lesson_button.setVisible(checked)
            header.setArrowType(
                Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
            )

        header.toggled.connect(toggle)
        return card
