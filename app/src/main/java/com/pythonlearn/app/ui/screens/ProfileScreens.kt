package com.pythonlearn.app.ui.screens

import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ManageSearch
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.Gavel
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Palette
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.School
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.Icon
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.TextButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DemoStats
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.SectionTitle
import com.pythonlearn.app.ui.components.Tag
import com.pythonlearn.app.ui.theme.AccentOption
import com.pythonlearn.app.ui.theme.ThemePreference
import com.pythonlearn.app.ui.theme.WallpaperOption
import com.pythonlearn.app.ui.theme.accentOptions
import com.pythonlearn.app.ui.theme.LegalRegion
import com.pythonlearn.app.ui.theme.legalRegionOptions
import com.pythonlearn.app.ui.theme.wallpaperOptions

@Composable
fun ProfileScreen(
    onOpenAi: () -> Unit,
    onOpenAppearance: () -> Unit,
    onOpenWallpaper: () -> Unit,
    onOpenLearningHub: () -> Unit,
    onOpenSearch: () -> Unit,
    onOpenErrorMuseum: () -> Unit,
    onOpenAiIndependence: () -> Unit,
    legalRegion: LegalRegion,
    onLegalRegionChange: (LegalRegion) -> Unit,
    completedLessonIds: Set<String>,
    completedProjectIds: Set<String>,
    wrongQuizIds: Set<String>,
    completedTrainingIds: Set<String>,
    wrongTrainingIds: Set<String>,
    favoriteCount: Int,
    aiFreeCompleted: Int,
    aiPromptCount: Int,
) {
    var legalDialogOpen by remember { mutableStateOf(false) }
    if (legalDialogOpen) {
        AlertDialog(
            onDismissRequest = { legalDialogOpen = false },
            title = { Text(text = "法律地区") },
            text = {
                Column {
                    legalRegionOptions.forEach { region ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onLegalRegionChange(region)
                                    legalDialogOpen = false
                                }
                                .padding(vertical = 9.dp),
                        ) {
                            Icon(
                                imageVector = if (legalRegion.id == region.id) {
                                    Icons.Filled.Check
                                } else {
                                    Icons.Filled.RadioButtonUnchecked
                                },
                                contentDescription = null,
                                tint = if (legalRegion.id == region.id) {
                                    MaterialTheme.colorScheme.primary
                                } else {
                                    MaterialTheme.colorScheme.onSurfaceVariant
                                },
                            )
                            Text(text = region.label)
                        }
                    }
                }
            },
            confirmButton = {},
            dismissButton = {
                TextButton(onClick = { legalDialogOpen = false }) {
                    Text(text = "取消")
                }
            },
        )
    }
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 18.dp, bottom = 18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text(
                text = "我的",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
        }

        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Filled.School,
                            contentDescription = null,
                            modifier = Modifier.width(30.dp),
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = if (completedLessonIds.isEmpty()) {
                                    DemoStats.pythonLevel
                                } else {
                                    "Python Lv.${(completedLessonIds.size / 3).coerceAtLeast(1) + 1}"
                                },
                                fontWeight = FontWeight.Bold,
                            )
                            MutedText(text = "学习进度已保存 · 换设备不会同步")
                        }
                        Tag(
                            text = if (completedLessonIds.isEmpty()) "未开始" else "学习中",
                            active = completedLessonIds.isNotEmpty(),
                        )
                    }
                    Spacer(modifier = Modifier.height(14.dp))
                    Row {
                        StatCell("${completedLessonIds.size}", "完成课程", Modifier.weight(1f))
                        Spacer(modifier = Modifier.width(8.dp))
                        StatCell("${completedProjectIds.size}", "完成项目", Modifier.weight(1f))
                        Spacer(modifier = Modifier.width(8.dp))
                        StatCell("${wrongQuizIds.size + wrongTrainingIds.size}", "待复习", Modifier.weight(1f))
                    }
                }
            }
        }

        item {
            val finishedStages = CourseCatalog.stages.count { stage ->
                CourseCatalog.stageProgress(stage, completedLessonIds) == 100
            }
            SectionTitle(
                title = "能力数据",
                trailing = if (finishedStages == 0) "尚未完成阶段" else "完成 $finishedStages 个阶段",
            )
        }

        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    CourseCatalog.stages.forEach { stage ->
                        SkillLine(
                            name = stage.name,
                            value = CourseCatalog.stageProgress(stage, completedLessonIds),
                        )
                    }
                    SkillLine(
                        name = "项目实战",
                        value = ProjectCatalog.all.count { it.id in completedProjectIds } * 100 / ProjectCatalog.all.size,
                    )
                    SkillLine(
                        name = "编程训练",
                        value = completedTrainingIds.size * 100 / TrainingCatalog.all.size,
                    )
                }
            }
        }

        item {
            SectionTitle(title = "学习工具")
        }

        item {
            GlassCard {
                Column {
                    SettingsRow(
                        title = "学习中心",
                        subtitle = "知识树 · 到期复习 · 下一步推荐",
                        imageVector = Icons.Filled.School,
                        onClick = onOpenLearningHub,
                    )
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(
                        title = "搜索与收藏",
                        subtitle = "$favoriteCount 项收藏 · 第三方库与工程实践",
                        imageVector = Icons.AutoMirrored.Filled.ManageSearch,
                        onClick = onOpenSearch,
                    )
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(
                        title = "错误博物馆",
                        subtitle = "报错类型、原因、修复与预防",
                        imageVector = Icons.Filled.BugReport,
                        onClick = onOpenErrorMuseum,
                    )
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(
                        title = "AI 独立能力",
                        subtitle = "$aiFreeCompleted 项 AI-Free 已完成 · $aiPromptCount 次 AI 提问",
                        imageVector = Icons.Filled.Psychology,
                        onClick = onOpenAiIndependence,
                    )
                }
            }
        }

        item {
            SectionTitle(title = "外观与设置")
        }

        item {
            GlassCard {
                Column {
                    SettingsRow(title = "AI Python 老师", subtitle = "老师模式 · 引导式问答", imageVector = Icons.Filled.SmartToy, onClick = onOpenAi)
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(title = "外观", subtitle = "浅色 / 深色 / 跟随系统", imageVector = Icons.Filled.Palette, onClick = onOpenAppearance)
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(title = "壁纸", subtitle = "内置配色壁纸", imageVector = Icons.Filled.Image, onClick = onOpenWallpaper)
                    androidx.compose.material3.HorizontalDivider(
                        modifier = Modifier.padding(horizontal = 16.dp),
                        color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                    )
                    SettingsRow(
                        title = "法律地区",
                        subtitle = "${legalRegion.label} · 本模块不构成法律意见",
                        imageVector = Icons.Filled.Gavel,
                        onClick = { legalDialogOpen = true },
                    )
                }
            }
        }
    }
}

