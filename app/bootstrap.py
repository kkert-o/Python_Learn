from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

from app.config import AppPaths
from app.data.content import ContentLoadResult, ContentLoader
from app.data.database import Database
from app.data.repositories import ProgressRepository, WorkspaceRepository
from app.learning import CourseCatalog
from app.projects import CourseProjectWorkspace, ProjectCatalog
from app.training import TrainingCatalog, training_catalog
from app.services.settings import SettingsService


@dataclass(slots=True)
class AppContext:
    paths: AppPaths
    settings: SettingsService
    database: Database
    content_result: ContentLoadResult
    progress_repository: ProgressRepository
    workspace_repository: WorkspaceRepository
    course_catalog: CourseCatalog
    training_catalog: TrainingCatalog
    project_catalog: ProjectCatalog
    project_workspace: CourseProjectWorkspace

    @property
    def content(self):
        return self.content_result.content


def configure_logging(paths: AppPaths) -> None:
    log_path = paths.logs_dir / "python-learner.log"
    handler = RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(item, RotatingFileHandler) for item in root.handlers):
        root.addHandler(handler)


def bootstrap(paths: AppPaths | None = None) -> AppContext:
    resolved_paths = paths or AppPaths.discover()
    resolved_paths.ensure()
    configure_logging(resolved_paths)
    settings = SettingsService(resolved_paths.settings_path)
    database = Database(resolved_paths.database_path)
    database.migrate()
    content_result = ContentLoader(resolved_paths).load()
    if content_result.used_fallback and content_result.warning:
        logging.getLogger(__name__).warning(content_result.warning)
    content = content_result.content
    return AppContext(
        paths=resolved_paths,
        settings=settings,
        database=database,
        content_result=content_result,
        progress_repository=ProgressRepository(database),
        workspace_repository=WorkspaceRepository(database),
        course_catalog=CourseCatalog(content),
        training_catalog=training_catalog,
        project_catalog=ProjectCatalog(content.projects),
        project_workspace=CourseProjectWorkspace(resolved_paths),
    )
