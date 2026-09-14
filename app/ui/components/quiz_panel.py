from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.data.models import Quiz


class QuizPanel(QWidget):
    result_selected = Signal(str, bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.quiz: Quiz | None = None
        self.selected_index: int | None = None
        self.correct = False
        self.option_buttons: list[QPushButton] = []
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setObjectName("quizQuestion")
        self.code_view = QPlainTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        self.code_view.setMaximumHeight(120)
        self.options_layout = QVBoxLayout()
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        self.explanation = QLabel()
        self.explanation.setWordWrap(True)
        self.explanation.setObjectName("mutedText")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.question_label)
        layout.addWidget(self.code_view)
        layout.addLayout(self.options_layout)
        layout.addWidget(self.feedback)
        layout.addWidget(self.explanation)

    def set_quiz(self, quiz: Quiz, already_resolved: bool = False) -> None:
        self.quiz = quiz
        self.selected_index = quiz.answer_index if already_resolved else None
        self.correct = already_resolved
        self.question_label.setText(quiz.question)
        self.code_view.setPlainText(quiz.code)
        self.code_view.setVisible(bool(quiz.code.strip()))
        self._clear_options()
        for index, option in enumerate(quiz.options):
            button = QPushButton(f"{chr(ord('A') + index)}. {option}")
            button.setObjectName("quizOption")
            button.clicked.connect(lambda _checked=False, value=index: self._choose(value))
            self.options_layout.addWidget(button)
            self.option_buttons.append(button)
        self._refresh_options()
        self._refresh_feedback()

    def _clear_options(self) -> None:
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.option_buttons = []

    def _choose(self, index: int) -> None:
        if self.quiz is None:
            return
        self.selected_index = index
        self.correct = index == self.quiz.answer_index
        self._refresh_options()
        self._refresh_feedback()
        self.result_selected.emit(self.quiz.question, self.correct)

    def _refresh_options(self) -> None:
        if self.quiz is None:
            return
        for index, button in enumerate(self.option_buttons):
            is_selected = self.selected_index == index
            is_correct = index == self.quiz.answer_index
            button.setProperty(
                "result",
                "correct"
                if is_selected and is_correct
                else "wrong"
                if is_selected
                else "answer"
                if self.selected_index is not None and is_correct
                else "",
            )
            button.style().unpolish(button)
            button.style().polish(button)
            button.setEnabled(not (self.correct and is_correct))
            button.setCheckable(True)
            button.setChecked(is_selected)

    def _refresh_feedback(self) -> None:
        if self.quiz is None or self.selected_index is None:
            self.feedback.clear()
            self.explanation.clear()
            return
        self.feedback.setText("回答正确。" if self.correct else "还没有选对，可以再试一次。")
        self.feedback.setObjectName("quizCorrect" if self.correct else "quizWrong")
        self.feedback.style().unpolish(self.feedback)
        self.feedback.style().polish(self.feedback)
        self.explanation.setText(self.quiz.explanation)

