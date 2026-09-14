package com.pythonlearn.app.ui

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.EditNote
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.School
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.Alignment
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.draw.blur
import coil.compose.AsyncImage
import com.pythonlearn.app.data.AiIndependenceEngine
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DailyLearningStats
import com.pythonlearn.app.data.LearningDashboard
import com.pythonlearn.app.data.ReviewTargetType
import com.pythonlearn.app.ui.screens.AppearanceScreen
import com.pythonlearn.app.ui.screens.AiIndependenceScreen
import com.pythonlearn.app.ui.screens.AiTeacherScreen
import com.pythonlearn.app.ui.screens.CourseScreen
import com.pythonlearn.app.ui.screens.CodeWorkbenchScreen
import com.pythonlearn.app.ui.screens.ErrorMuseumScreen
import com.pythonlearn.app.ui.screens.HomeScreen
import com.pythonlearn.app.ui.screens.LearningHubScreen
import com.pythonlearn.app.ui.screens.LessonScreen
import com.pythonlearn.app.ui.screens.PracticeScreen
import com.pythonlearn.app.ui.screens.ProfileScreen
import com.pythonlearn.app.ui.screens.ProjectScreen
import com.pythonlearn.app.ui.screens.SearchLibraryScreen
import com.pythonlearn.app.ui.screens.WallpaperScreen
import com.pythonlearn.app.ui.screens.toWorkbenchCode
import com.pythonlearn.app.runtime.AiConfig
import com.pythonlearn.app.ui.theme.AccentOption
import com.pythonlearn.app.ui.theme.ThemePreference
import com.pythonlearn.app.ui.theme.WallpaperOption
import com.pythonlearn.app.ui.theme.LegalRegion
import com.pythonlearn.app.ui.theme.customWallpaperOption

private enum class Destination(val label: String) {
    HOME("首页"),
    COURSES("课程"),
    PRACTICE("练习"),
    PROJECTS("项目"),
    PROFILE("我的"),
}

private enum class ProfilePanel {
    MAIN,
    APPEARANCE,
    WALLPAPER,
    LEARNING,
    SEARCH,
    ERRORS,
    AI_INDEPENDENCE,
}

private sealed interface AppOverlay {
    data class Lesson(val lessonId: String) : AppOverlay

    data class Workbench(val initialCode: String?) : AppOverlay

    data class Profile(val panel: ProfilePanel) : AppOverlay

    data object AiTeacher : AppOverlay
}

