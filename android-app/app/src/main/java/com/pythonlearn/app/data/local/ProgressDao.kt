package com.pythonlearn.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface ProgressDao {
    @Query("SELECT * FROM lesson_progress")
    fun observeLessons(): Flow<List<LessonProgressEntity>>

    @Query("SELECT * FROM project_progress")
    fun observeProjects(): Flow<List<ProjectProgressEntity>>

    @Query("SELECT * FROM training_progress")
    fun observeTraining(): Flow<List<TrainingProgressEntity>>

    @Query("SELECT * FROM quiz_progress")
    fun observeQuizzes(): Flow<List<QuizProgressEntity>>

    @Query("SELECT * FROM review_schedule")
    fun observeReviewSchedules(): Flow<List<ReviewScheduleEntity>>

    @Query("SELECT * FROM learning_event ORDER BY occurredAt DESC")
    fun observeLearningEvents(): Flow<List<LearningEventEntity>>

    @Query("SELECT * FROM lesson_progress WHERE lessonId = :lessonId LIMIT 1")
    suspend fun lesson(lessonId: String): LessonProgressEntity?

    @Query("SELECT * FROM project_progress WHERE projectId = :projectId LIMIT 1")
    suspend fun project(projectId: String): ProjectProgressEntity?

    @Query("SELECT * FROM training_progress WHERE exerciseId = :exerciseId LIMIT 1")
    suspend fun training(exerciseId: String): TrainingProgressEntity?

    @Query("SELECT * FROM quiz_progress WHERE question = :question LIMIT 1")
    suspend fun quiz(question: String): QuizProgressEntity?

    @Query("SELECT * FROM review_schedule WHERE targetKey = :targetKey LIMIT 1")
    suspend fun reviewSchedule(targetKey: String): ReviewScheduleEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertReviewSchedule(progress: ReviewScheduleEntity)

    @Insert
    suspend fun insertLearningEvent(event: LearningEventEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertLesson(progress: LessonProgressEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertProject(progress: ProjectProgressEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertTraining(progress: TrainingProgressEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertQuiz(progress: QuizProgressEntity)
}
