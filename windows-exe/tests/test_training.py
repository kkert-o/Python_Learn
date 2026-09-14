from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from app.training import TrainingGrader, TrainingType
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def test_training_catalog_has_all_four_types() -> None:
    from app.training import training_catalog

    assert len(training_catalog.all) == 20
    assert {
        training_type: len(training_catalog.by_type(training_type))
        for training_type in TrainingType
    } == {
        TrainingType.READ_CODE: 4,
        TrainingType.PREDICT_OUTPUT: 4,
        TrainingType.COMPLETE_CODE: 4,
        TrainingType.DEBUG_LAB: 8,
    }


def test_training_reference_solutions_pass_and_starters_fail() -> None:
    from app.training import training_catalog

    code_tasks = [exercise for exercise in training_catalog.all if exercise.is_code_task]
    assert len(code_tasks) == 12
    for exercise in code_tasks:
        assert exercise.reference_solution is not None
        reference = TrainingGrader.check_code(
            exercise,
            exercise.reference_solution,
        )
        assert reference.correct, exercise.exercise_id
        starter = TrainingGrader.check_code(
            exercise,
            exercise.starter_code or "",
        )
        assert not starter.correct, exercise.exercise_id


def test_training_progress_records_and_clears_review(app_paths) -> None:
    context = bootstrap(app_paths)
    repository = context.progress_repository
    repository.record_training_result("read-variable", False)
    assert "read-variable" in repository.training_needs_review_ids()
    repository.record_training_result("read-variable", True)
    assert "read-variable" not in repository.training_needs_review_ids()
    assert "read-variable" in repository.completed_training_ids()
    result = repository.training_result("read-variable")
    assert result == (True, False, 1, 1)


def test_training_ui_choice_code_and_review_flow(app_paths) -> None:
    from app.training import training_catalog

    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_TRAINING)
    app.processEvents()
    assert window.training_center_screen.catalog.all

    choice = training_catalog.by_type(TrainingType.READ_CODE)[0]
    window._start_training_session([choice], "测试训练")
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_TRAINING_SESSION
    window.training_session_screen.option_buttons[choice.answer_index].click()
    assert window.training_session_screen.next_button.isEnabled()
    assert choice.exercise_id in context.progress_repository.completed_training_ids()

    code_task = next(
        exercise
        for exercise in training_catalog.by_type(TrainingType.COMPLETE_CODE)
        if exercise.exercise_id == "complete-range"
    )
    window._start_training_session([code_task], "代码补全")
    app.processEvents()
    window.training_session_screen.code_editor.setPlainText(
        code_task.reference_solution or ""
    )
    window.training_session_screen._check_code()
    assert window.training_session_screen.current_correct is True
    assert code_task.exercise_id in context.progress_repository.completed_training_ids()

    wrong = training_catalog.by_type(TrainingType.READ_CODE)[1]
    window._start_training_session([wrong], "错题")
    app.processEvents()
    wrong_index = next(
        index
        for index in range(len(wrong.options))
        if index != wrong.answer_index
    )
    window.training_session_screen.option_buttons[wrong_index].click()
    assert wrong.exercise_id in context.progress_repository.training_needs_review_ids()
    window.close()

