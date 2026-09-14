from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass

from app.data.database import Database
from app.learning.review import ReviewScheduler


@dataclass(frozen=True, slots=True)
class ProgressSnapshot:
    completed_lessons: int
    completed_projects: int
    completed_training: int
    review_due: int
    total_events: int


class ProgressRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def snapshot(self) -> ProgressSnapshot:
        with self.database.connect() as connection:
            return ProgressSnapshot(
                completed_lessons=self._count_where(
                    connection, "lesson_progress", "completed = 1"
                ),
                completed_projects=self._count_where(
                    connection, "project_progress", "completed = 1"
                ),
                completed_training=self._count_where(
                    connection, "training_progress", "completed = 1"
                ),
                review_due=self._count_where(
                    connection,
                    "review_schedule",
                    "dueAt <= ?",
                    (int(time.time() * 1000),),
                ),
                total_events=self._count_where(connection, "learning_event", "1 = 1"),
            )

    def completed_lesson_ids(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT lessonId FROM lesson_progress WHERE completed = 1"
            ).fetchall()
        return {str(row["lessonId"]) for row in rows}

    def started_lesson_ids(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT targetId
                FROM learning_event
                WHERE eventType = 'lesson_started' AND targetId IS NOT NULL
                """
            ).fetchall()
        return {str(row["targetId"]) for row in rows}

    def record_lesson_started(self, lesson_id: str) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO learning_event(eventType, targetId, correct, occurredAt)
                VALUES ('lesson_started', ?, NULL, ?)
                """,
                (lesson_id, now),
            )

    def complete_lesson(self, lesson_id: str) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO lesson_progress(lessonId, completed, updatedAt)
                VALUES (?, 1, ?)
                ON CONFLICT(lessonId) DO UPDATE SET
                    completed = 1,
                    updatedAt = excluded.updatedAt
                """,
                (lesson_id, now),
            )
            connection.execute(
                """
                INSERT INTO learning_event(eventType, targetId, correct, occurredAt)
                VALUES ('lesson_completed', ?, 1, ?)
                """,
                (lesson_id, now),
            )
            self._schedule_review(
                connection,
                ReviewScheduler.lesson_key(lesson_id),
                correct=True,
                now_ms=now,
            )

    def is_lesson_completed(self, lesson_id: str) -> bool:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT completed FROM lesson_progress
                WHERE lessonId = ?
                """,
                (lesson_id,),
            ).fetchone()
        return bool(row and row["completed"])

    def record_quiz_result(self, question: str, correct: bool) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            existing = connection.execute(
                """
                SELECT resolved, correctCount, wrongCount
                FROM quiz_progress
                WHERE question = ?
                """,
                (question,),
            ).fetchone()
            correct_count = int(existing["correctCount"]) if existing else 0
            wrong_count = int(existing["wrongCount"]) if existing else 0
            if correct:
                correct_count += 1
            else:
                wrong_count += 1
            resolved = 1 if correct or (existing and existing["resolved"]) else 0
            connection.execute(
                """
                INSERT INTO quiz_progress(
                    question, resolved, correctCount, wrongCount, updatedAt
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(question) DO UPDATE SET
                    resolved = excluded.resolved,
                    correctCount = excluded.correctCount,
                    wrongCount = excluded.wrongCount,
                    updatedAt = excluded.updatedAt
                """,
                (question, resolved, correct_count, wrong_count, now),
            )
            connection.execute(
                """
                INSERT INTO learning_event(eventType, targetId, correct, occurredAt)
                VALUES ('quiz_answered', ?, ?, ?)
                """,
                (question, 1 if correct else 0, now),
            )
            self._schedule_review(
                connection,
                ReviewScheduler.quiz_key(question),
                correct=correct,
                now_ms=now,
            )

    def quiz_result(self, question: str) -> tuple[bool, int, int] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT resolved, correctCount, wrongCount
                FROM quiz_progress
                WHERE question = ?
                """,
                (question,),
            ).fetchone()
        if not row:
            return None
        return (
            bool(row["resolved"]),
            int(row["correctCount"]),
            int(row["wrongCount"]),
        )

    def wrong_quiz_questions(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT question FROM quiz_progress
                WHERE resolved = 0
                """
            ).fetchall()
        return {str(row["question"]) for row in rows}

    def due_review_count(self, now_ms: int | None = None) -> int:
        timestamp = now_ms if now_ms is not None else int(time.time() * 1000)
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM review_schedule WHERE dueAt <= ?",
                (timestamp,),
            ).fetchone()
        return int(row["count"]) if row else 0

    def record_training_result(self, exercise_id: str, correct: bool) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            existing = connection.execute(
                """
                SELECT completed, correctCount, wrongCount
                FROM training_progress
                WHERE exerciseId = ?
                """,
                (exercise_id,),
            ).fetchone()
            correct_count = int(existing["correctCount"]) if existing else 0
            wrong_count = int(existing["wrongCount"]) if existing else 0
            if correct:
                correct_count += 1
            else:
                wrong_count += 1
            completed = bool(existing and existing["completed"]) or correct
            connection.execute(
                """
                INSERT INTO training_progress(
                    exerciseId, completed, needsReview,
                    correctCount, wrongCount, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(exerciseId) DO UPDATE SET
                    completed = excluded.completed,
                    needsReview = excluded.needsReview,
                    correctCount = excluded.correctCount,
                    wrongCount = excluded.wrongCount,
                    updatedAt = excluded.updatedAt
                """,
                (
                    exercise_id,
                    1 if completed else 0,
                    0 if correct else 1,
                    correct_count,
                    wrong_count,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO learning_event(eventType, targetId, correct, occurredAt)
                VALUES ('training_answered', ?, ?, ?)
                """,
                (exercise_id, 1 if correct else 0, now),
            )
            self._schedule_review(
                connection,
                ReviewScheduler.training_key(exercise_id),
                correct=correct,
                now_ms=now,
            )

    def completed_training_ids(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT exerciseId FROM training_progress
                WHERE completed = 1
                """
            ).fetchall()
        return {str(row["exerciseId"]) for row in rows}

    def training_needs_review_ids(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT exerciseId FROM training_progress
                WHERE needsReview = 1
                """
            ).fetchall()
        return {str(row["exerciseId"]) for row in rows}

    def training_result(self, exercise_id: str) -> tuple[bool, bool, int, int] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT completed, needsReview, correctCount, wrongCount
                FROM training_progress
                WHERE exerciseId = ?
                """,
                (exercise_id,),
            ).fetchone()
        if not row:
            return None
        return (
            bool(row["completed"]),
            bool(row["needsReview"]),
            int(row["correctCount"]),
            int(row["wrongCount"]),
        )

    def completed_project_ids(self) -> set[str]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT projectId FROM project_progress WHERE completed = 1"
            ).fetchall()
        return {str(row["projectId"]) for row in rows}

    def complete_project(self, project_id: str) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO project_progress(projectId, completed, updatedAt)
                VALUES (?, 1, ?)
                ON CONFLICT(projectId) DO UPDATE SET
                    completed = 1,
                    updatedAt = excluded.updatedAt
                """,
                (project_id, now),
            )
            connection.execute(
                """
                INSERT INTO learning_event(eventType, targetId, correct, occurredAt)
                VALUES ('project_completed', ?, 1, ?)
                """,
                (project_id, now),
            )

    def is_project_completed(self, project_id: str) -> bool:
        return project_id in self.completed_project_ids()

    def set_graduation_milestone(
        self,
        project_id: str,
        milestone_key: str,
        completed: bool,
    ) -> None:
        now = int(time.time() * 1000)
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO graduation_milestones(
                    projectId, milestoneKey, completed, updatedAt
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(projectId, milestoneKey) DO UPDATE SET
                    completed = excluded.completed,
                    updatedAt = excluded.updatedAt
                """,
                (
                    project_id,
                    milestone_key,
                    1 if completed else 0,
                    now,
                ),
            )

    def graduation_milestones(self, project_id: str) -> dict[str, bool]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT milestoneKey, completed
                FROM graduation_milestones
                WHERE projectId = ?
                """,
                (project_id,),
            ).fetchall()
        return {
            str(row["milestoneKey"]): bool(row["completed"])
            for row in rows
        }

    def _schedule_review(
        self,
        connection: sqlite3.Connection,
        target_key: str,
        *,
        correct: bool,
        now_ms: int,
    ) -> None:
        existing = connection.execute(
            """
            SELECT reviewStage FROM review_schedule
            WHERE targetKey = ?
            """,
            (target_key,),
        ).fetchone()
        transition = ReviewScheduler.next_review(
            now_ms=now_ms,
            correct=correct,
            current_stage=int(existing["reviewStage"]) if existing else None,
        )
        connection.execute(
            """
            INSERT INTO review_schedule(
                targetKey, dueAt, reviewStage, lastReviewedAt
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(targetKey) DO UPDATE SET
                dueAt = excluded.dueAt,
                reviewStage = excluded.reviewStage,
                lastReviewedAt = excluded.lastReviewedAt
            """,
            (
                target_key,
                transition.due_at,
                transition.review_stage,
                now_ms,
            ),
        )

    @staticmethod
    def _count_where(
        connection: sqlite3.Connection,
        table: str,
        where: str,
        params: tuple[object, ...] = (),
    ) -> int:
        allowed_tables = {
            "lesson_progress",
            "project_progress",
            "training_progress",
            "review_schedule",
            "learning_event",
        }
        if table not in allowed_tables:
            raise ValueError(f"不支持的统计表：{table}")
        row = connection.execute(
            f"SELECT COUNT(*) AS count FROM {table} WHERE {where}",
            params,
        ).fetchone()
        return int(row["count"]) if row else 0
