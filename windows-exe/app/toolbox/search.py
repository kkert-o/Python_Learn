from __future__ import annotations

from app.data.models import CourseContent
from app.projects import ProjectCatalog
from app.toolbox.catalog import (
    EngineeringCatalog,
    ErrorMuseumCatalog,
    LibraryCatalog,
)
from app.toolbox.models import GlobalSearchResult, SearchResultKind
from app.training import TrainingCatalog


class GlobalSearchEngine:
    @staticmethod
    def all_results(
        content: CourseContent,
        training_catalog: TrainingCatalog,
        project_catalog: ProjectCatalog,
    ) -> list[GlobalSearchResult]:
        results: list[GlobalSearchResult] = []
        for lesson in content.lessons.values():
            results.append(
                GlobalSearchResult(
                    lesson.lesson_id,
                    lesson.title,
                    lesson.stage,
                    SearchResultKind.LESSON,
                    lesson.lesson_id,
                )
            )
        for project in project_catalog.all:
            results.append(
                GlobalSearchResult(
                    project.project_id,
                    project.title,
                    project.level,
                    SearchResultKind.PROJECT,
                    project.project_id,
                )
            )
        for exercise in training_catalog.all:
            results.append(
                GlobalSearchResult(
                    exercise.exercise_id,
                    exercise.title,
                    exercise.type.label,
                    SearchResultKind.TRAINING,
                    exercise.exercise_id,
                )
            )
        for library in LibraryCatalog.all:
            results.append(
                GlobalSearchResult(
                    library.library_id,
                    library.name,
                    library.category.value,
                    SearchResultKind.LIBRARY,
                    library.library_id,
                )
            )
        for error in ErrorMuseumCatalog.all:
            results.append(
                GlobalSearchResult(
                    error.error_id,
                    error.title,
                    error.error_type,
                    SearchResultKind.ERROR,
                    error.error_id,
                )
            )
        for module in EngineeringCatalog.all:
            results.append(
                GlobalSearchResult(
                    module.module_id,
                    module.title,
                    module.category.value,
                    SearchResultKind.ENGINEERING,
                    module.module_id,
                )
            )
        return results

    @classmethod
    def search(
        cls,
        query: str,
        content: CourseContent,
        training_catalog: TrainingCatalog,
        project_catalog: ProjectCatalog,
        limit: int = 30,
    ) -> list[GlobalSearchResult]:
        needle = query.strip().casefold()
        if not needle:
            return []
        return [
            result
            for result in cls.all_results(
                content,
                training_catalog,
                project_catalog,
            )
            if needle
            in f"{result.title} {result.subtitle}".casefold()
        ][:limit]

    @classmethod
    def resolve(
        cls,
        favorite_key: str,
        content: CourseContent,
        training_catalog: TrainingCatalog,
        project_catalog: ProjectCatalog,
    ) -> GlobalSearchResult | None:
        return next(
            (
                result
                for result in cls.all_results(
                    content,
                    training_catalog,
                    project_catalog,
                )
                if result.favorite_key == favorite_key
            ),
            None,
        )
