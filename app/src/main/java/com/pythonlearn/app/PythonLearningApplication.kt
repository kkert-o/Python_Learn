package com.pythonlearn.app

import android.util.Log
import com.chaquo.python.android.PyApplication
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.content.ContentPayloadDto
import com.pythonlearn.app.data.content.ContentUpdateManager
import com.pythonlearn.app.data.content.HttpContentDownloader
import com.pythonlearn.app.data.content.JsonCourseContentRepository
import com.pythonlearn.app.data.local.PythonLearningDatabase
import com.pythonlearn.app.data.repository.ProgressRepository
import java.io.File

class PythonLearningApplication : PyApplication() {
    lateinit var progressRepository: ProgressRepository
        private set
    lateinit var contentUpdateManager: ContentUpdateManager
        private set
    var contentLoadError: String? = null
        private set

    override fun onCreate() {
        super.onCreate()
        val bundledContent = runCatching {
            JsonCourseContentRepository(this).load()
        }.onFailure { error ->
            contentLoadError = error.message
            Log.e(TAG, "Unable to load bundled course content, using built-in fallback", error)
        }.getOrElse { builtInContent() }
        val manager = ContentUpdateManager(
            installedFile = File(filesDir, "content/course_content.json"),
            bundledContent = { bundledContent },
            downloader = HttpContentDownloader(),
            appVersionCode = packageManager
                .getPackageInfo(packageName, 0)
                .longVersionCode
                .toInt(),
        )
        val content = manager.loadActiveContent()
        CourseCatalog.install(content)
        ProjectCatalog.install(content.projects)
        contentUpdateManager = manager
        val database = PythonLearningDatabase.getInstance(this)
        progressRepository = ProgressRepository(database.progressDao())
    }

    private fun builtInContent() = ContentPayloadDto.from(
        version = 1,
        updatedAt = "built-in",
        stages = CourseCatalog.stages,
        lessons = CourseCatalog.allLessons.associateBy { it.id },
        projects = ProjectCatalog.all,
    ).toDomain()

    private companion object {
        const val TAG = "PythonLearningApplication"
    }
}
