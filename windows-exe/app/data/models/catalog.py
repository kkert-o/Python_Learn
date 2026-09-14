from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class LessonState(StrEnum):
    TODO = "TODO"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"
    LOCKED = "LOCKED"


@dataclass(frozen=True, slots=True)
class Quiz:
    question: str
    options: tuple[str, ...]
    answer_index: int
    explanation: str = ""
    code: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Quiz":
        return cls(
            question=str(raw.get("question", "")),
            options=tuple(str(item) for item in raw.get("options", [])),
            answer_index=int(raw.get("answerIndex", -1)),
            explanation=str(raw.get("explanation", "")),
            code=str(raw.get("code", "")),
        )


@dataclass(frozen=True, slots=True)
class ExampleNote:
    left: str
    right: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ExampleNote":
        return cls(
            left=str(raw.get("left", "")),
            right=str(raw.get("right", "")),
        )


@dataclass(frozen=True, slots=True)
class ErrorExample:
    title: str
    detail: str
    code: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ErrorExample":
        return cls(
            title=str(raw.get("title", "")),
            detail=str(raw.get("detail", raw.get("explanation", ""))),
            code=str(
                raw.get(
                    "code",
                    raw.get("brokenCode", raw.get("broken", "")),
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class LessonSummary:
    lesson_id: str
    title: str
    minutes: int
    state: LessonState = LessonState.TODO

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "LessonSummary":
        state_value = str(raw.get("state", LessonState.TODO.value)).upper()
        try:
            state = LessonState(state_value)
        except ValueError:
            state = LessonState.TODO
        return cls(
            lesson_id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            minutes=int(raw.get("minutes", 0)),
            state=state,
        )


@dataclass(frozen=True, slots=True)
class CourseStage:
    label: str
    name: str
    lessons: tuple[LessonSummary, ...]
    progress: int = 0
    special: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CourseStage":
        return cls(
            label=str(raw.get("label", "")),
            name=str(raw.get("name", "")),
            lessons=tuple(
                LessonSummary.from_dict(item) for item in raw.get("lessons", [])
            ),
            progress=int(raw.get("progress", 0)),
            special=bool(raw.get("special", False)),
        )


@dataclass(frozen=True, slots=True)
class LessonDetail:
    lesson_id: str
    title: str
    stage: str
    level: str
    minutes: int
    knowledge: tuple[str, ...] = ()
    why: tuple[str, ...] = ()
    purpose: str = ""
    example: str = ""
    example_notes: tuple[ExampleNote, ...] = ()
    quiz: Quiz | None = None
    errors: tuple[ErrorExample, ...] = ()
    project_code: str = ""
    legal_risk: str = ""
    legal_note: str = ""
    legal_basis: str = ""
    legal_updated: str = ""
    next_lessons: tuple[LessonSummary, ...] = ()

    @classmethod
    def from_dict(cls, lesson_id: str, raw: dict[str, Any]) -> "LessonDetail":
        quiz_raw = raw.get("quiz")
        quiz = Quiz.from_dict(quiz_raw) if isinstance(quiz_raw, dict) else None
        return cls(
            lesson_id=lesson_id,
            title=str(raw.get("title", "")),
            stage=str(raw.get("stage", "")),
            level=str(raw.get("level", "")),
            minutes=int(raw.get("minutes", 0)),
            knowledge=tuple(str(item) for item in raw.get("knowledge", [])),
            why=tuple(str(item) for item in raw.get("why", [])),
            purpose=str(raw.get("purpose", "")),
            example=str(raw.get("example", "")),
            example_notes=tuple(
                ExampleNote.from_dict(item) for item in raw.get("exampleNotes", [])
            ),
            quiz=quiz,
            errors=tuple(
                ErrorExample.from_dict(item) for item in raw.get("errors", [])
            ),
            project_code=str(raw.get("projectCode", "")),
            legal_risk=str(raw.get("legalRisk", "")),
            legal_note=str(raw.get("legalNote", "")),
            legal_basis=str(raw.get("legalBasis", "")),
            legal_updated=str(raw.get("legalUpdated", "")),
            next_lessons=tuple(
                LessonSummary.from_dict(item) for item in raw.get("next", [])
            ),
        )


@dataclass(frozen=True, slots=True)
class ProjectInfo:
    project_id: str
    title: str
    level: str
    goal: str
    requirements: tuple[str, ...] = ()
    knowledge: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    starter: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ProjectInfo":
        return cls(
            project_id=str(raw.get("id", "")),
            title=str(raw.get("title", "")),
            level=str(raw.get("level", "")),
            goal=str(raw.get("goal", "")),
            requirements=tuple(str(item) for item in raw.get("requirements", [])),
            knowledge=tuple(str(item) for item in raw.get("knowledge", [])),
            hints=tuple(str(item) for item in raw.get("hints", [])),
            starter=str(raw.get("starter", "")),
        )


@dataclass(frozen=True, slots=True)
class CourseContent:
    version: int
    updated_at: str
    stages: tuple[CourseStage, ...]
    lessons: dict[str, LessonDetail] = field(default_factory=dict)
    projects: tuple[ProjectInfo, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CourseContent":
        lessons = {
            str(lesson_id): LessonDetail.from_dict(str(lesson_id), detail)
            for lesson_id, detail in raw.get("lessons", {}).items()
        }
        return cls(
            version=int(raw.get("version", 0)),
            updated_at=str(raw.get("updatedAt", "")),
            stages=tuple(CourseStage.from_dict(item) for item in raw.get("stages", [])),
            lessons=lessons,
            projects=tuple(
                ProjectInfo.from_dict(item) for item in raw.get("projects", [])
            ),
        )

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    @property
    def project_count(self) -> int:
        return len(self.projects)

    @property
    def stage_count(self) -> int:
        return len(self.stages)