@Composable
fun AppearanceScreen(
    themePreference: ThemePreference,
    onThemePreferenceChange: (ThemePreference) -> Unit,
    accent: AccentOption,
    onAccentChange: (AccentOption) -> Unit,
    onBack: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 18.dp),
    ) {
        BackHeader(title = "外观", onBack = onBack)
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 24.dp),
        ) {
            SectionTitle(title = "主题")
            Spacer(modifier = Modifier.height(6.dp))
            GlassCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    ThemePreference.entries.forEach { preference ->
                        SelectionButton(
                            text = preference.label,
                            selected = themePreference == preference,
                            modifier = Modifier.weight(1f),
                        ) {
                            onThemePreferenceChange(preference)
                        }
                    }
                }
            }
            Spacer(modifier = Modifier.height(14.dp))
            SectionTitle(title = "主色")
            Spacer(modifier = Modifier.height(6.dp))
            GlassCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    accentOptions.forEach { option ->
                        ColorDot(
                            color = option.color,
                            selected = accent == option,
                            modifier = Modifier.weight(1f),
                        ) {
                            onAccentChange(option)
                        }
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            GlassCard {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(text = "当前主色", fontWeight = FontWeight.Bold)
                    MutedText(text = "${accent.name} · 深色与浅色模式会自动适配", small = false)
                }
            }
        }
    }
}

