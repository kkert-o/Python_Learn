from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from app.data.database import Database


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass(frozen=True, slots=True)
class ProjectRecord:
    project_id: str
    name: str
    root_path: str
    created_at: int
    last_opened_at: int


@dataclass(frozen=True, slots=True)
class RecentFile:
    path: str
    project_id: str | None
    last_opened_at: int


@dataclass(frozen=True, slots=True)
class RunHistoryEntry:
    run_id: str
    project_id: str | None
    script_path: str
    started_at: int
    duration_ms: int
    exit_code: int | None
    success: bool
    cancelled: bool


@dataclass(frozen=True, slots=True)
class EditorState:
    path: str
    cursor_position: int
    scroll_position: int
    updated_at: int


class WorkspaceRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def upsert_project(self, root_path: str | Path) -> ProjectRecord:
        path = Path(root_path).resolve()
        now = _now_ms()
        project_id = str(path).casefold()
        with self.database.transaction() as connection:
            existing = connection.execute(
                "SELECT createdAt FROM python_projects WHERE projectId = ?",
                (project_id,),
            ).fetchone()
            created_at = int(existing["createdAt"]) if existing else now
            connection.execute(
                """
                INSERT INTO python_projects(
                    projectId, name, rootPath, createdAt, lastOpenedAt
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(projectId) DO UPDATE SET
                    name = excluded.name,
                    rootPath = excluded.rootPath,
                    lastOpenedAt = excluded.lastOpenedAt
                """,
                (project_id, path.name, str(path), created_at, now),
            )
        return ProjectRecord(project_id, path.name, str(path), created_at, now)

    def list_projects(self, limit: int = 20) -> list[ProjectRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT projectId, name, rootPath, createdAt, lastOpenedAt
                FROM python_projects
                ORDER BY lastOpenedAt DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            ProjectRecord(
                project_id=str(row["projectId"]),
                name=str(row["name"]),
                root_path=str(row["rootPath"]),
                created_at=int(row["createdAt"]),
                last_opened_at=int(row["lastOpenedAt"]),
            )
            for row in rows
        ]

    def record_recent_file(
        self,
        path: str | Path,
        project_root: str | Path | None = None,
    ) -> None:
        file_path = str(Path(path).resolve())
        project_id = (
            str(Path(project_root).resolve()).casefold()
            if project_root is not None
            else None
        )
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO python_recent_files(path, projectId, lastOpenedAt)
                VALUES (?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    projectId = excluded.projectId,
                    lastOpenedAt = excluded.lastOpenedAt
                """,
                (file_path, project_id, _now_ms()),
            )

    def list_recent_files(self, limit: int = 10) -> list[RecentFile]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT path, projectId, lastOpenedAt
                FROM python_recent_files
                ORDER BY lastOpenedAt DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            RecentFile(
                path=str(row["path"]),
                project_id=str(row["projectId"]) if row["projectId"] else None,
                last_opened_at=int(row["lastOpenedAt"]),
            )
            for row in rows
        ]

    def record_run(
        self,
        *,
        run_id: str,
        script_path: str,
        started_at: int,
        duration_ms: int,
        exit_code: int | None,
        success: bool,
        cancelled: bool,
        project_root: str | Path | None = None,
    ) -> None:
        project_id = (
            str(Path(project_root).resolve()).casefold()
            if project_root is not None
            else None
        )
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO python_run_history(
                    runId, projectId, scriptPath, startedAt, durationMs,
                    exitCode, success, cancelled
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    project_id,
                    str(Path(script_path).resolve()),
                    started_at,
                    duration_ms,
                    exit_code,
                    1 if success else 0,
                    1 if cancelled else 0,
                ),
            )
            connection.execute(
                """
                DELETE FROM python_run_history
                WHERE runId NOT IN (
                    SELECT runId FROM python_run_history
                    ORDER BY startedAt DESC
                    LIMIT 100
                )
                """
            )

    def list_run_history(self, limit: int = 20) -> list[RunHistoryEntry]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT runId, projectId, scriptPath, startedAt, durationMs,
                       exitCode, success, cancelled
                FROM python_run_history
                ORDER BY startedAt DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            RunHistoryEntry(
                run_id=str(row["runId"]),
                project_id=str(row["projectId"]) if row["projectId"] else None,
                script_path=str(row["scriptPath"]),
                started_at=int(row["startedAt"]),
                duration_ms=int(row["durationMs"]),
                exit_code=int(row["exitCode"]) if row["exitCode"] is not None else None,
                success=bool(row["success"]),
                cancelled=bool(row["cancelled"]),
            )
            for row in rows
        ]

    def save_editor_state(
        self,
        path: str | Path,
        cursor_position: int,
        scroll_position: int,
    ) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO editor_state(
                    path, cursorPosition, scrollPosition, updatedAt
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    cursorPosition = excluded.cursorPosition,
                    scrollPosition = excluded.scrollPosition,
                    updatedAt = excluded.updatedAt
                """,
                (
                    str(Path(path).resolve()),
                    cursor_position,
                    scroll_position,
                    _now_ms(),
                ),
            )

    def get_editor_state(self, path: str | Path) -> EditorState | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT path, cursorPosition, scrollPosition, updatedAt
                FROM editor_state
                WHERE path = ?
                """,
                (str(Path(path).resolve()),),
            ).fetchone()
        if not row:
            return None
        return EditorState(
            path=str(row["path"]),
            cursor_position=int(row["cursorPosition"] or 0),
            scroll_position=int(row["scrollPosition"] or 0),
            updated_at=int(row["updatedAt"]),
        )