@Composable
fun PythonLearningApp(
    themePreference: ThemePreference,
    onThemePreferenceChange: (ThemePreference) -> Unit,
    accent: AccentOption,
    onAccentChange: (AccentOption) -> Unit,
    wallpaper: WallpaperOption,
    onWallpaperChange: (WallpaperOption) -> Unit,
    completedLessonIds: Set<String>,
    onCompleteLesson: (String) -> Unit,
    completedProjectIds: Set<String>,
    onCompleteProject: (String) -> Unit,
    wrongQuizIds: Set<String>,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
    completedTrainingIds: Set<String>,
    wrongTrainingIds: Set<String>,
    onTrainingResult: (exerciseId: String, correct: Boolean) -> Unit,
    legalRegion: LegalRegion,
    onLegalRegionChange: (LegalRegion) -> Unit,
    learningDashboard: LearningDashboard,
    dailyLearningStats: DailyLearningStats,
    favoriteIds: Set<String>,
    onToggleFavorite: (String) -> Unit,
    aiFreeChallengeIds: Set<String>,
    onToggleAiFreeChallenge: (String) -> Unit,
    aiPromptCount: Int,
    onAiPrompt: () -> Unit,
    customWallpaperUri: Uri?,
    onImportWallpaper: (Uri) -> Unit,
    aiConfig: AiConfig,
    onAiConfigChange: (AiConfig) -> Unit,
) {
    val context = LocalContext.current
    val wallpaperPicker = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent(),
    ) { uri ->
        if (uri != null) {
            try {
                context.contentResolver.takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION,
                )
            } catch (_: SecurityException) {
                // Some providers do not support persistable permission.
            }
            onImportWallpaper(uri)
            onWallpaperChange(customWallpaperOption)
        }
    }
    var destination by remember { mutableStateOf(Destination.HOME) }
    var overlays by remember { mutableStateOf<List<AppOverlay>>(emptyList()) }

    val dark = when (themePreference) {
        ThemePreference.SYSTEM -> isSystemInDarkTheme()
        ThemePreference.LIGHT -> false
        ThemePreference.DARK -> true
    }
    val wallpaperColors = if (dark) wallpaper.darkColors else wallpaper.lightColors
    val backgroundBrush = remember(wallpaperColors) {
        Brush.verticalGradient(wallpaperColors)
    }

    val openLesson: (String) -> Unit = { lessonId ->
        if (CourseCatalog.lesson(lessonId) != null) {
            overlays = overlays + AppOverlay.Lesson(lessonId)
        }
    }
    val openWorkbench: (String?) -> Unit = { code ->
        overlays = overlays + AppOverlay.Workbench(code)
    }
    val pushAi: () -> Unit = {
        overlays = overlays + AppOverlay.AiTeacher
    }
    val popOverlay: () -> Unit = {
        if (overlays.isNotEmpty()) {
            overlays = overlays.dropLast(1)
        }
    }
    BackHandler(
        enabled = overlays.isNotEmpty(),
    ) {
        popOverlay()
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (wallpaper.isCustom && customWallpaperUri != null) {
            AsyncImage(
                model = customWallpaperUri,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxSize()
                    .blur(16.dp),
                contentScale = ContentScale.Crop,
                alpha = 0.92f,
            )
            if (dark) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black.copy(alpha = 0.28f)),
                )
            }
        } else {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(backgroundBrush),
            )
        }

        when (val overlay = overlays.lastOrNull()) {
            null -> MainShell(
                destination = destination,
                onDestinationChange = { destination = it },
                onOpenLesson = openLesson,
                onOpenAi = pushAi,
                completedLessonIds = completedLessonIds,
                completedProjectIds = completedProjectIds,
                onCompleteProject = onCompleteProject,
                wrongQuizIds = wrongQuizIds,
                onRecordWrong = onRecordWrong,
                onResolveWrong = onResolveWrong,
                completedTrainingIds = completedTrainingIds,
                wrongTrainingIds = wrongTrainingIds,
                onTrainingResult = onTrainingResult,
                legalRegion = legalRegion,
                onLegalRegionChange = onLegalRegionChange,
                onOpenAppearance = { overlays = overlays + AppOverlay.Profile(ProfilePanel.APPEARANCE) },
                onOpenWallpaper = { overlays = overlays + AppOverlay.Profile(ProfilePanel.WALLPAPER) },
                learningDashboard = learningDashboard,
                dailyLearningStats = dailyLearningStats,
                onOpenLearningHub = { overlays = overlays + AppOverlay.Profile(ProfilePanel.LEARNING) },
                favoriteIds = favoriteIds,
                onToggleFavorite = onToggleFavorite,
                onOpenSearch = { overlays = overlays + AppOverlay.Profile(ProfilePanel.SEARCH) },
                onOpenErrorMuseum = { overlays = overlays + AppOverlay.Profile(ProfilePanel.ERRORS) },
                aiFreeChallengeIds = aiFreeChallengeIds,
                onOpenAiIndependence = { overlays = overlays + AppOverlay.Profile(ProfilePanel.AI_INDEPENDENCE) },
                aiPromptCount = aiPromptCount,
                onAiPrompt = onAiPrompt,
                onOpenWorkbench = openWorkbench,
            )

            is AppOverlay.AiTeacher -> Box(
                modifier = Modifier
                    .fillMaxSize()
                    .systemBarsPadding(),
            ) {
                AiTeacherScreen(
                    onBack = popOverlay,
                    aiConfig = aiConfig,
                    onAiConfigChange = onAiConfigChange,
                    onAiPrompt = onAiPrompt,
                )
            }

            is AppOverlay.Lesson -> {
                val lesson = CourseCatalog.lesson(overlay.lessonId)
                if (lesson == null) {
                    popOverlay()
                } else {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .systemBarsPadding(),
                    ) {
                        LessonScreen(
                            lesson = lesson,
                            onBack = popOverlay,
                            onOpenLesson = openLesson,
                            onCompleteLesson = {
                                onCompleteLesson(lesson.id)
                                popOverlay()
                            },
                            legalRegionLabel = legalRegion.label,
                            onOpenWorkbench = { openWorkbench(lesson.example) },
                            onRecordWrong = onRecordWrong,
                            onResolveWrong = onResolveWrong,
                        )
                    }
                }
            }

            is AppOverlay.Workbench -> Box(
                modifier = Modifier
                    .fillMaxSize()
                    .systemBarsPadding(),
            ) {
                CodeWorkbenchScreen(
                    onBack = popOverlay,
                    initialCode = overlay.initialCode,
                )
            }

            is AppOverlay.Profile -> when (overlay.panel) {
                ProfilePanel.MAIN -> {
                    popOverlay()
                }

                ProfilePanel.APPEARANCE -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    AppearanceScreen(
                        themePreference = themePreference,
                        onThemePreferenceChange = onThemePreferenceChange,
                        accent = accent,
                        onAccentChange = onAccentChange,
                        onBack = popOverlay,
                    )
                }

                ProfilePanel.WALLPAPER -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    WallpaperScreen(
                        current = wallpaper,
                        onWallpaperChange = onWallpaperChange,
                        onBack = popOverlay,
                        customWallpaperUri = customWallpaperUri,
                        onPickWallpaper = {
                            wallpaperPicker.launch("image/*")
                        },
                    )
                }

                ProfilePanel.LEARNING -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    LearningHubScreen(
                        dashboard = learningDashboard,
                        onBack = popOverlay,
                        onOpenLesson = openLesson,
                        onOpenReview = { review ->
                            if (review.targetType == ReviewTargetType.LESSON) {
                                openLesson(review.targetId)
                            } else {
                                review.toWorkbenchCode()?.let(openWorkbench)
                            }
                        },
                    )
                }

                ProfilePanel.SEARCH -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    SearchLibraryScreen(
                        favoriteIds = favoriteIds,
                        onToggleFavorite = onToggleFavorite,
                        completedProjectIds = completedProjectIds,
                        onCompleteProject = onCompleteProject,
                        onBack = popOverlay,
                        onOpenLesson = openLesson,
                        onOpenWorkbench = openWorkbench,
                        onTrainingResult = onTrainingResult,
                    )
                }

                ProfilePanel.ERRORS -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    ErrorMuseumScreen(
                        onBack = popOverlay,
                        onOpenWorkbench = openWorkbench,
                        onOpenLesson = openLesson,
                    )
                }

                ProfilePanel.AI_INDEPENDENCE -> Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .systemBarsPadding(),
                ) {
                    AiIndependenceScreen(
                        profile = AiIndependenceEngine.build(
                            completedLessons = completedLessonIds.size,
                            completedProjects = completedProjectIds.size,
                            completedTraining = completedTrainingIds.size,
                            aiPromptCount = aiPromptCount,
                            aiFreeCompletedIds = aiFreeChallengeIds,
                        ),
                        completedChallengeIds = aiFreeChallengeIds,
                        aiPromptCount = aiPromptCount,
                        onToggleChallenge = onToggleAiFreeChallenge,
                        onOpenAi = pushAi,
                        onBack = popOverlay,
                    )
                }
            }
        }
    }
}

