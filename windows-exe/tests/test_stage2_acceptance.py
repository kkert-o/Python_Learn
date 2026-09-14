from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from app.data.models import LessonState
from app.ui.components import QuizPanel
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def test_stage2_course_quiz_workbench_and_persistence(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    catalog = context.course_catalog
    first_id, second_id = catalog.ordered_lesson_ids[:2]
    assert catalog.lesson_state(second_id, set()) is LessonState.LOCKED

    window._open_lesson(first_id)
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_LESSON
    first_lesson = catalog.lesson(first_id)
    assert first_lesson is not None and first_lesson.quiz is not None

    quiz_panel = window.lesson_screen.findChild(QuizPanel)
    assert quiz_panel is not None
    quiz_panel.option_buttons[first_lesson.quiz.answer_index].click()
    assert quiz_panel.correct is True

    window.lesson_screen._complete_lesson()
    app.processEvents()
    assert first_id in context.progress_repository.completed_lesson_ids()
    assert (
        catalog.lesson_state(second_id, context.progress_repository.completed_lesson_ids())
        is LessonState.TODO
    )
    second_lesson = catalog.lesson(second_id)
    assert second_lesson is not None
    assert second_lesson.title in window.home_screen.continue_text.text()

    window.workbench.open_code_snippet("测试示例", 'print("hello")')
    editor = window.workbench.current_editor()
    assert editor is not None
    assert editor.toPlainText() == 'print("hello")\n'

    window.navigate(2)
    app.processEvents()
    practice_panel = window.practice_screen.findChild(QuizPanel)
    assert practice_panel is not None
    assert practice_panel.quiz is not None
    practice_panel.option_buttons[practice_panel.quiz.answer_index].click()
    assert window.practice_screen.next_button.isEnabled()
    window.close()

    reloaded = bootstrap(app_paths)
    assert first_id in reloaded.progress_repository.completed_lesson_ids()


def test_stage2_screens_have_real_content(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.resize(1440, 900)
    window.show()
    app.processEvents()

    assert window.navigation.count() == 13
    window.navigate(1)
    app.processEvents()
    assert window.course_screen.catalog.content.stage_count == 16

    window._open_lesson("python")
    app.processEvents()
    assert window.lesson_screen.lesson is not None
    assert window.lesson_screen.lesson.title == "Python 是什么"

    window.navigate(4)
    app.processEvents()
    assert window.learning_hub_screen.catalog.content.lesson_count == 56
    window.close()
