package com.pythonlearn.app.data

import com.pythonlearn.app.data.local.QuizProgressEntity
import com.pythonlearn.app.data.local.ReviewScheduleEntity
import com.pythonlearn.app.data.local.TrainingProgressEntity

enum class KnowledgeState {
    NOT_STARTED,
    LEARNING,
    COMPLETED,
    MASTERED,
    NEEDS_REVIEW,
    LOCKED,
}

data class KnowledgeNode(
    val lessonId: String,
    val title: String,
    val stage: String,
    val state: KnowledgeState,
    val masteryScore: Int,
    val nextReviewAt: Long?,
)

object ReviewScheduler {
    val intervalsInDays: LongArray = longArrayOf(1, 3, 7, 14, 30)
    private const val DAY_MILLIS = 24L * 60L * 60L * 1000L

    fun lessonKey(lessonId: String): String = "lesson:$lessonId"

    fun trainingKey(exerciseId: String): String = "training:$exerciseId"

    fun quizKey(question: String): String = "quiz:$question"

    fun next(
        targetKey: String,
        existing: ReviewScheduleEntity?,
        correct: Boolean,
        now: Long,
    ): ReviewScheduleEntity {
        val nextStage = if (correct) {
            ((existing?.reviewStage ?: -1) + 1).coerceAtMost(intervalsInDays.lastIndex)
        } else {
            0
        }
        return ReviewScheduleEntity(
            targetKey = targetKey,
            dueAt = now + intervalsInDays[nextStage] * DAY_MILLIS,
            reviewStage = nextStage,
            lastReviewedAt = now,
        )
    }
}

object KnowledgeTreeEngine {
    fun build(
        completedLessonIds: Set<String>,
        trainingProgress: List<TrainingProgressEntity>,
        quizProgress: List<QuizProgressEntity>,
        reviewSchedules: List<ReviewScheduleEntity>,
        now: Long,
    ): List<KnowledgeNode> {
        val trainingByLesson = trainingProgress
            .groupBy { it.exerciseId }
            .mapNotNull { (exerciseId, rows) ->
                val lessonId = TrainingCatalog.byId(exerciseId)?.lessonId ?: return@mapNotNull null
                lessonId to rows
            }
            .toMap()
        val quizByLesson = quizProgress
            .groupBy { CourseCatalog.lessonIdByQuizQuestion(it.question) }
            .filterKeys { it != null }
            .mapKeys { it.key!! }
        val scheduleByKey = reviewSchedules.associateBy { it.targetKey }

        val orderedIds = CourseCatalog.orderedLessonIds
        return orderedIds.mapIndexed { index, lessonId ->
            val lesson = CourseCatalog.lesson(lessonId)
                ?: error("Lesson $lessonId is missing from CourseCatalog")
            val training = trainingByLesson[lessonId].orEmpty()
            val quizzes = quizByLesson[lessonId].orEmpty()
            val completed = lessonId in completedLessonIds
            val allTrainingCompleted = training.isNotEmpty() && training.all { it.completed }
            val trainingRatio = if (training.isEmpty()) {
                0f
            } else {
                training.count { it.completed }.toFloat() / training.size
            }
            val hasResolvedQuiz = quizzes.any { it.resolved || it.correctCount > 0 }
            val hasWrongTraining = training.any { it.needsReview }
            val hasWrongQuiz = quizzes.any { !it.resolved && it.wrongCount > 0 }
            val reviewKeys = buildList {
                add(ReviewScheduler.lessonKey(lessonId))
                training.forEach { add(ReviewScheduler.trainingKey(it.exerciseId)) }
                quizzes.forEach { add(ReviewScheduler.quizKey(it.question)) }
            }
            val dueSchedule = reviewKeys
                .mapNotNull(scheduleByKey::get)
                .filter { it.dueAt <= now }
                .minByOrNull { it.dueAt }
            val needsReview = hasWrongTraining || hasWrongQuiz || dueSchedule != null

            val score = buildList {
                if (completed) add(40)
                if (training.isEmpty()) {
                    add(15)
                } else {
                    add((trainingRatio * 30).toInt())
                }
                if (hasResolvedQuiz) add(30) else if (quizzes.any { it.wrongCount > 0 }) add(10)
                if (allTrainingCompleted) add(5)
            }.sum().coerceIn(0, 100)

            val hasStarted = training.isNotEmpty() || quizzes.isNotEmpty()
            val previousCompleted = index == 0 || orderedIds[index - 1] in completedLessonIds
            val state = when {
                !previousCompleted && !completed && !hasStarted -> KnowledgeState.LOCKED
                needsReview -> KnowledgeState.NEEDS_REVIEW
                completed && score >= 80 -> KnowledgeState.MASTERED
                completed -> KnowledgeState.COMPLETED
                hasStarted -> KnowledgeState.LEARNING
                else -> KnowledgeState.NOT_STARTED
            }
            val nextReviewAt = reviewKeys
                .mapNotNull(scheduleByKey::get)
                .minOfOrNull { it.dueAt }

            KnowledgeNode(
                lessonId = lessonId,
                title = lesson.title,
                stage = lesson.stage,
                state = state,
                masteryScore = score,
                nextReviewAt = nextReviewAt,
            )
        }
    }
}
