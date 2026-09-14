from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ReviewTargetType(StrEnum):
    LESSON = "lesson"
    TRAINING = "training"
    QUIZ = "quiz"


@dataclass(frozen=True, slots=True)
class ReviewTransition:
    due_at: int
    review_stage: int


class ReviewScheduler:
    INTERVAL_DAYS = (1, 3, 7, 14, 30)
    DAY_MS = 24 * 60 * 60 * 1000

    @classmethod
    def lesson_key(cls, lesson_id: str) -> str:
        return f"{ReviewTargetType.LESSON.value}:{lesson_id}"

    @classmethod
    def training_key(cls, exercise_id: str) -> str:
        return f"{ReviewTargetType.TRAINING.value}:{exercise_id}"

    @classmethod
    def quiz_key(cls, question: str) -> str:
        return f"{ReviewTargetType.QUIZ.value}:{question}"

    @classmethod
    def next_review(
        cls,
        *,
        now_ms: int,
        correct: bool,
        current_stage: int | None = None,
    ) -> ReviewTransition:
        if not correct:
            stage = 0
        elif current_stage is None:
            stage = 0
        else:
            stage = min(current_stage + 1, len(cls.INTERVAL_DAYS) - 1)
        return ReviewTransition(
            due_at=now_ms + cls.INTERVAL_DAYS[stage] * cls.DAY_MS,
            review_stage=stage,
        )

