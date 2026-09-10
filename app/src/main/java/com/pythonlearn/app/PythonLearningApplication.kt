package com.pythonlearn.app

import android.util.Log
import com.chaquo.python.android.PyApplication
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.content.JsonCourseContentRepository
import com.pythonlearn.app.data.local.PythonLearningDatabase
import com.pythonlearn.app.data.repository.ProgressRepository

class PythonLearningApplication : PyApplication() {
    lateinit var progressRepository: ProgressRepository
        private set
    var contentLoadError: String? = null
        private set

    override fun onCreate() {
        super.onCreate()
        runCatching {
            val content = JsonCourseContentRepository(this).load()
            CourseCatalog.install(content)
            ProjectCatalog.install(content.projects)
        }.onFailure { error ->
            contentLoadError = error.message
            Log.e(TAG, "Unable to load bundled course content, using built-in fallback", error)
        }
        val database = PythonLearningDatabase.getInstance(this)
        progressRepository = ProgressRepository(database.progressDao())
    }

    private companion object {
        const val TAG = "PythonLearningApplication"
    }
}
