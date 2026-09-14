from __future__ import annotations

from dataclasses import dataclass

from app.data.models import (
    CourseContent,
    CourseStage,
    LessonDetail,
    LessonState,
    LessonSummary,
)


@dataclass(frozen=True, slots=True)
class CourseProgressSummary:
    completed: int
    total: int
    percent: int
    next_lesson_id: str | None


class CourseCatalog:
    def __init__(self, content: CourseContent) -> None:
        self.content = content
        self.ordered_lesson_ids = tuple(
            lesson.lesson_id
            for stage in content.stages
            for lesson in stage.lessons
            if lesson.lesson_id in content.lessons
        )
        self._position = {
            lesson_id: index
            for index, lesson_id in enumerate(self.ordered_lesson_ids)
        }

    def lesson(self, lesson_id: str) -> LessonDetail | None:
        return self.content.lessons.get(lesson_id)

    def summary(self, lesson_id: str) -> LessonSummary | None:
        for stage in self.content.stages:
            for lesson in stage.lessons:
                if lesson.lesson_id == lesson_id:
                    return lesson
        return None

    def lesson_state(
        self,
        lesson_id: str,
        completed_ids: set[str],
        started_ids: set[str] | None = None,
    ) -> LessonState:
        if lesson_id in completed_ids:
            return LessonState.COMPLETED
        if lesson_id not in self._position:
            return LessonState.LOCKED
        index = self._position[lesson_id]
        if started_ids and lesson_id in started_ids:
            return LessonState.LEARNING
        if index == 0 or self.ordered_lesson_ids[index - 1] in completed_ids:
            return LessonState.TODO
        return LessonState.LOCKED

    def stage_progress(
        self,
        stage: CourseStage,
        completed_ids: set[str],
    ) -> int:
        total = len(stage.lessons)
        if total == 0:
            return 0
        completed = sum(
            lesson.lesson_id in completed_ids for lesson in stage.lessons
        )
        return round(completed * 100 / total)

    def overall_summary(self, completed_ids: set[str]) -> CourseProgressSummary:
        total = len(self.ordered_lesson_ids)
        completed = len(set(self.ordered_lesson_ids) & completed_ids)
        percent = round(completed * 100 / total) if total else 0
        return CourseProgressSummary(
            completed=completed,
            total=total,
            percent=percent,
            next_lesson_id=self.next_lesson_id(completed_ids),
        )

    def next_lesson_id(self, completed_ids: set[str]) -> str | None:
        for lesson_id in self.ordered_lesson_ids:
            if lesson_id not in completed_ids:
                return lesson_id
        return None

    def quiz_items(self) -> tuple[tuple[str, LessonDetail], ...]:
        return tuple(
            (lesson_id, detail)
            for lesson_id, detail in self.content.lessons.items()
            if detail.quiz is not None
        )

    def lesson_id_by_quiz_question(self, question: str) -> str | None:
        for lesson_id, detail in self.content.lessons.items():
            if detail.quiz is not None and detail.quiz.question == question:
                return lesson_id
        return None

