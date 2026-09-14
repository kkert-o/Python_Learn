from __future__ import annotations

from app.data.models import ProjectInfo


class ProjectCatalog:
    def __init__(self, projects: tuple[ProjectInfo, ...]) -> None:
        self.all = projects
        self._by_id = {project.project_id: project for project in projects}

    def by_id(self, project_id: str) -> ProjectInfo | None:
        return self._by_id.get(project_id)

    @property
    def levels(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(project.level for project in self.all))

    def by_level(self, level: str) -> list[ProjectInfo]:
        return [project for project in self.all if project.level == level]

