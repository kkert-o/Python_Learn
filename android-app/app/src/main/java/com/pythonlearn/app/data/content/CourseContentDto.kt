package com.pythonlearn.app.data.content

import com.pythonlearn.app.data.CourseStage
import com.pythonlearn.app.data.ErrorExample
import com.pythonlearn.app.data.LessonDetail
import com.pythonlearn.app.data.LessonState
import com.pythonlearn.app.data.LessonSummary
import com.pythonlearn.app.data.ProjectInfo
import com.pythonlearn.app.data.Quiz

data class CourseContent(
    val version: Int,
    val updatedAt: String,
    val stages: List<CourseStage>,
    val lessons: Map<String, LessonDetail>,
    val projects: List<ProjectInfo>,
)

data class ContentPayloadDto(
    val version: Int,
    val updatedAt: String,
    val stages: List<StageDto>,
    val lessons: Map<String, LessonDto>,
    val projects: List<ProjectDto>,
) {
    fun toDomain(): CourseContent {
        return CourseContent(
            version = version,
            updatedAt = updatedAt,
            stages = stages.map { it.toDomain() },
            lessons = lessons.mapValues { it.value.toDomain() },
            projects = projects.map { it.toDomain() },
        )
    }

    companion object {
        fun from(
            version: Int,
            updatedAt: String,
            stages: List<CourseStage>,
            lessons: Map<String, LessonDetail>,
            projects: List<ProjectInfo>,
        ): ContentPayloadDto {
            return ContentPayloadDto(
                version = version,
                updatedAt = updatedAt,
                stages = stages.map(StageDto::from),
                lessons = lessons.mapValues { LessonDto.from(it.value) },
                projects = projects.map(ProjectDto::from),
            )
        }
    }
}

data class StageDto(
    val label: String,
    val name: String,
    val progress: Int,
    val special: Boolean,
    val lessons: List<LessonSummaryDto>,
) {
    fun toDomain(): CourseStage {
        return CourseStage(
            label = label,
            name = name,
            progress = progress,
            lessons = lessons.map { it.toDomain() },
            special = special,
        )
    }

    companion object {
        fun from(stage: CourseStage): StageDto {
            return StageDto(
                label = stage.label,
                name = stage.name,
                progress = stage.progress,
                special = stage.special,
                lessons = stage.lessons.map(LessonSummaryDto::from),
            )
        }
    }
}

data class LessonSummaryDto(
    val id: String,
    val title: String,
    val minutes: Int,
    val state: String,
) {
    fun toDomain(): LessonSummary {
        return LessonSummary(
            id = id,
            title = title,
            minutes = minutes,
            state = runCatching { LessonState.valueOf(state) }.getOrDefault(LessonState.TODO),
        )
    }

    companion object {
        fun from(summary: LessonSummary): LessonSummaryDto {
            return LessonSummaryDto(
                id = summary.id,
                title = summary.title,
                minutes = summary.minutes,
                state = summary.state.name,
            )
        }
    }
}

data class LessonDto(
    val id: String,
    val title: String,
    val stage: String,
    val level: String,
    val minutes: Int,
    val knowledge: List<String>,
    val why: List<String>,
    val purpose: String,
    val example: String,
    val exampleNotes: List<NoteDto>,
    val quiz: QuizDto,
    val errors: List<ErrorDto>,
    val projectCode: String,
    val legalRisk: String,
    val legalNote: String,
    val legalBasis: String,
    val legalUpdated: String,
    val next: List<LessonSummaryDto>,
) {
    fun toDomain(): LessonDetail {
        return LessonDetail(
            id = id,
            title = title,
            stage = stage,
            level = level,
            minutes = minutes,
            knowledge = knowledge,
            why = why,
            purpose = purpose,
            example = example,
            exampleNotes = exampleNotes.map { it.left to it.right },
            quiz = quiz.toDomain(),
            errors = errors.map { it.toDomain() },
            projectCode = projectCode,
            legalRisk = legalRisk,
            legalNote = legalNote,
            legalBasis = legalBasis,
            legalUpdated = legalUpdated,
            next = next.map { it.toDomain() },
        )
    }

    companion object {
        fun from(lesson: LessonDetail): LessonDto {
            return LessonDto(
                id = lesson.id,
                title = lesson.title,
                stage = lesson.stage,
                level = lesson.level,
                minutes = lesson.minutes,
                knowledge = lesson.knowledge,
                why = lesson.why,
                purpose = lesson.purpose,
                example = lesson.example,
                exampleNotes = lesson.exampleNotes.map { NoteDto(it.first, it.second) },
                quiz = QuizDto.from(lesson.quiz),
                errors = lesson.errors.map(ErrorDto::from),
                projectCode = lesson.projectCode,
                legalRisk = lesson.legalRisk,
                legalNote = lesson.legalNote,
                legalBasis = lesson.legalBasis,
                legalUpdated = lesson.legalUpdated,
                next = lesson.next.map(LessonSummaryDto::from),
            )
        }
    }
}

data class NoteDto(
    val left: String,
    val right: String,
)

data class QuizDto(
    val question: String,
    val code: String,
    val options: List<String>,
    val answerIndex: Int,
    val explanation: String,
) {
    fun toDomain(): Quiz {
        return Quiz(
            question = question,
            code = code,
            options = options,
            answerIndex = answerIndex,
            explanation = explanation,
        )
    }

    companion object {
        fun from(quiz: Quiz): QuizDto {
            return QuizDto(
                question = quiz.question,
                code = quiz.code,
                options = quiz.options,
                answerIndex = quiz.answerIndex,
                explanation = quiz.explanation,
            )
        }
    }
}

data class ErrorDto(
    val title: String,
    val detail: String,
    val code: String,
) {
    fun toDomain(): ErrorExample {
        return ErrorExample(
            title = title,
            detail = detail,
            code = code,
        )
    }

    companion object {
        fun from(error: ErrorExample): ErrorDto {
            return ErrorDto(
                title = error.title,
                detail = error.detail,
                code = error.code,
            )
        }
    }
}

data class ProjectDto(
    val id: String,
    val title: String,
    val level: String,
    val goal: String,
    val requirements: List<String>,
    val knowledge: List<String>,
    val hints: List<String>,
    val starter: String,
) {
    fun toDomain(): ProjectInfo {
        return ProjectInfo(
            id = id,
            title = title,
            level = level,
            goal = goal,
            requirements = requirements,
            knowledge = knowledge,
            hints = hints,
            starter = starter,
        )
    }

    companion object {
        fun from(project: ProjectInfo): ProjectDto {
            return ProjectDto(
                id = project.id,
                title = project.title,
                level = project.level,
                goal = project.goal,
                requirements = project.requirements,
                knowledge = project.knowledge,
                hints = project.hints,
                starter = project.starter,
            )
        }
    }
}
