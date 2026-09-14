package com.pythonlearn.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(
    entities = [
        LearningEventEntity::class,
        ReviewScheduleEntity::class,
        LessonProgressEntity::class,
        ProjectProgressEntity::class,
        TrainingProgressEntity::class,
        QuizProgressEntity::class,
    ],
    version = 2,
    exportSchema = false,
)
abstract class PythonLearningDatabase : RoomDatabase() {
    abstract fun progressDao(): ProgressDao

    companion object {
        @Volatile
        private var instance: PythonLearningDatabase? = null

        fun getInstance(context: Context): PythonLearningDatabase {
            return instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    PythonLearningDatabase::class.java,
                    "python-learning.db",
                )
                    .addMigrations(MIGRATION_1_2)
                    .build()
                    .also { instance = it }
            }
        }

        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS learning_event (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        eventType TEXT NOT NULL,
                        targetId TEXT NOT NULL,
                        correct INTEGER NOT NULL,
                        occurredAt INTEGER NOT NULL
                    )
                    """.trimIndent(),
                )
                db.execSQL(
                    """
                    CREATE TABLE IF NOT EXISTS review_schedule (
                        targetKey TEXT NOT NULL,
                        dueAt INTEGER NOT NULL,
                        reviewStage INTEGER NOT NULL,
                        lastReviewedAt INTEGER NOT NULL,
                        PRIMARY KEY(targetKey)
                    )
                    """.trimIndent(),
                )
            }
        }
    }
}