@Composable
fun WallpaperScreen(
    current: WallpaperOption,
    onWallpaperChange: (WallpaperOption) -> Unit,
    onBack: () -> Unit,
    customWallpaperUri: Uri?,
    onPickWallpaper: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 18.dp),
    ) {
        BackHeader(title = "壁纸", onBack = onBack)
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 24.dp),
        ) {
            SectionTitle(title = "当前壁纸")
            Spacer(modifier = Modifier.height(8.dp))
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .height(132.dp)
                    .background(
                        Brush.verticalGradient(current.lightColors),
                        RoundedCornerShape(17.dp),
                    ),
            ) {
                if (current.isCustom && customWallpaperUri != null) {
                    AsyncImage(
                        model = customWallpaperUri,
                        contentDescription = "自定义壁纸",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop,
                    )
                }
                Box(
                    modifier = Modifier
                        .padding(16.dp)
                        .fillMaxSize()
                        .background(Color.White.copy(alpha = 0.58f), RoundedCornerShape(14.dp)),
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.Center,
                    ) {
                        Text(text = "Python 课程", fontWeight = FontWeight.Bold, color = Color(0xFF1E262D))
                        MutedText(text = "壁纸预览", small = false)
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            SectionTitle(title = "自定义")
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onPickWallpaper)
                    .background(
                        if (current.isCustom) {
                            MaterialTheme.colorScheme.primaryContainer
                        } else {
                            MaterialTheme.colorScheme.surface.copy(alpha = 0.82f)
                        },
                        RoundedCornerShape(15.dp),
                    )
                    .padding(13.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    imageVector = Icons.Filled.Image,
                    contentDescription = null,
                    modifier = Modifier.width(24.dp),
                    tint = MaterialTheme.colorScheme.primary,
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = if (current.isCustom) "自定义壁纸已启用" else "从相册导入", fontWeight = FontWeight.Bold)
                    MutedText(text = "系统会保留你选择的图片访问权限")
                }
                Text(text = "选择", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(14.dp))
            SectionTitle(title = "内置壁纸")
            Spacer(modifier = Modifier.height(8.dp))
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                wallpaperOptions.forEach { option ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { onWallpaperChange(option) }
                            .background(
                                if (current == option) {
                                    MaterialTheme.colorScheme.primaryContainer
                                } else {
                                    MaterialTheme.colorScheme.surface.copy(alpha = 0.82f)
                                },
                                RoundedCornerShape(15.dp),
                            )
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            modifier = Modifier
                                .width(52.dp)
                                .height(36.dp)
                                .background(
                                    Brush.linearGradient(option.lightColors.take(2)),
                                    RoundedCornerShape(10.dp),
                                ),
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = option.name, fontWeight = FontWeight.Bold)
                            MutedText(text = if (current == option) "正在使用" else "轻点使用")
                        }
                        Icon(
                            imageVector = if (current == option) Icons.Filled.Check else Icons.Filled.ChevronRight,
                            contentDescription = null,
                            tint = if (current == option) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.width(18.dp),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun BackHeader(title: String, onBack: () -> Unit) {
    BackBar(title = title, onBack = onBack, modifier = Modifier.padding(horizontal = 0.dp))
}

@Composable
private fun SelectionButton(
    text: String,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    Box(
        modifier = modifier
            .background(
                if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface.copy(alpha = 0.7f),
                RoundedCornerShape(11.dp),
            )
            .clickable(onClick = onClick)
            .padding(vertical = 10.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = text,
            color = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
            fontWeight = FontWeight.SemiBold,
            fontSize = 12.sp,
        )
    }
}

@Composable
private fun ColorDot(
    color: Color,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    Box(
        modifier = modifier
            .height(42.dp)
            .background(
                if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface.copy(alpha = 0.72f),
                RoundedCornerShape(12.dp),
            )
            .clickable(onClick = onClick)
            .padding(4.dp),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(26.dp)
                .background(color, RoundedCornerShape(9.dp)),
        )
    }
}

@Composable
private fun StatCell(value: String, label: String, modifier: Modifier = Modifier) {
    Column(modifier = modifier) {
        Text(text = value, fontWeight = FontWeight.Bold, fontSize = 20.sp)
        MutedText(text = label)
    }
}

@Composable
private fun SkillLine(name: String, value: Int) {
    Column(modifier = Modifier.padding(bottom = 10.dp)) {
        Row(modifier = Modifier.fillMaxWidth()) {
            Text(text = name, modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
            MutedText(text = "$value%")
        }
        Spacer(modifier = Modifier.height(4.dp))
        ProgressTrack(progress = value)
    }
}

@Composable
private fun SettingsRow(
    title: String,
    subtitle: String,
    imageVector: ImageVector,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = imageVector,
            contentDescription = null,
            modifier = Modifier.width(22.dp),
            tint = MaterialTheme.colorScheme.primary,
        )
        Spacer(modifier = Modifier.width(11.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(text = title, fontWeight = FontWeight.SemiBold)
            MutedText(text = subtitle)
        }
        Icon(
            imageVector = Icons.Filled.ChevronRight,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(18.dp),
        )
    }
}