@Composable
private fun MainShell(
    destination: Destination,
    onDestinationChange: (Destination) -> Unit,
    onOpenLesson: (String) -> Unit,
    onOpenAi: () -> Unit,
    completedLessonIds: Set<String>,
    completedProjectIds: Set<String>,
    onCompleteProject: (String) -> Unit,
    wrongQuizIds: Set<String>,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
    completedTrainingIds: Set<String>,
    wrongTrainingIds: Set<String>,
    onTrainingResult: (exerciseId: String, correct: Boolean) -> Unit,
    legalRegion: LegalRegion,
    onLegalRegionChange: (LegalRegion) -> Unit,
    onOpenAppearance: () -> Unit,
    onOpenWallpaper: () -> Unit,
    learningDashboard: LearningDashboard,
    dailyLearningStats: DailyLearningStats,
    onOpenLearningHub: () -> Unit,
    favoriteIds: Set<String>,
    onToggleFavorite: (String) -> Unit,
    onOpenSearch: () -> Unit,
    onOpenErrorMuseum: () -> Unit,
    aiFreeChallengeIds: Set<String>,
    onOpenAiIndependence: () -> Unit,
    aiPromptCount: Int,
    onAiPrompt: () -> Unit,
    onOpenWorkbench: (String?) -> Unit,
) {
    Scaffold(
        containerColor = Color.Transparent,
        contentWindowInsets = WindowInsets.safeDrawing,
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.88f),
                tonalElevation = 0.dp,
            ) {
                Destination.entries.forEach { item ->
                    NavigationBarItem(
                        selected = destination == item,
                        onClick = {
                            onDestinationChange(item)
                        },
                        icon = {
                            Icon(
                                imageVector = when (item) {
                                    Destination.HOME -> Icons.Filled.Home
                                    Destination.COURSES -> Icons.Filled.School
                                    Destination.PRACTICE -> Icons.Filled.EditNote
                                    Destination.PROJECTS -> Icons.Filled.Code
                                    Destination.PROFILE -> Icons.Filled.Person
                                },
                                contentDescription = item.label,
                            )
                        },
                        label = { Text(text = item.label, fontSize = 10.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedTextColor = MaterialTheme.colorScheme.primary,
                            selectedIconColor = MaterialTheme.colorScheme.primary,
                            indicatorColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.10f),
                            unselectedTextColor = MaterialTheme.colorScheme.onSurfaceVariant,
                        ),
                    )
                }
            }
        },
    ) { innerPadding ->
        AdaptiveFrame {
            Box(modifier = Modifier.padding(innerPadding)) {
                when (destination) {
                    Destination.HOME -> HomeScreen(
                        onOpenLesson = onOpenLesson,
                        onOpenAi = onOpenAi,
                        onOpenLearningHub = onOpenLearningHub,
                        completedLessonIds = completedLessonIds,
                        dashboard = learningDashboard,
                        dailyLearningStats = dailyLearningStats,
                    )
                    Destination.COURSES -> CourseScreen(
                        onOpenLesson = onOpenLesson,
                        completedLessonIds = completedLessonIds,
                        onOpenLearningHub = onOpenLearningHub,
                    )
                    Destination.PRACTICE -> PracticeScreen(
                        onOpenWorkbench = onOpenWorkbench,
                        wrongQuizIds = wrongQuizIds,
                        completedTrainingIds = completedTrainingIds,
                        wrongTrainingIds = wrongTrainingIds,
                        onRecordWrong = onRecordWrong,
                        onResolveWrong = onResolveWrong,
                        onTrainingResult = onTrainingResult,
                        dueReviewCount = learningDashboard.dueReviews.size,
                        onOpenLearningHub = onOpenLearningHub,
                        onOpenErrorMuseum = onOpenErrorMuseum,
                        onOpenSearch = onOpenSearch,
                    )
                    Destination.PROJECTS -> ProjectScreen(
                        onOpenLesson = onOpenLesson,
                        onOpenWorkbench = { code -> onOpenWorkbench(code) },
                        completedProjectIds = completedProjectIds,
                        onCompleteProject = onCompleteProject,
                    )
                    Destination.PROFILE -> ProfileScreen(
                        onOpenAi = onOpenAi,
                        onOpenAppearance = onOpenAppearance,
                        onOpenWallpaper = onOpenWallpaper,
                        onOpenLearningHub = onOpenLearningHub,
                        onOpenSearch = onOpenSearch,
                        onOpenErrorMuseum = onOpenErrorMuseum,
                        onOpenAiIndependence = onOpenAiIndependence,
                        legalRegion = legalRegion,
                        onLegalRegionChange = onLegalRegionChange,
                        completedLessonIds = completedLessonIds,
                        completedProjectIds = completedProjectIds,
                        wrongQuizIds = wrongQuizIds,
                        completedTrainingIds = completedTrainingIds,
                        wrongTrainingIds = wrongTrainingIds,
                        favoriteCount = favoriteIds.size,
                        aiFreeCompleted = aiFreeChallengeIds.size,
                        aiPromptCount = aiPromptCount,
                    )
                }
            }
        }
    }
}

@Composable
private fun AdaptiveFrame(content: @Composable () -> Unit) {
    val maxWidth = LocalConfiguration.current.screenWidthDp.dp
    if (maxWidth >= 760.dp) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Transparent),
            contentAlignment = Alignment.TopCenter,
        ) {
            Box(
                modifier = Modifier
                    .widthIn(max = 720.dp)
                    .fillMaxSize(),
            ) {
                content()
            }
        }
    } else {
        Box(modifier = Modifier.fillMaxSize()) {
            content()
        }
    }
}
