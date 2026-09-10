package com.pythonlearn.app

import com.chaquo.python.android.PyApplication
import com.pythonlearn.app.data.local.PythonLearningDatabase
import com.pythonlearn.app.data.repository.ProgressRepository

class PythonLearningApplication : PyApplication() {
    lateinit var progressRepository: ProgressRepository
        private set

    override fun onCreate() {
        super.onCreate()
        val database = PythonLearningDatabase.getInstance(this)
        progressRepository = ProgressRepository(database.progressDao())
    }
}
