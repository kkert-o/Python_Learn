package com.pythonlearn.app.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "learning_event")
data class LearningEventEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val eventType: String,
    val targetId: String,
    val correct: Boolean,
    val occurredAt: Long,
)

@Entity(tableName = "review_schedule")
data class ReviewScheduleEntity(
    @PrimaryKey val targetKey: String,
    val dueAt: Long,
    val reviewStage: Int,
    val lastReviewedAt: Long,
)

@Entity(tableName = "lesson_progress")
data class LessonProgressEntity(
    @PrimaryKey val lessonId: String,
    val completed: Boolean,
    val updatedAt: Long,
)

@Entity(tableName = "project_progress")
data class ProjectProgressEntity(
    @PrimaryKey val projectId: String,
    val completed: Boolean,
    val updatedAt: Long,
)

@Entity(tableName = "training_progress")
data class TrainingProgressEntity(
    @PrimaryKey val exerciseId: String,
    val completed: Boolean,
    val needsReview: Boolean,
    val correctCount: Int,
    val wrongCount: Int,
    val updatedAt: Long,
)

@Entity(tableName = "quiz_progress")
data class QuizProgressEntity(
    @PrimaryKey val question: String,
    val resolved: Boolean,
    val correctCount: Int,
    val wrongCount: Int,
    val updatedAt: Long,
)

data class ProgressSnapshot(
    val completedLessonIds: Set<String> = emptySet(),
    val completedProjectIds: Set<String> = emptySet(),
    val completedTrainingIds: Set<String> = emptySet(),
    val wrongTrainingIds: Set<String> = emptySet(),
    val wrongQuizIds: Set<String> = emptySet(),
) {
    companion object {
        fun from(
            lessons: List<LessonProgressEntity>,
            projects: List<ProjectProgressEntity>,
            training: List<TrainingProgressEntity>,
            quizzes: List<QuizProgressEntity>,
        ): ProgressSnapshot {
            return ProgressSnapshot(
                completedLessonIds = lessons.filter { it.completed }.map { it.lessonId }.toSet(),
                completedProjectIds = projects.filter { it.completed }.map { it.projectId }.toSet(),
                completedTrainingIds = training.filter { it.completed }.map { it.exerciseId }.toSet(),
                wrongTrainingIds = training.filter { it.needsReview }.map { it.exerciseId }.toSet(),
                wrongQuizIds = quizzes.filter { !it.resolved }.map { it.question }.toSet(),
            )
        }
    }
}
