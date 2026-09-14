from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontDatabase
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

from app.config import AppPaths
from app.data.repositories import ProgressRepository
from app.runtime import PythonRunner, RunResult
from app.training import (
    TrainingExercise,
    TrainingGrader,
    TrainingType,
)
from app.ui.components import CodeEditor
from app.ui.components.common import clear_layout


class TrainingSessionScreen(QWidget):
    back_requested = Signal()
    workbench_requested = Signal(str, str)
    progress_changed = Signal()

    def __init__(
        self,
        paths: AppPaths,
        progress_repository: ProgressRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.paths = paths
        self.progress_repository = progress_repository
        self.exercises: list[TrainingExercise] = []
        self.index = 0
        self.session_title = "专项训练"
        self.selected_index: int | None = None
        self.credited: set[str] = set()
        self.current_correct = False
        self.show_hints = False
        self.show_solution = False
        self.check_result = None
        self.runner = PythonRunner(paths, self)
        self.runner.result_ready.connect(self._prediction_finished)
        self.runner.failed.connect(self._prediction_failed)

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

    def start_session(
        self,
        exercises: list[TrainingExercise],
        title: str = "专项训练",
    ) -> None:
        self.exercises = exercises
        self.index = 0
        self.session_title = title
        self.credited = set()
        self._reset_task()
        self._render()
        self.scroll.verticalScrollBar().setValue(0)

    def leave_session(self) -> None:
        self.runner.stop()
        self.back_requested.emit()

    def _reset_task(self) -> None:
        self.selected_index = None
        self.current_correct = False
        self.show_hints = False
        self.show_solution = False
        self.check_result = None

    def _render(self) -> None:
        clear_layout(self.container_layout)
        if not self.exercises:
            empty = QLabel("暂时没有可训练的内容。")
            empty.setObjectName("pageSubtitle")
            self.container_layout.addWidget(empty)
            return
        if self.index >= len(self.exercises):
            self._render_finished()
            return

        exercise = self.exercises[self.index]
        top = QHBoxLayout()
        back = QPushButton("返回专项训练")
        back.clicked.connect(self.leave_session)
        top.addWidget(back)
        top.addStretch(1)
        self.container_layout.addLayout(top)

        title = QLabel(exercise.title)
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            f"{self.session_title} · 第 {self.index + 1} / {len(self.exercises)} 题"
        )
        subtitle.setObjectName("pageSubtitle")
        self.container_layout.addWidget(title)
        self.container_layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("practicePanel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 22)
        card_layout.setSpacing(10)
        type_label = QLabel(exercise.type.label)
        type_label.setObjectName("tagLabel")
        prompt = QLabel(exercise.prompt)
        prompt.setObjectName("mutedText")
        prompt.setWordWrap(True)
        card_layout.addWidget(type_label)
        card_layout.addWidget(prompt)
        card_layout.addWidget(self._code_view(exercise.code))
        question = QLabel(exercise.question)
        question.setObjectName("quizQuestion")
        question.setWordWrap(True)
        card_layout.addWidget(question)

        if exercise.is_code_task:
            self._render_code_task(card_layout, exercise)
        else:
            self._render_choice_task(card_layout, exercise)
        self.container_layout.addWidget(card)

        self.next_button = QPushButton(
            "完成训练"
            if self.index == len(self.exercises) - 1
            else "下一题"
        )
        self.next_button.setObjectName("primaryButton")
        self.next_button.setEnabled(self.current_correct)
        self.next_button.clicked.connect(self._next)
        self.container_layout.addWidget(
            self.next_button,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        self.container_layout.addStretch(1)

    def _render_choice_task(
        self,
        layout: QVBoxLayout,
        exercise: TrainingExercise,
    ) -> None:
        self.option_buttons: list[QPushButton] = []
        for index, option in enumerate(exercise.options):
            button = QPushButton(f"{chr(ord('A') + index)}. {option}")
            button.setObjectName("quizOption")
            button.clicked.connect(
                lambda _checked=False, value=index: self._choose(value)
            )
            layout.addWidget(button)
            self.option_buttons.append(button)
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)
        self.explanation = QLabel()
        self.explanation.setObjectName("mutedText")
        self.explanation.setWordWrap(True)
        layout.addWidget(self.explanation)
        if exercise.type is TrainingType.PREDICT_OUTPUT:
            self.run_button = QPushButton("运行验证")
            self.run_button.clicked.connect(self._run_prediction)
            self.run_button.setEnabled(False)
            layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.run_output = QLabel()
        self.run_output.setWordWrap(True)
        self.run_output.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.run_output)
        self._refresh_options()

    def _render_code_task(
        self,
        layout: QVBoxLayout,
        exercise: TrainingExercise,
    ) -> None:
        self.code_editor = CodeEditor()
        self.code_editor.setPlainText(exercise.starter_code or exercise.code)
        self.code_editor.setFixedHeight(260)
        layout.addWidget(self.code_editor)

        button_row = QHBoxLayout()
        hints_button = QPushButton("查看提示")
        hints_button.clicked.connect(self._toggle_hints)
        check_button = QPushButton("检查代码")
        check_button.setObjectName("primaryButton")
        check_button.clicked.connect(self._check_code)
        workbench = QPushButton("在运行台继续编辑")
        workbench.clicked.connect(
            lambda _checked=False, exercise=exercise: self.workbench_requested.emit(
                exercise.title,
                self.code_editor.toPlainText(),
            )
        )
        button_row.addWidget(hints_button)
        button_row.addWidget(check_button)
        button_row.addStretch(1)
        button_row.addWidget(workbench)
        layout.addLayout(button_row)

        self.hints_view = QPlainTextEdit()
        self.hints_view.setReadOnly(True)
        self.hints_view.setMaximumHeight(110)
        self.hints_view.setVisible(False)
        layout.addWidget(self.hints_view)
        self.check_label = QLabel()
        self.check_label.setWordWrap(True)
        layout.addWidget(self.check_label)
        self.solution_view = QPlainTextEdit()
        self.solution_view.setReadOnly(True)
        self.solution_view.setMaximumHeight(180)
        self.solution_view.setVisible(False)
        layout.addWidget(self.solution_view)

    def _choose(self, index: int) -> None:
        exercise = self.exercises[self.index]
        self.selected_index = index
        correct = TrainingGrader.check_choice(exercise, index)
        self.current_correct = correct
        if correct:
            self._record_result(exercise, True)
        else:
            self.progress_repository.record_training_result(
                exercise.exercise_id,
                False,
            )
            self.progress_changed.emit()
        self._refresh_options()
        self.next_button.setEnabled(correct)

    def _refresh_options(self) -> None:
        exercise = self.exercises[self.index]
        for index, button in enumerate(self.option_buttons):
            is_selected = self.selected_index == index
            is_correct = index == exercise.answer_index
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
            button.setEnabled(not (self.current_correct and is_correct))
        if self.selected_index is None:
            self.feedback.clear()
            self.explanation.clear()
        else:
            self.feedback.setText(
                "回答正确。" if self.current_correct else "这次还不对，看看原因后再试。"
            )
            self.feedback.setObjectName(
                "quizCorrect" if self.current_correct else "quizWrong"
            )
            self.feedback.style().unpolish(self.feedback)
            self.feedback.style().polish(self.feedback)
            self.explanation.setText(exercise.explanation)
        if hasattr(self, "run_button"):
            self.run_button.setEnabled(self.selected_index is not None)

    def _run_prediction(self) -> None:
        if self.runner.is_running:
            return
        exercise = self.exercises[self.index]
        run_dir = self.paths.projects_dir / "training_runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        script = run_dir / f"{exercise.exercise_id}.py"
        script.write_text(exercise.code, encoding="utf-8")
        self.run_output.setText("正在运行验证...")
        self.run_button.setEnabled(False)
        self.runner.start(
            code=exercise.code,
            script_path=script,
            working_directory=run_dir,
        )

    def _prediction_finished(self, result: RunResult) -> None:
        if result.exit_code == 0:
            output = result.stdout.strip() or "（没有输出）"
            self.run_output.setText(f"实际输出：{output}")
        else:
            self.run_output.setText(f"实际结果：运行失败\n{result.stderr.strip()}")
        if hasattr(self, "run_button"):
            self.run_button.setEnabled(True)

    def _prediction_failed(self, message: str) -> None:
        self.run_output.setText(message)
        if hasattr(self, "run_button"):
            self.run_button.setEnabled(True)

    def _toggle_hints(self) -> None:
        self.show_hints = not self.show_hints
        exercise = self.exercises[self.index]
        self.hints_view.setPlainText(
            "\n".join(
                f"{index + 1}. {hint}"
                for index, hint in enumerate(exercise.hints)
            )
        )
        self.hints_view.setVisible(self.show_hints)

    def _check_code(self) -> None:
        if not hasattr(self, "code_editor"):
            return
        exercise = self.exercises[self.index]
        result = TrainingGrader.check_code(
            exercise,
            self.code_editor.toPlainText(),
        )
        self.check_result = result
        self.current_correct = result.correct
        self.check_label.setText(result.message)
        self.check_label.setObjectName(
            "quizCorrect" if result.correct else "quizWrong"
        )
        self.check_label.style().unpolish(self.check_label)
        self.check_label.style().polish(self.check_label)
        if result.correct:
            self._record_result(exercise, True)
        else:
            self.progress_repository.record_training_result(
                exercise.exercise_id,
                False,
            )
            self.progress_changed.emit()
            if exercise.reference_solution:
                self.show_solution = True
                self.solution_view.setPlainText(exercise.reference_solution)
                self.solution_view.setVisible(True)
        self.next_button.setEnabled(result.correct)

    def _record_result(self, exercise: TrainingExercise, correct: bool) -> None:
        if not correct or exercise.exercise_id in self.credited:
            return
        self.progress_repository.record_training_result(exercise.exercise_id, True)
        self.credited.add(exercise.exercise_id)
        self.progress_changed.emit()

    def _next(self) -> None:
        if not self.current_correct:
            return
        self.index += 1
        self._reset_task()
        self._render()
        self.scroll.verticalScrollBar().setValue(0)

    def _render_finished(self) -> None:
        result = QLabel(
            f"训练完成\n本次通过 {len(self.credited)} / {len(self.exercises)} 题"
        )
        result.setObjectName("practiceResult")
        result.setWordWrap(True)
        back = QPushButton("返回专项训练")
        back.setObjectName("primaryButton")
        back.clicked.connect(self.leave_session)
        self.container_layout.addWidget(result)
        self.container_layout.addWidget(back)
        self.container_layout.addStretch(1)

    @staticmethod
    def _code_view(code: str) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setPlainText(code)
        view.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        view.setMaximumHeight(190)
        return view

