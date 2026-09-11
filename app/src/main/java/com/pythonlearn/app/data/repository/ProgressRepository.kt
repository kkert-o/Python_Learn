package com.pythonlearn.app.data.repository

import com.pythonlearn.app.data.KnowledgeNode
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DailyLearningStats
import com.pythonlearn.app.data.LearningDashboard
import com.pythonlearn.app.data.LearningDashboardEngine
import com.pythonlearn.app.data.ReviewScheduler
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.data.TrainingType
import com.pythonlearn.app.data.local.LearningEventEntity
import com.pythonlearn.app.data.local.LessonProgressEntity
import com.pythonlearn.app.data.local.ProgressDao
import com.pythonlearn.app.data.local.ProgressSnapshot
import com.pythonlearn.app.data.local.ProjectProgressEntity
import com.pythonlearn.app.data.local.QuizProgressEntity
import com.pythonlearn.app.data.local.TrainingProgressEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import java.time.Instant
import java.time.ZoneId

class ProgressRepository(
    private val dao: ProgressDao,
    private val now: () -> Long = System::currentTimeMillis,
) {
    fun observeProgress(): Flow<ProgressSnapshot> {
        return combine(
            dao.observeLessons(),
            dao.observeProjects(),
            dao.observeTraining(),
            dao.observeQuizzes(),
        ) { lessons, projects, training, quizzes ->
            ProgressSnapshot.from(lessons, projects, training, quizzes)
        }
    }

    fun observeKnowledgeTree(): Flow<List<KnowledgeNode>> {
        return observeLearningDashboard().map { it.knowledgeTree }
    }

    fun observeLearningDashboard(): Flow<LearningDashboard> {
        return combine(
            dao.observeLessons(),
            dao.observeTraining(),
            dao.observeQuizzes(),
            dao.observeReviewSchedules(),
        ) { lessons, training, quizzes, schedules ->
            LearningDashboardEngine.build(
                completedLessonIds = lessons.filter { it.completed }.map { it.lessonId }.toSet(),
                trainingProgress = training,
                quizProgress = quizzes,
                reviewSchedules = schedules,
                now = now(),
            )
        }
    }

    fun observeDailyLearningStats(): Flow<DailyLearningStats> {
        return dao.observeLearningEvents().map { events ->
            val zone = ZoneId.systemDefault()
            val today = Instant.ofEpochMilli(now()).atZone(zone).toLocalDate()
            val datedEvents = events.map { event ->
                event to Instant.ofEpochMilli(event.occurredAt).atZone(zone).toLocalDate()
            }
            val todayEvents = datedEvents.filter { (_, date) -> date == today }
            val activeDates = datedEvents.map { (_, date) -> date }.toSet()
            val weekStart = today.minusDays((today.dayOfWeek.value - 1).toLong())

            var streakDays = 0
            var cursor = today
            while (cursor in activeDates) {
                streakDays += 1
                cursor = cursor.minusDays(1)
            }

            DailyLearningStats(
                minutes = todayEvents
                    .filter { (event, _) -> event.eventType == "lesson_completed" }
                    .map { (event, _) -> event.targetId }
                    .distinct()
                    .sumOf { lessonId -> CourseCatalog.lesson(lessonId)?.minutes ?: 0 },
                quizAnswers = todayEvents
                    .filter { (event, _) -> event.eventType == "quiz_result" }
                    .map { (event, _) -> event.targetId }
                    .distinct()
                    .size,
                challengeCompleted = todayEvents.any { (event, _) ->
                    event.eventType == "training_result" &&
                        event.correct &&
                        TrainingCatalog.byId(event.targetId)?.type == TrainingType.PREDICT_OUTPUT
                },
                streakDays = streakDays,
                weekDays = activeDates.count { date -> !date.isBefore(weekStart) && !date.isAfter(today) },
            )
        }
    }

    suspend fun migrateLegacyProgress(
        completedLessonIds: Set<String>,
        completedProjectIds: Set<String>,
        completedTrainingIds: Set<String>,
        wrongTrainingIds: Set<String>,
        wrongQuizIds: Set<String>,
    ) {
        val timestamp = now()
        completedLessonIds.forEach { lessonId ->
            dao.upsertLesson(
                LessonProgressEntity(
                    lessonId = lessonId,
                    completed = true,
                    updatedAt = timestamp,
                ),
            )
        }
        completedProjectIds.forEach { projectId ->
            dao.upsertProject(
                ProjectProgressEntity(
                    projectId = projectId,
                    completed = true,
                    updatedAt = timestamp,
                ),
            )
        }
        val allTrainingIds = completedTrainingIds + wrongTrainingIds
        allTrainingIds.forEach { exerciseId ->
            val existing = dao.training(exerciseId)
            dao.upsertTraining(
                TrainingProgressEntity(
                    exerciseId = exerciseId,
                    completed = exerciseId in completedTrainingIds,
                    needsReview = exerciseId in wrongTrainingIds,
                    correctCount = existing?.correctCount ?: 0,
                    wrongCount = maxOf(existing?.wrongCount ?: 0, if (exerciseId in wrongTrainingIds) 1 else 0),
                    updatedAt = timestamp,
                ),
            )
        }
        wrongQuizIds.forEach { question ->
            val existing = dao.quiz(question)
            dao.upsertQuiz(
                QuizProgressEntity(
                    question = question,
                    resolved = false,
                    correctCount = existing?.correctCount ?: 0,
                    wrongCount = maxOf(existing?.wrongCount ?: 0, 1),
                    updatedAt = timestamp,
                ),
            )
            scheduleReview(ReviewScheduler.quizKey(question), correct = false, at = timestamp)
        }
        wrongTrainingIds.forEach { exerciseId ->
            scheduleReview(ReviewScheduler.trainingKey(exerciseId), correct = false, at = timestamp)
        }
    }

    suspend fun completeLesson(lessonId: String) {
        val timestamp = now()
        dao.upsertLesson(
            LessonProgressEntity(
                lessonId = lessonId,
                completed = true,
                updatedAt = timestamp,
            ),
        )
        dao.insertLearningEvent(
            LearningEventEntity(
                eventType = "lesson_completed",
                targetId = lessonId,
                correct = true,
                occurredAt = timestamp,
            ),
        )
        scheduleReview(ReviewScheduler.lessonKey(lessonId), correct = true, at = timestamp)
    }

    suspend fun completeProject(projectId: String) {
        dao.upsertProject(
            ProjectProgressEntity(
                projectId = projectId,
                completed = true,
                updatedAt = now(),
            ),
        )
    }

    suspend fun recordTrainingResult(exerciseId: String, correct: Boolean) {
        val existing = dao.training(exerciseId)
        val timestamp = now()
        dao.upsertTraining(
            TrainingProgressEntity(
                exerciseId = exerciseId,
                completed = correct || existing?.completed == true,
                needsReview = !correct,
                correctCount = (existing?.correctCount ?: 0) + if (correct) 1 else 0,
                wrongCount = (existing?.wrongCount ?: 0) + if (correct) 0 else 1,
                updatedAt = timestamp,
            ),
        )
        dao.insertLearningEvent(
            LearningEventEntity(
                eventType = "training_result",
                targetId = exerciseId,
                correct = correct,
                occurredAt = timestamp,
            ),
        )
        scheduleReview(ReviewScheduler.trainingKey(exerciseId), correct, timestamp)
    }

    suspend fun recordQuizResult(question: String, correct: Boolean) {
        val existing = dao.quiz(question)
        val timestamp = now()
        dao.upsertQuiz(
            QuizProgressEntity(
                question = question,
                resolved = correct,
                correctCount = (existing?.correctCount ?: 0) + if (correct) 1 else 0,
                wrongCount = (existing?.wrongCount ?: 0) + if (correct) 0 else 1,
                updatedAt = timestamp,
            ),
        )
        dao.insertLearningEvent(
            LearningEventEntity(
                eventType = "quiz_result",
                targetId = question,
                correct = correct,
                occurredAt = timestamp,
            ),
        )
        scheduleReview(ReviewScheduler.quizKey(question), correct, timestamp)
    }

    private suspend fun scheduleReview(
        targetKey: String,
        correct: Boolean,
        at: Long,
    ) {
        val existing = dao.reviewSchedule(targetKey)
        dao.upsertReviewSchedule(
            ReviewScheduler.next(
                targetKey = targetKey,
                existing = existing,
                correct = correct,
                now = at,
            ),
        )
    }
}
