package com.pythonlearn.app.data.repository

import com.pythonlearn.app.data.local.LessonProgressEntity
import com.pythonlearn.app.data.local.ProgressDao
import com.pythonlearn.app.data.local.ProgressSnapshot
import com.pythonlearn.app.data.local.ProjectProgressEntity
import com.pythonlearn.app.data.local.QuizProgressEntity
import com.pythonlearn.app.data.local.TrainingProgressEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine

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
        }
    }

    suspend fun completeLesson(lessonId: String) {
        dao.upsertLesson(
            LessonProgressEntity(
                lessonId = lessonId,
                completed = true,
                updatedAt = now(),
            ),
        )
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
        dao.upsertTraining(
            TrainingProgressEntity(
                exerciseId = exerciseId,
                completed = correct || existing?.completed == true,
                needsReview = !correct,
                correctCount = (existing?.correctCount ?: 0) + if (correct) 1 else 0,
                wrongCount = (existing?.wrongCount ?: 0) + if (correct) 0 else 1,
                updatedAt = now(),
            ),
        )
    }

    suspend fun recordQuizResult(question: String, correct: Boolean) {
        val existing = dao.quiz(question)
        dao.upsertQuiz(
            QuizProgressEntity(
                question = question,
                resolved = correct,
                correctCount = (existing?.correctCount ?: 0) + if (correct) 1 else 0,
                wrongCount = (existing?.wrongCount ?: 0) + if (correct) 0 else 1,
                updatedAt = now(),
            ),
        )
    }
}
