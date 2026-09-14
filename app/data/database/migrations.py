from __future__ import annotations


MIGRATIONS: dict[int, tuple[str, ...]] = {
    1: (
        """
        CREATE TABLE lesson_progress (
            lessonId TEXT PRIMARY KEY,
            completed INTEGER NOT NULL,
            updatedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE project_progress (
            projectId TEXT PRIMARY KEY,
            completed INTEGER NOT NULL,
            updatedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE training_progress (
            exerciseId TEXT PRIMARY KEY,
            completed INTEGER NOT NULL,
            needsReview INTEGER NOT NULL,
            correctCount INTEGER NOT NULL,
            wrongCount INTEGER NOT NULL,
            updatedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE quiz_progress (
            question TEXT PRIMARY KEY,
            resolved INTEGER NOT NULL,
            correctCount INTEGER NOT NULL,
            wrongCount INTEGER NOT NULL,
            updatedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE review_schedule (
            targetKey TEXT PRIMARY KEY,
            dueAt INTEGER NOT NULL,
            reviewStage INTEGER NOT NULL,
            lastReviewedAt INTEGER
        )
        """,
        """
        CREATE TABLE learning_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eventType TEXT,
            targetId TEXT,
            correct INTEGER,
            occurredAt INTEGER
        )
        """,
        """
        CREATE INDEX idx_learning_event_occurred_at
        ON learning_event(occurredAt)
        """,
        """
        CREATE TABLE python_projects (
            projectId TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rootPath TEXT NOT NULL,
            createdAt INTEGER NOT NULL,
            lastOpenedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE python_recent_files (
            path TEXT PRIMARY KEY,
            projectId TEXT,
            lastOpenedAt INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE python_run_history (
            runId TEXT PRIMARY KEY,
            projectId TEXT,
            scriptPath TEXT NOT NULL,
            startedAt INTEGER NOT NULL,
            durationMs INTEGER NOT NULL,
            exitCode INTEGER,
            success INTEGER NOT NULL,
            cancelled INTEGER NOT NULL
        )
        """,
        """
        CREATE INDEX idx_run_history_started_at
        ON python_run_history(startedAt DESC)
        """,
        """
        CREATE TABLE editor_state (
            path TEXT PRIMARY KEY,
            cursorPosition INTEGER,
            scrollPosition INTEGER,
            updatedAt INTEGER NOT NULL
        )
        """,
    )
}

MIGRATIONS[2] = (
    """
    CREATE TABLE graduation_milestones (
        projectId TEXT NOT NULL,
        milestoneKey TEXT NOT NULL,
        completed INTEGER NOT NULL,
        updatedAt INTEGER NOT NULL,
        PRIMARY KEY (projectId, milestoneKey)
    )
    """,
)


CURRENT_SCHEMA_VERSION = max(MIGRATIONS)
