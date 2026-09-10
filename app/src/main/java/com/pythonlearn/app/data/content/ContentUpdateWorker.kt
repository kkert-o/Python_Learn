package com.pythonlearn.app.data.content

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import com.pythonlearn.app.BuildConfig
import com.pythonlearn.app.PythonLearningApplication
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ContentUpdateWorker(
    appContext: Context,
    params: WorkerParameters,
) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val manifestUrl = BuildConfig.CONTENT_MANIFEST_URL
        if (manifestUrl.isBlank()) return Result.success()
        val application = applicationContext as? PythonLearningApplication
            ?: return Result.failure()
        return when (
            withContext(Dispatchers.IO) {
                application.contentUpdateManager.downloadAndInstall(manifestUrl)
            }
        ) {
            is ContentInstallResult.Installed,
            is ContentInstallResult.UpToDate -> Result.success()

            is ContentInstallResult.Failed -> {
                if (runAttemptCount < MAX_RETRY_ATTEMPTS) {
                    Result.retry()
                } else {
                    Result.failure()
                }
            }
        }
    }

    private companion object {
        const val MAX_RETRY_ATTEMPTS = 3
    }
}

object ContentUpdateScheduler {
    private const val WORK_NAME = "python-learning-content-update"

    fun schedule(context: Context) {
        val workManager = WorkManager.getInstance(context)
        if (BuildConfig.CONTENT_MANIFEST_URL.isBlank()) {
            workManager.cancelUniqueWork(WORK_NAME)
            return
        }
        val request = PeriodicWorkRequestBuilder<ContentUpdateWorker>(
            24,
            TimeUnit.HOURS,
        )
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build(),
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                30,
                TimeUnit.MINUTES,
            )
            .build()
        workManager.enqueueUniquePeriodicWork(
            WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request,
        )
    }
}
