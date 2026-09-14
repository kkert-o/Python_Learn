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
    QVBoxLayout,
    QWidget,
)

from app.data.models import LessonDetail, LessonState
from app.data.repositories import ProgressRepository
from app.learning import CourseCatalog
from app.ui.components.common import clear_layout
from app.ui.components.quiz_panel import QuizPanel


class LessonScreen(QWidget):
    back_requested = Signal()
    lesson_requested = Signal(str)
    workbench_requested = Signal(str, str)
    progress_changed = Signal()

    def __init__(
        self,
        catalog: CourseCatalog,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.catalog = catalog
        self.progress_repository = progress_repository
        self.lesson: LessonDetail | None = None
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(34, 24, 34, 34)
        self.container_layout.setSpacing(14)
        self.container_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.container)
        self.scroll = scroll
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def show_lesson(self, lesson_id: str) -> None:
        lesson = self.catalog.lesson(lesson_id)
        if lesson is None:
            return
        self.lesson = lesson
        if lesson_id not in self.progress_repository.started_lesson_ids():
            self.progress_repository.record_lesson_started(lesson_id)
        self._render()
        self.scroll.verticalScrollBar().setValue(0)

    def _render(self) -> None:
        if self.lesson is None:
            return
        lesson = self.lesson
        completed_ids = self.progress_repository.completed_lesson_ids()
        already_completed = lesson.lesson_id in completed_ids
        clear_layout(self.container_layout)

        top = QHBoxLayout()
        back = QPushButton("返回课程")
        back.clicked.connect(self.back_requested.emit)
        top.addWidget(back)
        top.addStretch(1)
        self.container_layout.addLayout(top)

        title = QLabel(lesson.title)
        title.setObjectName("pageTitle")
        meta = QLabel(
            f"{lesson.stage} · {lesson.level} · {lesson.minutes} 分钟 · "
            f"{'已完成' if already_completed else '学习中'}"
        )
        meta.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(meta)

        knowledge = self._section("①", "知识讲解")
        for paragraph in lesson.knowledge:
            knowledge.addWidget(self._paragraph(paragraph))
        knowledge.addWidget(self._code_block(lesson.example, lesson.title, True))
        for note in lesson.example_notes:
            row = QHBoxLayout()
            left = QLabel(note.left)
            left.setObjectName("codeNote")
            left.setMinimumWidth(125)
            right = self._paragraph(note.right)
            row.addWidget(left)
            row.addWidget(right, 1)
            knowledge.addLayout(row)

        why = self._section("②", "为什么需要它")
        for paragraph in lesson.why:
            why.addWidget(self._paragraph(paragraph))

        purpose = self._section("③", "它在真实项目中的用途")
        purpose.addWidget(self._paragraph(lesson.purpose))

        example = self._section("④", "Python 示例")
        example.addWidget(self._code_block(lesson.example, lesson.title, True))

        run = self._section("⑤", "在线运行代码")
        run.addWidget(
            self._paragraph(
                "把本节示例发送到 Python 工作台，可以直接运行、修改并再次运行。"
            )
        )
        run.addWidget(self._code_block(lesson.example, lesson.title, True))

        quiz_section = self._section("⑥", "小练习")
        if lesson.quiz is not None:
            quiz_panel = QuizPanel()
            existing = self.progress_repository.quiz_result(lesson.quiz.question)
            quiz_panel.set_quiz(lesson.quiz, already_resolved=bool(existing and existing[0]))
            quiz_panel.result_selected.connect(self._record_quiz)
            quiz_section.addWidget(quiz_panel)

        errors = self._section("⑦", "常见错误")
        for error in lesson.errors:
            error_title = QLabel(f"!  {error.title}")
            error_title.setObjectName("errorTitle")
            errors.addWidget(error_title)
            errors.addWidget(self._paragraph(error.detail))
            errors.addWidget(self._code_block(error.code, error.title, False))

        project = self._section("⑧", "项目中的实际使用")
        project.addWidget(
            self._paragraph(
                "它不会单独出现，而是会和其他知识一起组成真实程序。"
            )
        )
        if lesson.project_code.strip():
            project.addWidget(self._code_block(lesson.project_code, lesson.title, True))

        legal = self._section("⑨", "法律与合规")
        legal.addWidget(self._paragraph(lesson.legal_note))
        legal_info = QLabel(
            f"{lesson.legal_risk} · {lesson.legal_basis}\n"
            f"更新时间：{lesson.legal_updated} · 不构成法律意见"
        )
        legal_info.setObjectName("mutedText")
        legal_info.setWordWrap(True)
        legal.addWidget(legal_info)

        if lesson.next_lessons:
            next_section = self._section("⑩", "下一步学习")
            for next_lesson in lesson.next_lessons:
                state = self.catalog.lesson_state(
                    next_lesson.lesson_id,
                    completed_ids,
                    self.progress_repository.started_lesson_ids(),
                )
                button = QPushButton(
                    f"{next_lesson.title} · {next_lesson.minutes} 分钟"
                )
                button.setEnabled(state is not LessonState.LOCKED)
                button.clicked.connect(
                    lambda _checked=False, lesson_id=next_lesson.lesson_id: self.lesson_requested.emit(
                        lesson_id
                    )
                )
                next_section.addWidget(button)

        complete = QPushButton("本节已完成" if already_completed else "完成本节")
        complete.setObjectName("primaryButton")
        complete.setEnabled(not already_completed)
        complete.clicked.connect(self._complete_lesson)
        self.container_layout.addWidget(complete)
        self.container_layout.addStretch(1)

    def _section(self, number: str, title_text: str) -> QVBoxLayout:
        card = QFrame()
        card.setObjectName("lessonSection")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(9)
        title = QLabel(f"{number}  {title_text}")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        self.container_layout.addWidget(card)
        return layout

    @staticmethod
    def _paragraph(text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def _code_block(self, code: str, title: str, allow_send: bool) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        actions = QHBoxLayout()
        action_label = QLabel("Python 代码")
        action_label.setObjectName("mutedText")
        actions.addWidget(action_label)
        actions.addStretch(1)
        copy_button = QPushButton("复制")
        copy_button.clicked.connect(
            lambda _checked=False, text=code: QGuiApplication.clipboard().setText(text)
        )
        actions.addWidget(copy_button)
        if allow_send:
            send_button = QPushButton("发送到工作台")
            send_button.clicked.connect(
                lambda _checked=False, text=code, lesson_title=title: self.workbench_requested.emit(
                    lesson_title, text
                )
            )
            actions.addWidget(send_button)
        layout.addLayout(actions)

        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setPlainText(code)
        view.setObjectName("lessonCode")
        view.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        line_count = max(3, min(14, code.count("\n") + 1))
        view.setFixedHeight(28 + line_count * 22)
        layout.addWidget(view)
        return wrapper

    def _record_quiz(self, question: str, correct: bool) -> None:
        self.progress_repository.record_quiz_result(question, correct)
        self.progress_changed.emit()

    def _complete_lesson(self) -> None:
        if self.lesson is None:
            return
        self.progress_repository.complete_lesson(self.lesson.lesson_id)
        self.progress_changed.emit()
        self._render()
