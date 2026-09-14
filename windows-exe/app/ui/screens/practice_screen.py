from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.data.models import LessonDetail
from app.data.repositories import ProgressRepository
from app.learning import CourseCatalog
from app.ui.components import QuizPanel
from app.ui.components.common import clear_layout


@dataclass(frozen=True, slots=True)
class PracticeItem:
    lesson_id: str
    lesson: LessonDetail


class PracticeScreen(QWidget):
    progress_changed = Signal()
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
        self.items: list[PracticeItem] = []
        self.index = 0
        self.correct_count = 0
        self.answered_current = False

        self.title = QLabel("综合练习")
        self.title.setObjectName("pageTitle")
        self.progress_label = QLabel()
        self.progress_label.setObjectName("pageSubtitle")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.panel = QFrame()
        self.panel.setObjectName("practicePanel")
        self.panel_layout = QVBoxLayout(self.panel)
        self.panel_layout.setContentsMargins(22, 20, 22, 22)
        self.next_button = QPushButton("下一题")
        self.next_button.setObjectName("primaryButton")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._next)

        back = QPushButton("返回课程")
        back.clicked.connect(self.back_requested.emit)
        header = QHBoxLayout()
        header.addWidget(back)
        header.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 24, 34, 30)
        layout.setSpacing(13)
        layout.addLayout(header)
        layout.addWidget(self.title)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.panel, 1)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.start()

    def start(self) -> None:
        self.items = [
            PracticeItem(lesson_id, detail)
            for lesson_id, detail in self.catalog.quiz_items()
            if detail.quiz is not None
        ]
        self.index = 0
        self.correct_count = 0
        self.answered_current = False
        self._render()

    def _render(self) -> None:
        self._clear_panel()
        total = len(self.items)
        if not total:
            self.progress_label.setText("当前没有可用练习题")
            return
        if self.index >= total:
            self._render_finished()
            return
        item = self.items[self.index]
        self.progress_label.setText(
            f"第 {self.index + 1} / {total} 题 · 已答对 {self.correct_count} 题"
        )
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(self.index)
        quiz = item.lesson.quiz
        if quiz is None:
            self.index += 1
            self._render()
            return
        source = QLabel(f"来源：{item.lesson.title}")
        source.setObjectName("mutedText")
        panel = QuizPanel()
        panel.set_quiz(quiz)
        panel.result_selected.connect(self._record_result)
        self.panel_layout.addWidget(source)
        self.panel_layout.addWidget(panel, 1)
        self.next_button.setEnabled(False)
        self.next_button.setText("完成练习" if self.index == total - 1 else "下一题")

    def _clear_panel(self) -> None:
        clear_layout(self.panel_layout)

    def _record_result(self, question: str, correct: bool) -> None:
        self.progress_repository.record_quiz_result(question, correct)
        self.progress_changed.emit()
        if correct:
            self.correct_count += 1
            self.next_button.setEnabled(True)
        self.answered_current = True

    def _next(self) -> None:
        if not self.answered_current:
            return
        self.index += 1
        self.answered_current = False
        self._render()

    def _render_finished(self) -> None:
        self.progress_bar.setValue(len(self.items))
        self.progress_label.setText(
            f"练习完成 · 答对 {self.correct_count} / {len(self.items)}"
        )
        result = QLabel(
            f"本次答对 {self.correct_count} 题。\n"
            "答错的内容已经进入复习记录。"
        )
        result.setObjectName("practiceResult")
        result.setWordWrap(True)
        restart = QPushButton("重新开始")
        restart.setObjectName("primaryButton")
        restart.clicked.connect(self.start)
        review = QPushButton("回到课程复习")
        review.clicked.connect(self.back_requested.emit)
        self.panel_layout.addWidget(result)
        self.panel_layout.addWidget(restart)
        self.panel_layout.addWidget(review)
        self.panel_layout.addStretch(1)
        self.next_button.setEnabled(False)
