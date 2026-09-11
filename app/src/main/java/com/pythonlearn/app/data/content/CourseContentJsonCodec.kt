package com.pythonlearn.app.data.content

import com.google.gson.Gson
import com.google.gson.JsonSyntaxException

object CourseContentJsonCodec {
    fun decode(json: String, gson: Gson = Gson()): CourseContent {
        val payload = try {
            gson.fromJson(json, ContentPayloadDto::class.java)
        } catch (error: JsonSyntaxException) {
            throw IllegalArgumentException("课程内容不是有效的 JSON", error)
        } ?: throw IllegalArgumentException("课程内容为空")
        return payload.toDomain()
    }
}

object CourseContentValidator {
    fun validate(content: CourseContent): List<String> {
        val errors = mutableListOf<String>()
        if (content.version <= 0) {
            errors += "内容版本必须大于 0"
        }
        if (content.updatedAt.isBlank()) {
            errors += "缺少内容更新时间"
        }
        if (content.stages.isEmpty()) {
            errors += "课程阶段不能为空"
        }
        if (content.lessons.isEmpty()) {
            errors += "课程知识点不能为空"
        }
        if (content.projects.isEmpty()) {
            errors += "项目内容不能为空"
        }

        content.stages.forEach { stage ->
            if (stage.label.isBlank()) {
                errors += "阶段 ${stage.name} 缺少序号"
            }
            if (stage.name.isBlank()) {
                errors += "存在没有名称的课程阶段"
            }
            if (stage.lessons.isEmpty()) {
                errors += "阶段 ${stage.name} 没有知识点"
            }
            stage.lessons.forEach { summary ->
                val lesson = content.lessons[summary.id]
                if (lesson != null && lesson.stage != stage.name) {
                    errors += "知识点 ${summary.id} 的阶段 ${lesson.stage} 与阶段 ${stage.name} 不一致"
                }
                if (summary.minutes <= 0) {
                    errors += "知识点 ${summary.id} 的学习时长必须大于 0"
                }
            }
        }

        val stageLessonIds = content.stages.flatMap { stage ->
            stage.lessons.map { it.id }
        }
        if (stageLessonIds.size != stageLessonIds.distinct().size) {
            errors += "课程阶段中存在重复知识点"
        }
        val missingLessonIds = stageLessonIds.filterNot { it in content.lessons }
        if (missingLessonIds.isNotEmpty()) {
            errors += "以下知识点缺少详情：${missingLessonIds.joinToString("、")}"
        }
        val unexpectedLessonIds = content.lessons.keys - stageLessonIds.toSet()
        if (unexpectedLessonIds.isNotEmpty()) {
            errors += "以下详情没有出现在课程阶段中：${unexpectedLessonIds.joinToString("、")}"
        }
        content.lessons.forEach { (lessonId, lesson) ->
            if (lesson.id != lessonId) {
                errors += "知识点键 $lessonId 与详情 id ${lesson.id} 不一致"
            }
            if (lesson.title.isBlank()) {
                errors += "知识点 $lessonId 缺少标题"
            }
            if (lesson.example.isBlank()) {
                errors += "知识点 $lessonId 缺少示例代码"
            }
            if (lesson.quiz.options.size < 2) {
                errors += "知识点 $lessonId 的练习选项不足"
            }
            if (lesson.quiz.answerIndex !in lesson.quiz.options.indices) {
                errors += "知识点 $lessonId 的练习答案下标越界"
            }
            lesson.next.forEach { next ->
                if (next.id !in content.lessons) {
                    errors += "知识点 $lessonId 的下一课 ${next.id} 不存在"
                }
            }
        }
        val projectIds = content.projects.map { it.id }
        if (projectIds.size != projectIds.distinct().size) {
            errors += "项目内容中存在重复 id"
        }
        content.projects.forEach { project ->
            if (project.title.isBlank() || project.goal.isBlank()) {
                errors += "项目 ${project.id} 缺少标题或目标"
            }
        }
        return errors
    }
}
