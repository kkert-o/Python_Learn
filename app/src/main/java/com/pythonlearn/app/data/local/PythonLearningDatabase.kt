package com.pythonlearn.app.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        LessonProgressEntity::class,
        ProjectProgressEntity::class,
        TrainingProgressEntity::class,
        QuizProgressEntity::class,
    ],
    version = 1,
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
                ).build().also { instance = it }
            }
        }
    }
}
