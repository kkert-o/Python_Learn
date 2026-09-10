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
import com.pythonlearn.app.ui.screens.ReleaseCheckScreen
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
    RELEASE,
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
    var openLessonId by remember { mutableStateOf<String?>(null) }
    var workbenchOpen by remember { mutableStateOf(false) }
    var workbenchInitialCode by remember { mutableStateOf<String?>(null) }
    var profilePanel by remember { mutableStateOf(ProfilePanel.MAIN) }
    var aiOpen by remember { mutableStateOf(false) }

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
            workbenchOpen = false
            openLessonId = lessonId
            profilePanel = ProfilePanel.MAIN
        }
    }
    val openWorkbench: (String?) -> Unit = { code ->
        aiOpen = false
        openLessonId = null
        profilePanel = ProfilePanel.MAIN
        workbenchInitialCode = code
        workbenchOpen = true
    }
    val closeWorkbench: () -> Unit = {
        workbenchOpen = false
        workbenchInitialCode = null
    }
    val openProfilePanel: (ProfilePanel) -> Unit = { panel ->
        aiOpen = false
        openLessonId = null
        workbenchOpen = false
        profilePanel = panel
    }
    BackHandler(
        enabled = aiOpen || openLessonId != null || workbenchOpen || profilePanel != ProfilePanel.MAIN,
    ) {
        when {
            aiOpen -> aiOpen = false
            openLessonId != null -> openLessonId = null
            workbenchOpen -> closeWorkbench()
            profilePanel != ProfilePanel.MAIN -> profilePanel = ProfilePanel.MAIN
        }
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

        val lesson = openLessonId?.let(CourseCatalog::lesson)
        if (aiOpen) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                AiTeacherScreen(
                    onBack = { aiOpen = false },
                    aiConfig = aiConfig,
                    onAiConfigChange = onAiConfigChange,
                    onAiPrompt = onAiPrompt,
                )
            }
        } else if (lesson != null) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                LessonScreen(
                    lesson = lesson,
                    onBack = { openLessonId = null },
                    onOpenLesson = openLesson,
                    onCompleteLesson = {
                        onCompleteLesson(lesson.id)
                        openLessonId = null
                    },
                    legalRegionLabel = legalRegion.label,
                    onOpenWorkbench = { openWorkbench(lesson.example) },
                    onRecordWrong = onRecordWrong,
                    onResolveWrong = onResolveWrong,
                )
            }
        } else if (profilePanel == ProfilePanel.APPEARANCE) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                AppearanceScreen(
                    themePreference = themePreference,
                    onThemePreferenceChange = onThemePreferenceChange,
                    accent = accent,
                    onAccentChange = onAccentChange,
                    onBack = { profilePanel = ProfilePanel.MAIN },
                )
            }
        } else if (profilePanel == ProfilePanel.WALLPAPER) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                WallpaperScreen(
                    current = wallpaper,
                    onWallpaperChange = onWallpaperChange,
                    onBack = { profilePanel = ProfilePanel.MAIN },
                    customWallpaperUri = customWallpaperUri,
                    onPickWallpaper = {
                        wallpaperPicker.launch(
                            "image/*",
                        )
                    },
                )
            }
        } else if (profilePanel == ProfilePanel.LEARNING) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                LearningHubScreen(
                    dashboard = learningDashboard,
                    onBack = { profilePanel = ProfilePanel.MAIN },
                    onOpenLesson = { lessonId ->
                        profilePanel = ProfilePanel.MAIN
                        openLesson(lessonId)
                    },
                    onOpenReview = { review ->
                        if (review.targetType == ReviewTargetType.LESSON) {
                            profilePanel = ProfilePanel.MAIN
                            openLesson(review.targetId)
                        } else {
                            review.toWorkbenchCode()?.let(openWorkbench)
                        }
                    },
                )
            }
        } else if (profilePanel == ProfilePanel.SEARCH) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                SearchLibraryScreen(
                    favoriteIds = favoriteIds,
                    onToggleFavorite = onToggleFavorite,
                    completedProjectIds = completedProjectIds,
                    onCompleteProject = onCompleteProject,
                    onBack = { profilePanel = ProfilePanel.MAIN },
                    onOpenLesson = { lessonId ->
                        profilePanel = ProfilePanel.MAIN
                        openLesson(lessonId)
                    },
                    onOpenWorkbench = openWorkbench,
                    onTrainingResult = onTrainingResult,
                )
            }
        } else if (profilePanel == ProfilePanel.ERRORS) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                ErrorMuseumScreen(
                    onBack = { profilePanel = ProfilePanel.MAIN },
                    onOpenWorkbench = openWorkbench,
                    onOpenLesson = { lessonId ->
                        profilePanel = ProfilePanel.MAIN
                        openLesson(lessonId)
                    },
                )
            }
        } else if (profilePanel == ProfilePanel.AI_INDEPENDENCE) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
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
                    onOpenAi = { aiOpen = true },
                    onBack = { profilePanel = ProfilePanel.MAIN },
                )
            }
        } else if (profilePanel == ProfilePanel.RELEASE) {
            Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                ReleaseCheckScreen(
                    completedLessons = completedLessonIds.size,
                    completedProjects = completedProjectIds.size,
                    completedTraining = completedTrainingIds.size,
                    onBack = { profilePanel = ProfilePanel.MAIN },
                )
            }
        } else {
            MainShell(
                destination = destination,
                onDestinationChange = { destination = it },
                onOpenLesson = openLesson,
                onOpenAi = { aiOpen = true },
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
                onOpenAppearance = { profilePanel = ProfilePanel.APPEARANCE },
                onOpenWallpaper = { profilePanel = ProfilePanel.WALLPAPER },
                learningDashboard = learningDashboard,
                onOpenLearningHub = { openProfilePanel(ProfilePanel.LEARNING) },
                favoriteIds = favoriteIds,
                onToggleFavorite = onToggleFavorite,
                onOpenSearch = { openProfilePanel(ProfilePanel.SEARCH) },
                onOpenErrorMuseum = { openProfilePanel(ProfilePanel.ERRORS) },
                aiFreeChallengeIds = aiFreeChallengeIds,
                onOpenAiIndependence = { openProfilePanel(ProfilePanel.AI_INDEPENDENCE) },
                onOpenReleaseCheck = { openProfilePanel(ProfilePanel.RELEASE) },
                aiPromptCount = aiPromptCount,
                onAiPrompt = onAiPrompt,
                workbenchOpen = workbenchOpen,
                workbenchInitialCode = workbenchInitialCode,
                onOpenWorkbench = openWorkbench,
                onCloseWorkbench = closeWorkbench,
            )
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
    onOpenLearningHub: () -> Unit,
    favoriteIds: Set<String>,
    onToggleFavorite: (String) -> Unit,
    onOpenSearch: () -> Unit,
    onOpenErrorMuseum: () -> Unit,
    aiFreeChallengeIds: Set<String>,
    onOpenAiIndependence: () -> Unit,
    onOpenReleaseCheck: () -> Unit,
    aiPromptCount: Int,
    onAiPrompt: () -> Unit,
    workbenchOpen: Boolean,
    workbenchInitialCode: String?,
    onOpenWorkbench: (String?) -> Unit,
    onCloseWorkbench: () -> Unit,
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
                            onCloseWorkbench()
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
                if (workbenchOpen) {
                    CodeWorkbenchScreen(
                        onBack = onCloseWorkbench,
                        initialCode = workbenchInitialCode,
                    )
                } else {
                    when (destination) {
                        Destination.HOME -> HomeScreen(
                            onOpenLesson = onOpenLesson,
                            onOpenAi = onOpenAi,
                            onOpenLearningHub = onOpenLearningHub,
                            completedLessonIds = completedLessonIds,
                            dashboard = learningDashboard,
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
                            onOpenReleaseCheck = onOpenReleaseCheck,
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
