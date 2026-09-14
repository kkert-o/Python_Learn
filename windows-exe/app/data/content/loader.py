from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import AppPaths
from app.data.content.validator import ContentValidationError, validate_content
from app.data.models import CourseContent


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ContentLoadResult:
    content: CourseContent
    source: Path
    used_fallback: bool = False
    warning: str | None = None


class ContentLoader:
    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths

    def load(self) -> ContentLoadResult:
        candidates = (
            self.paths.installed_content_path,
            self.paths.built_in_content_path,
        )
        errors: list[str] = []
        for index, path in enumerate(candidates):
            if not path.exists():
                continue
            try:
                raw = self._read_json(path)
                validate_content(raw)
                content = CourseContent.from_dict(raw)
                return ContentLoadResult(
                    content=content,
                    source=path,
                    used_fallback=index > 0,
                    warning=errors[-1] if index > 0 and errors else None,
                )
            except (OSError, json.JSONDecodeError, ContentValidationError, ValueError) as exc:
                message = f"内容文件无效，已忽略 {path}: {exc}"
                logger.warning(message)
                errors.append(message)

        raise ContentValidationError(
            "找不到有效的课程内容文件。"
            + (f" 最近错误：{errors[-1]}" if errors else "")
        )

    @staticmethod
    def _read_json(path: Path) -> Any:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)

