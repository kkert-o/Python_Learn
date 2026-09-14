from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TrainingType(StrEnum):
    READ_CODE = "READ_CODE"
    PREDICT_OUTPUT = "PREDICT_OUTPUT"
    COMPLETE_CODE = "COMPLETE_CODE"
    DEBUG_LAB = "DEBUG_LAB"

    @property
    def label(self) -> str:
        return {
            TrainingType.READ_CODE: "看代码",
            TrainingType.PREDICT_OUTPUT: "预测输出",
            TrainingType.COMPLETE_CODE: "代码补全",
            TrainingType.DEBUG_LAB: "Debug Lab",
        }[self]

    @property
    def description(self) -> str:
        return {
            TrainingType.READ_CODE: "读懂变量、条件和循环",
            TrainingType.PREDICT_OUTPUT: "先判断结果，再运行验证",
            TrainingType.COMPLETE_CODE: "补上缺失的表达式或语句",
            TrainingType.DEBUG_LAB: "定位错误并写出修正后的代码",
        }[self]


@dataclass(frozen=True, slots=True)
class TrainingExercise:
    exercise_id: str
    lesson_id: str
    type: TrainingType
    title: str
    prompt: str
    code: str
    question: str
    explanation: str
    options: tuple[str, ...] = ()
    answer_index: int = -1
    hints: tuple[str, ...] = ()
    starter_code: str | None = None
    required_snippets: tuple[str, ...] = ()
    forbidden_snippets: tuple[str, ...] = ()
    stdin: str = ""
    reference_solution: str | None = None
    preserve_indentation: bool = False

    @property
    def is_code_task(self) -> bool:
        return self.starter_code is not None

