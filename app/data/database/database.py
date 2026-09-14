from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.data.database.migrations import CURRENT_SCHEMA_VERSION, MIGRATIONS


class Database:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def migrate(self) -> int:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER NOT NULL
                )
                """
            )
            row = connection.execute(
                "SELECT version FROM schema_version LIMIT 1"
            ).fetchone()
            current = int(row["version"]) if row else 0
            has_version_row = row is not None

            if current > CURRENT_SCHEMA_VERSION:
                raise RuntimeError(
                    f"数据库版本 {current} 高于程序支持的 {CURRENT_SCHEMA_VERSION}"
                )

            for version in range(current + 1, CURRENT_SCHEMA_VERSION + 1):
                statements = MIGRATIONS.get(version)
                if statements is None:
                    raise RuntimeError(f"缺少数据库迁移：{version}")
                try:
                    for statement in statements:
                        connection.execute(statement)
                    if has_version_row:
                        connection.execute(
                            "UPDATE schema_version SET version = ?",
                            (version,),
                        )
                    else:
                        connection.execute(
                            "INSERT INTO schema_version(version) VALUES (?)",
                            (version,),
                        )
                        has_version_row = True
                except Exception:
                    connection.rollback()
                    raise
            return CURRENT_SCHEMA_VERSION

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def schema_version(self) -> int:
        with self.connect() as connection:
            table = connection.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = 'schema_version'
                """
            ).fetchone()
            if not table:
                return 0
            row = connection.execute(
                "SELECT version FROM schema_version LIMIT 1"
            ).fetchone()
            return int(row["version"]) if row else 0
