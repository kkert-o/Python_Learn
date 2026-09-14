from __future__ import annotations

import io
import textwrap
import tokenize
from dataclasses import dataclass

from app.training.models import TrainingExercise


@dataclass(frozen=True, slots=True)
class TrainingCheckResult:
    correct: bool
    message: str


class TrainingGrader:
    @staticmethod
    def check_choice(exercise: TrainingExercise, selected_index: int | None) -> bool:
        return selected_index is not None and selected_index == exercise.answer_index

    @classmethod
    def check_code(
        cls,
        exercise: TrainingExercise,
        submitted_code: str,
    ) -> TrainingCheckResult:
        normalized = cls._normalize(submitted_code, exercise.preserve_indentation)
        starter = cls._normalize(
            exercise.starter_code or "",
            exercise.preserve_indentation,
        )
        forbidden = next(
            (
                snippet
                for snippet in exercise.forbidden_snippets
                if cls._normalize(snippet, exercise.preserve_indentation) in normalized
            ),
            None,
        )
        if forbidden is not None:
            return TrainingCheckResult(False, f"代码里仍然保留了错误写法：{forbidden}")
        if not normalized or normalized == starter:
            return TrainingCheckResult(
                False,
                "还没有完成修改，先补上缺失部分或修复错误。",
            )
        missing = [
            snippet
            for snippet in exercise.required_snippets
            if cls._normalize(snippet, exercise.preserve_indentation) not in normalized
        ]
        if missing:
            return TrainingCheckResult(
                False,
                "还缺少必要的代码结构：" + "、".join(missing),
            )
        return TrainingCheckResult(
            True,
            "检查通过。代码已经包含完成任务所需的关键结构。",
        )

    @staticmethod
    def _normalize(code: str, preserve_indentation: bool) -> str:
        if preserve_indentation:
            return textwrap.dedent(code).strip().replace("\r\n", "\n")
        try:
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            return "".join(
                token.string
                for token in tokens
                if token.type
                not in {
                    tokenize.COMMENT,
                    tokenize.NL,
                    tokenize.NEWLINE,
                    tokenize.INDENT,
                    tokenize.DEDENT,
                    tokenize.ENCODING,
                    tokenize.ENDMARKER,
                }
            )
        except tokenize.TokenError:
            return "".join(
                line.split("#", 1)[0] for line in code.splitlines()
            ).replace(" ", "").replace("\t", "")

