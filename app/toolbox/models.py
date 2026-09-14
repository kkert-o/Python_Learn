from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LibraryCategory(StrEnum):
    NETWORK = "网络与 API"
    DATA = "数据处理"
    DATABASE = "数据库"
    WEB = "Web 开发"
    TESTING = "测试与质量"
    AI = "AI 应用"
    TOOLS = "工程工具"


@dataclass(frozen=True, slots=True)
class LibraryEntry:
    library_id: str
    name: str
    import_name: str
    category: LibraryCategory
    summary: str
    use_case: str
    install: str
    example: str
    lesson_id: str | None = None


@dataclass(frozen=True, slots=True)
class ErrorMuseumEntry:
    error_id: str
    title: str
    error_type: str
    symptom: str
    cause: str
    broken_code: str
    fixed_code: str
    prevention: str
    lesson_id: str | None = None


class EngineeringCategory(StrEnum):
    GIT = "Git 版本管理"
    QUALITY = "代码质量"
    TESTING = "测试"


@dataclass(frozen=True, slots=True)
class EngineeringModule:
    module_id: str
    title: str
    category: EngineeringCategory
    summary: str
    checklist: tuple[str, ...]
    commands: tuple[str, ...]
    lesson_id: str | None = None


class SearchResultKind(StrEnum):
    LESSON = "课程"
    PROJECT = "项目"
    TRAINING = "训练"
    LIBRARY = "第三方库"
    ERROR = "错误博物馆"
    ENGINEERING = "工程实践"


@dataclass(frozen=True, slots=True)
class GlobalSearchResult:
    result_id: str
    title: str
    subtitle: str
    kind: SearchResultKind
    route_id: str

    @property
    def favorite_key(self) -> str:
        return f"{self.kind.value}:{self.route_id}"

