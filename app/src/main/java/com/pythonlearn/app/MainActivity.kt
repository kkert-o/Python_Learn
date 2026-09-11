package com.pythonlearn.app

import android.os.Bundle
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.lifecycle.lifecycleScope
import com.pythonlearn.app.data.DailyLearningStats
import com.pythonlearn.app.data.LearningDashboard
import com.pythonlearn.app.data.LearningDashboardEngine
import com.pythonlearn.app.ui.PythonLearningApp
import com.pythonlearn.app.runtime.AiConfig
import com.pythonlearn.app.ui.theme.AccentOption
import com.pythonlearn.app.ui.theme.PythonLearningTheme
import com.pythonlearn.app.ui.theme.ThemePreference
import com.pythonlearn.app.ui.theme.WallpaperOption
import com.pythonlearn.app.ui.theme.accentOptions
import com.pythonlearn.app.ui.theme.legalRegionOptions
import com.pythonlearn.app.ui.theme.customWallpaperOption
import com.pythonlearn.app.ui.theme.wallpaperOptions
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val prefs = getSharedPreferences("python_app_settings", MODE_PRIVATE)
        val progressRepository = (application as PythonLearningApplication).progressRepository

        setContent {
            var themePreference by remember {
                mutableStateOf(
                    ThemePreference.entries.firstOrNull {
                        it.name == prefs.getString(KEY_THEME, null)
                    } ?: ThemePreference.SYSTEM,
                )
            }
            var accent by remember {
                mutableStateOf(accentOptions.first { it.value == prefs.getLong(KEY_ACCENT, accentOptions.first().value) })
            }
            var wallpaper by remember {
                mutableStateOf(
                    (wallpaperOptions + customWallpaperOption).firstOrNull {
                        it.id == prefs.getString(KEY_WALLPAPER, null)
                    } ?: wallpaperOptions.first(),
                )
            }
            var completedLessonIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_COMPLETED_LESSONS, emptySet())?.toSet() ?: emptySet())
            }
            var completedProjectIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_COMPLETED_PROJECTS, emptySet())?.toSet() ?: emptySet())
            }
            var wrongQuizIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_WRONG_QUIZ, emptySet())?.toSet() ?: emptySet())
            }
            var completedTrainingIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_COMPLETED_TRAINING, emptySet())?.toSet() ?: emptySet())
            }
            var wrongTrainingIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_WRONG_TRAINING, emptySet())?.toSet() ?: emptySet())
            }
            var legalRegion by remember {
                mutableStateOf(
                    legalRegionOptions.firstOrNull {
                        it.id == prefs.getString(KEY_LEGAL_REGION, null)
                    } ?: legalRegionOptions.first(),
                )
            }
            var learningDashboard by remember {
                mutableStateOf(
                    LearningDashboardEngine.build(
                        completedLessonIds = completedLessonIds,
                        trainingProgress = emptyList(),
                        quizProgress = emptyList(),
                        reviewSchedules = emptyList(),
                        now = System.currentTimeMillis(),
                    ),
                )
            }
            var dailyLearningStats by remember { mutableStateOf(DailyLearningStats()) }
            var favoriteIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_FAVORITES, emptySet())?.toSet() ?: emptySet())
            }
            var aiFreeChallengeIds by remember {
                mutableStateOf(prefs.getStringSet(KEY_AI_FREE_CHALLENGES, emptySet())?.toSet() ?: emptySet())
            }
            var aiPromptCount by remember { mutableStateOf(prefs.getInt(KEY_AI_PROMPT_COUNT, 0)) }
            var customWallpaperUri by remember {
                mutableStateOf(
                    prefs.getString(KEY_CUSTOM_WALLPAPER, null)?.let(Uri::parse),
                )
            }
            var aiConfig by remember {
                mutableStateOf(
                    AiConfig(
                        endpoint = prefs.getString(KEY_AI_ENDPOINT, AiConfig.DEFAULT_ENDPOINT) ?: AiConfig.DEFAULT_ENDPOINT,
                        apiKey = prefs.getString(KEY_AI_API_KEY, "") ?: "",
                        model = prefs.getString(KEY_AI_MODEL, AiConfig.DEFAULT_MODEL) ?: AiConfig.DEFAULT_MODEL,
                    ),
                )
            }

            LaunchedEffect(Unit) {
                progressRepository.migrateLegacyProgress(
                    completedLessonIds = completedLessonIds,
                    completedProjectIds = completedProjectIds,
                    completedTrainingIds = completedTrainingIds,
                    wrongTrainingIds = wrongTrainingIds,
                    wrongQuizIds = wrongQuizIds,
                )
                progressRepository.observeProgress().collect { snapshot ->
                    completedLessonIds = snapshot.completedLessonIds
                    completedProjectIds = snapshot.completedProjectIds
                    completedTrainingIds = snapshot.completedTrainingIds
                    wrongTrainingIds = snapshot.wrongTrainingIds
                    wrongQuizIds = snapshot.wrongQuizIds
                }
            }

            LaunchedEffect(Unit) {
                progressRepository.observeLearningDashboard().collect { dashboard ->
                    learningDashboard = dashboard
                }
            }

            LaunchedEffect(Unit) {
                progressRepository.observeDailyLearningStats().collect { stats ->
                    dailyLearningStats = stats
                }
            }

            LaunchedEffect(
                themePreference,
                accent,
                wallpaper,
                completedLessonIds,
                completedProjectIds,
                wrongQuizIds,
                completedTrainingIds,
                wrongTrainingIds,
                legalRegion,
                favoriteIds,
                aiFreeChallengeIds,
                aiPromptCount,
                customWallpaperUri,
                aiConfig,
            ) {
                prefs.edit()
                    .putString(KEY_THEME, themePreference.name)
                    .putLong(KEY_ACCENT, accent.value)
                    .putString(KEY_WALLPAPER, wallpaper.id)
                    .putStringSet(KEY_COMPLETED_LESSONS, completedLessonIds)
                    .putStringSet(KEY_COMPLETED_PROJECTS, completedProjectIds)
                    .putStringSet(KEY_WRONG_QUIZ, wrongQuizIds)
                    .putStringSet(KEY_COMPLETED_TRAINING, completedTrainingIds)
                    .putStringSet(KEY_WRONG_TRAINING, wrongTrainingIds)
                    .putString(KEY_LEGAL_REGION, legalRegion.id)
                    .putStringSet(KEY_FAVORITES, favoriteIds)
                    .putStringSet(KEY_AI_FREE_CHALLENGES, aiFreeChallengeIds)
                    .putInt(KEY_AI_PROMPT_COUNT, aiPromptCount)
                    .putString(KEY_CUSTOM_WALLPAPER, customWallpaperUri?.toString())
                    .putString(KEY_AI_ENDPOINT, aiConfig.endpoint)
                    .putString(KEY_AI_API_KEY, aiConfig.apiKey)
                    .putString(KEY_AI_MODEL, aiConfig.model)
                    .apply()
            }

            PythonLearningTheme(
                preference = themePreference,
                accent = accent,
            ) {
                PythonLearningApp(
                    themePreference = themePreference,
                    onThemePreferenceChange = { themePreference = it },
                    accent = accent,
                    onAccentChange = { accent = it },
                    wallpaper = wallpaper,
                    onWallpaperChange = { wallpaper = it },
                    completedLessonIds = completedLessonIds,
                    onCompleteLesson = { lessonId ->
                        completedLessonIds = completedLessonIds + lessonId
                        lifecycleScope.launch {
                            progressRepository.completeLesson(lessonId)
                        }
                    },
                    completedProjectIds = completedProjectIds,
                    onCompleteProject = { projectId ->
                        completedProjectIds = completedProjectIds + projectId
                        lifecycleScope.launch {
                            progressRepository.completeProject(projectId)
                        }
                    },
                    wrongQuizIds = wrongQuizIds,
                    onRecordWrong = { question ->
                        wrongQuizIds = wrongQuizIds + question
                        lifecycleScope.launch {
                            progressRepository.recordQuizResult(question, correct = false)
                        }
                    },
                    onResolveWrong = { question ->
                        wrongQuizIds = wrongQuizIds - question
                        lifecycleScope.launch {
                            progressRepository.recordQuizResult(question, correct = true)
                        }
                    },
                    completedTrainingIds = completedTrainingIds,
                    wrongTrainingIds = wrongTrainingIds,
                    onTrainingResult = { exerciseId, correct ->
                        if (correct) {
                            completedTrainingIds = completedTrainingIds + exerciseId
                            wrongTrainingIds = wrongTrainingIds - exerciseId
                        } else {
                            wrongTrainingIds = wrongTrainingIds + exerciseId
                        }
                        lifecycleScope.launch {
                            progressRepository.recordTrainingResult(exerciseId, correct)
                        }
                    },
                    legalRegion = legalRegion,
                    onLegalRegionChange = { legalRegion = it },
                    learningDashboard = learningDashboard,
                    dailyLearningStats = dailyLearningStats,
                    favoriteIds = favoriteIds,
                    onToggleFavorite = { key ->
                        favoriteIds = if (key in favoriteIds) favoriteIds - key else favoriteIds + key
                    },
                    aiFreeChallengeIds = aiFreeChallengeIds,
                    onToggleAiFreeChallenge = { id ->
                        aiFreeChallengeIds = if (id in aiFreeChallengeIds) {
                            aiFreeChallengeIds - id
                        } else {
                            aiFreeChallengeIds + id
                        }
                    },
                    aiPromptCount = aiPromptCount,
                    onAiPrompt = { aiPromptCount += 1 },
                    customWallpaperUri = customWallpaperUri,
                    onImportWallpaper = { uri ->
                        customWallpaperUri = uri
                    },
                    aiConfig = aiConfig,
                    onAiConfigChange = { aiConfig = it },
                )
            }
        }
    }

    private companion object {
        const val KEY_THEME = "theme_preference"
        const val KEY_ACCENT = "accent_value"
        const val KEY_WALLPAPER = "wallpaper_id"
        const val KEY_COMPLETED_LESSONS = "completed_lessons"
        const val KEY_COMPLETED_PROJECTS = "completed_projects"
        const val KEY_WRONG_QUIZ = "wrong_quiz_ids"
        const val KEY_COMPLETED_TRAINING = "completed_training_ids"
        const val KEY_WRONG_TRAINING = "wrong_training_ids"
        const val KEY_LEGAL_REGION = "legal_region"
        const val KEY_FAVORITES = "favorites"
        const val KEY_AI_FREE_CHALLENGES = "ai_free_challenges"
        const val KEY_AI_PROMPT_COUNT = "ai_prompt_count"
        const val KEY_CUSTOM_WALLPAPER = "custom_wallpaper_uri"
        const val KEY_AI_ENDPOINT = "ai_endpoint"
        const val KEY_AI_API_KEY = "ai_api_key"
        const val KEY_AI_MODEL = "ai_model"
    }
}
