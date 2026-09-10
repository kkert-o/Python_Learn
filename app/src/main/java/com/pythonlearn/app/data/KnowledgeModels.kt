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

enum class ReviewTargetType {
    LESSON,
    TRAINING,
    QUIZ,
}

data class ReviewItem(
    val targetKey: String,
    val targetType: ReviewTargetType,
    val targetId: String,
    val title: String,
    val dueAt: Long,
    val overdueDays: Int,
    val priority: Int,
)

data class LearningRecommendation(
    val title: String,
    val reason: String,
    val lessonId: String? = null,
    val reviewTargetKey: String? = null,
)

data class LearningDashboard(
    val knowledgeTree: List<KnowledgeNode>,
    val dueReviews: List<ReviewItem>,
    val recommendation: LearningRecommendation,
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

object LearningDashboardEngine {
    private const val DAY_MILLIS = 24L * 60L * 60L * 1000L

    fun build(
        completedLessonIds: Set<String>,
        trainingProgress: List<TrainingProgressEntity>,
        quizProgress: List<QuizProgressEntity>,
        reviewSchedules: List<ReviewScheduleEntity>,
        now: Long,
    ): LearningDashboard {
        val knowledgeTree = KnowledgeTreeEngine.build(
            completedLessonIds = completedLessonIds,
            trainingProgress = trainingProgress,
            quizProgress = quizProgress,
            reviewSchedules = reviewSchedules,
            now = now,
        )
        val dueReviews = reviewSchedules
            .filter { it.dueAt <= now }
            .mapNotNull { schedule ->
                toReviewItem(
                    schedule = schedule,
                    trainingProgress = trainingProgress,
                    quizProgress = quizProgress,
                    now = now,
                )
            }
            .sortedWith(compareByDescending<ReviewItem> { it.priority }.thenBy { it.dueAt })

        val recommendation = when {
            dueReviews.isNotEmpty() -> {
                val first = dueReviews.first()
                LearningRecommendation(
                    title = "复习：${first.title}",
                    reason = if (dueReviews.size == 1) {
                        "这项内容已经到复习时间"
                    } else {
                        "今天有 ${dueReviews.size} 项内容需要复习"
                    },
                    lessonId = first.targetId.takeIf { first.targetType == ReviewTargetType.LESSON },
                    reviewTargetKey = first.targetKey,
                )
            }
            else -> {
                val nextNode = knowledgeTree.firstOrNull {
                    it.state == KnowledgeState.NOT_STARTED || it.state == KnowledgeState.LEARNING
                }
                if (nextNode != null) {
                    LearningRecommendation(
                        title = nextNode.title,
                        reason = if (nextNode.state == KnowledgeState.LEARNING) {
                            "继续学习这个知识点"
                        } else {
                            "完成前置知识后，下一项推荐学习内容"
                        },
                        lessonId = nextNode.lessonId,
                    )
                } else {
                    LearningRecommendation(
                        title = "进入项目实战",
                        reason = "当前课程已经完成，可以开始练习独立项目",
                    )
                }
            }
        }

        return LearningDashboard(
            knowledgeTree = knowledgeTree,
            dueReviews = dueReviews,
            recommendation = recommendation,
        )
    }

    private fun toReviewItem(
        schedule: ReviewScheduleEntity,
        trainingProgress: List<TrainingProgressEntity>,
        quizProgress: List<QuizProgressEntity>,
        now: Long,
    ): ReviewItem? {
        val separator = schedule.targetKey.indexOf(':')
        if (separator <= 0) return null
        val prefix = schedule.targetKey.substring(0, separator)
        val targetId = schedule.targetKey.substring(separator + 1)
        val targetType = when (prefix) {
            "lesson" -> ReviewTargetType.LESSON
            "training" -> ReviewTargetType.TRAINING
            "quiz" -> ReviewTargetType.QUIZ
            else -> return null
        }
        val title = when (targetType) {
            ReviewTargetType.LESSON -> CourseCatalog.lesson(targetId)?.title
            ReviewTargetType.TRAINING -> TrainingCatalog.byId(targetId)?.title
            ReviewTargetType.QUIZ -> targetId.take(30)
        } ?: return null
        val overdueDays = ((now - schedule.dueAt).coerceAtLeast(0L) / DAY_MILLIS).toInt()
        val wrongCount = when (targetType) {
            ReviewTargetType.LESSON -> 0
            ReviewTargetType.TRAINING -> {
                trainingProgress.firstOrNull { it.exerciseId == targetId }?.wrongCount ?: 0
            }
            ReviewTargetType.QUIZ -> {
                quizProgress.firstOrNull { it.question == targetId }?.wrongCount ?: 0
            }
        }
        val typeWeight = when (targetType) {
            ReviewTargetType.LESSON -> 1
            ReviewTargetType.TRAINING -> 2
            ReviewTargetType.QUIZ -> 3
        }
        return ReviewItem(
            targetKey = schedule.targetKey,
            targetType = targetType,
            targetId = targetId,
            title = title,
            dueAt = schedule.dueAt,
            overdueDays = overdueDays,
            priority = typeWeight + overdueDays + wrongCount.coerceAtMost(10),
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

            val rawScore = buildList {
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
                completed && rawScore >= 80 -> KnowledgeState.MASTERED
                completed -> KnowledgeState.COMPLETED
                hasStarted -> KnowledgeState.LEARNING
                else -> KnowledgeState.NOT_STARTED
            }
            val score = if (state == KnowledgeState.LOCKED || state == KnowledgeState.NOT_STARTED) {
                0
            } else {
                rawScore
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
