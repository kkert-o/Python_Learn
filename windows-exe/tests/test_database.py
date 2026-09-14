from __future__ import annotations

from app.data.database import Database
from app.data.database.migrations import CURRENT_SCHEMA_VERSION
from app.data.repositories import ProgressRepository, WorkspaceRepository


def test_database_migrates_to_current_schema(app_paths) -> None:
    database = Database(app_paths.database_path)
    assert database.migrate() == CURRENT_SCHEMA_VERSION
    assert database.schema_version() == CURRENT_SCHEMA_VERSION
    with database.connect() as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert {
        "schema_version",
        "lesson_progress",
        "python_projects",
        "python_recent_files",
        "python_run_history",
        "editor_state",
        "graduation_milestones",
    }.issubset(tables)


def test_database_migrates_existing_version_one(app_paths) -> None:
    database = Database(app_paths.database_path)
    with database.connect() as connection:
        connection.execute(
            "CREATE TABLE schema_version (version INTEGER NOT NULL)"
        )
        connection.execute(
            "INSERT INTO schema_version(version) VALUES (1)"
        )
        connection.commit()
    assert database.migrate() == CURRENT_SCHEMA_VERSION
    with database.connect() as connection:
        table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'graduation_milestones'
            """
        ).fetchone()
    assert table is not None


def test_progress_snapshot_starts_empty(app_paths) -> None:
    database = Database(app_paths.database_path)
    database.migrate()
    snapshot = ProgressRepository(database).snapshot()
    assert snapshot.completed_lessons == 0
    assert snapshot.completed_projects == 0
    assert snapshot.total_events == 0


def test_workspace_repository_round_trip(app_paths, tmp_path) -> None:
    database = Database(app_paths.database_path)
    database.migrate()
    repository = WorkspaceRepository(database)
    project_root = tmp_path / "demo"
    project_root.mkdir()
    script = project_root / "main.py"
    script.write_text('print("hello")', encoding="utf-8")

    project = repository.upsert_project(project_root)
    repository.record_recent_file(script, project_root)
    repository.record_run(
        run_id="run-1",
        script_path=str(script),
        started_at=1,
        duration_ms=125,
        exit_code=0,
        success=True,
        cancelled=False,
        project_root=project_root,
    )

    assert repository.list_projects()[0].project_id == project.project_id
    assert repository.list_recent_files()[0].path == str(script)
    run = repository.list_run_history()[0]
    assert run.run_id == "run-1"
    assert run.success is True
