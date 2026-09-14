from __future__ import annotations

from typing import Any


class ContentValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContentValidationError(message)


def validate_content(raw: Any) -> None:
    _require(isinstance(raw, dict), "内容根节点必须是 JSON 对象")
    version = raw.get("version")
    _require(isinstance(version, int) and version > 0, "内容 version 必须大于 0")
    _require(bool(str(raw.get("updatedAt", "")).strip()), "updatedAt 不能为空")

    stages = raw.get("stages")
    lessons = raw.get("lessons")
    projects = raw.get("projects")
    _require(isinstance(stages, list) and bool(stages), "stages 不能为空")
    _require(isinstance(lessons, dict) and bool(lessons), "lessons 不能为空")
    _require(isinstance(projects, list) and bool(projects), "projects 不能为空")

    summary_ids: set[str] = set()
    detail_ids: set[str] = set()
    for stage_index, stage in enumerate(stages):
        _require(isinstance(stage, dict), f"stages[{stage_index}] 必须是对象")
        stage_name = str(stage.get("name", "")).strip()
        _require(bool(stage_name), f"stages[{stage_index}].name 不能为空")
        stage_lessons = stage.get("lessons")
        _require(
            isinstance(stage_lessons, list) and bool(stage_lessons),
            f"阶段 {stage_name} 没有知识点",
        )
        for lesson_index, summary in enumerate(stage_lessons):
            _require(
                isinstance(summary, dict),
                f"阶段 {stage_name} 的 lessons[{lesson_index}] 必须是对象",
            )
            lesson_id = str(summary.get("id", "")).strip()
            _require(bool(lesson_id), f"阶段 {stage_name} 存在空知识点 ID")
            _require(
                lesson_id not in summary_ids,
                f"阶段中的知识点 ID 重复：{lesson_id}",
            )
            summary_ids.add(lesson_id)
            _require(
                lesson_id in lessons,
                f"知识点摘要缺少详情：{lesson_id}",
            )

    for lesson_id, detail in lessons.items():
        _require(bool(str(lesson_id).strip()), "lessons 中存在空 ID")
        _require(isinstance(detail, dict), f"知识点 {lesson_id} 的详情必须是对象")
        _require(
            str(detail.get("id", lesson_id)) == str(lesson_id),
            f"知识点详情 ID 与键不一致：{lesson_id}",
        )
        _require(str(detail.get("title", "")).strip(), f"知识点 {lesson_id} 标题为空")
        _require(str(detail.get("example", "")).strip(), f"知识点 {lesson_id} 示例为空")
        detail_ids.add(str(lesson_id))
        quiz = detail.get("quiz")
        _require(isinstance(quiz, dict), f"知识点 {lesson_id} 缺少小练习")
        options = quiz.get("options")
        _require(
            isinstance(options, list) and len(options) >= 2,
            f"知识点 {lesson_id} 小练习选项不足",
        )
        answer_index = quiz.get("answerIndex")
        _require(
            isinstance(answer_index, int) and 0 <= answer_index < len(options),
            f"知识点 {lesson_id} 小练习答案下标非法",
        )

    stray_details = detail_ids - summary_ids
    _require(not stray_details, f"存在游离知识点详情：{sorted(stray_details)}")

    project_ids: set[str] = set()
    for project_index, project in enumerate(projects):
        _require(isinstance(project, dict), f"projects[{project_index}] 必须是对象")
        project_id = str(project.get("id", "")).strip()
        _require(bool(project_id), f"projects[{project_index}] ID 为空")
        _require(project_id not in project_ids, f"项目 ID 重复：{project_id}")
        project_ids.add(project_id)
        _require(
            str(project.get("title", "")).strip(),
            f"项目 {project_id} 标题为空",
        )
        _require(
            str(project.get("goal", "")).strip(),
            f"项目 {project_id} 目标为空",
        )

