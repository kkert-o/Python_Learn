from __future__ import annotations

from app.bootstrap import bootstrap
from app.data.database.migrations import CURRENT_SCHEMA_VERSION
from app.data.models import LessonState
from app.learning import CourseCatalog, ReviewScheduler


def test_course_catalog_unlock_sequence(app_paths) -> None:
    context = bootstrap(app_paths)
    catalog = CourseCatalog(context.content)
    first_id, second_id = catalog.ordered_lesson_ids[:2]
    assert catalog.lesson_state(first_id, set()) is LessonState.TODO
    assert catalog.lesson_state(second_id, set()) is LessonState.LOCKED
    assert catalog.lesson_state(second_id, {first_id}) is LessonState.TODO


def test_lesson_detail_keeps_quiz_code_notes_and_next_lesson(app_paths) -> None:
    context = bootstrap(app_paths)
    lesson = context.course_catalog.lesson("python")
    assert lesson is not None
    assert lesson.quiz is not None
    assert lesson.quiz.code == 'print("Hello")'
    assert lesson.example_notes[0].left == "print("
    assert lesson.next_lessons[0].lesson_id == "hello"


def test_progress_repository_completes_lessons_and_records_quiz(app_paths) -> None:
    context = bootstrap(app_paths)
    repository = context.progress_repository
    lesson_id = context.course_catalog.ordered_lesson_ids[0]
    lesson = context.course_catalog.lesson(lesson_id)
    assert lesson is not None and lesson.quiz is not None

    repository.record_lesson_started(lesson_id)
    assert lesson_id in repository.started_lesson_ids()
    repository.complete_lesson(lesson_id)
    assert lesson_id in repository.completed_lesson_ids()
    assert context.database.schema_version() == CURRENT_SCHEMA_VERSION

    repository.record_quiz_result(lesson.quiz.question, False)
    assert lesson.quiz.question in repository.wrong_quiz_questions()
    repository.record_quiz_result(lesson.quiz.question, True)
    result = repository.quiz_result(lesson.quiz.question)
    assert result is not None
    assert result[0] is True
    assert repository.due_review_count() == 0


def test_review_scheduler_advances_and_resets() -> None:
    next_review = ReviewScheduler.next_review(now_ms=0, correct=True)
    assert next_review.review_stage == 0
    assert next_review.due_at == ReviewScheduler.DAY_MS
    advanced = ReviewScheduler.next_review(
        now_ms=0,
        correct=True,
        current_stage=next_review.review_stage,
    )
    assert advanced.review_stage == 1
    reset = ReviewScheduler.next_review(
        now_ms=0,
        correct=False,
        current_stage=4,
    )
    assert reset.review_stage == 0
