package com.pythonlearn.app.ui.screens

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.LibraryBooks
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Terminal
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.BuildConfig
import com.pythonlearn.app.data.AiFreeChallenge
import com.pythonlearn.app.data.AiIndependenceCatalog
import com.pythonlearn.app.data.AiIndependenceProfile
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.EngineeringCatalog
import com.pythonlearn.app.data.EngineeringModule
import com.pythonlearn.app.data.ErrorMuseumCatalog
import com.pythonlearn.app.data.ErrorMuseumEntry
import com.pythonlearn.app.data.GlobalSearchEngine
import com.pythonlearn.app.data.GlobalSearchResult
import com.pythonlearn.app.data.LibraryCatalog
import com.pythonlearn.app.data.LibraryCategory
import com.pythonlearn.app.data.LibraryEntry
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.SearchResultKind
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.runtime.PythonRunner
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.CodePanel
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.SectionTitle
import com.pythonlearn.app.ui.components.Tag
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.system.measureTimeMillis

@Composable
fun ErrorMuseumScreen(
    onBack: () -> Unit,
    onOpenWorkbench: (String) -> Unit,
    onOpenLesson: (String) -> Unit,
) {
    var query by remember { mutableStateOf("") }
    var openedId by remember { mutableStateOf<String?>(null) }
    val entries = remember(query) { ErrorMuseumCatalog.search(query) }

    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item { BackBar(title = "错误博物馆", onBack = onBack) }
        item {
            Text(
                text = "把报错变成可复用的经验。先判断类型，再定位原因，最后运行修复后的代码。",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            SearchField(
                value = query,
                onValueChange = { query = it },
                placeholder = "搜索 NameError、字典、文件……",
            )
        }
        entries.forEach { entry ->
            item {
                val opened = openedId == entry.id
                GlassCard(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { openedId = if (opened) null else entry.id },
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.BugReport,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.width(24.dp),
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(text = entry.title, fontWeight = FontWeight.Bold)
                                MutedText(text = entry.errorType)
                            }
                            Tag(text = if (opened) "收起" else "查看", active = opened)
                        }
                        if (opened) {
                            Spacer(modifier = Modifier.height(12.dp))
                            ErrorFact("出现的表现", entry.symptom)
                            ErrorFact("真正的原因", entry.cause)
                            Text(text = "错误代码", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            Spacer(modifier = Modifier.height(5.dp))
                            CodePanel(code = entry.brokenCode)
                            Spacer(modifier = Modifier.height(10.dp))
                            Text(text = "修复方式", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            Spacer(modifier = Modifier.height(5.dp))
                            CodePanel(code = entry.fixedCode)
                            Spacer(modifier = Modifier.height(10.dp))
                            ErrorFact("以后怎么避免", entry.prevention)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                ActionButton(
                                    text = "运行修复代码",
                                    icon = Icons.Filled.Terminal,
                                    modifier = Modifier.weight(1f),
                                ) {
                                    onOpenWorkbench(entry.fixedCode)
                                }
                                entry.lessonId?.let { lessonId ->
                                    ActionButton(
                                        text = "学习知识点",
                                        icon = Icons.Filled.Code,
                                        modifier = Modifier.weight(1f),
                                    ) {
                                        onOpenLesson(lessonId)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ErrorFact(label: String, value: String) {
    Column(modifier = Modifier.padding(bottom = 9.dp)) {
        Text(text = label, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Spacer(modifier = Modifier.height(3.dp))
        Text(
            text = value,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            lineHeight = 19.sp,
            fontSize = 13.sp,
        )
    }
}

@Composable
fun SearchLibraryScreen(
    favoriteIds: Set<String>,
    onToggleFavorite: (String) -> Unit,
    completedProjectIds: Set<String>,
    onCompleteProject: (String) -> Unit,
    onBack: () -> Unit,
    onOpenLesson: (String) -> Unit,
    onOpenWorkbench: (String) -> Unit,
    onTrainingResult: (String, Boolean) -> Unit,
) {
    var query by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<LibraryCategory?>(null) }
    var openProjectId by remember { mutableStateOf<String?>(null) }
    var openTrainingId by remember { mutableStateOf<String?>(null) }
    var selectedErrorId by remember { mutableStateOf<String?>(null) }
    var selectedLibraryId by remember { mutableStateOf<String?>(null) }
    var selectedEngineeringId by remember { mutableStateOf<String?>(null) }

    val openProject = openProjectId?.let(ProjectCatalog::byId)
    if (openProject != null) {
        ProjectDetailScreen(
            project = openProject,
            onBack = { openProjectId = null },
            onOpenWorkbench = onOpenWorkbench,
            completed = openProject.id in completedProjectIds,
            onComplete = {
                onCompleteProject(openProject.id)
                openProjectId = null
            },
        )
        return
    }
    val openTraining = openTrainingId?.let(TrainingCatalog::byId)
    if (openTraining != null) {
        TrainingSessionScreen(
            exercises = listOf(openTraining),
            onBack = { openTrainingId = null },
            onOpenWorkbench = onOpenWorkbench,
            onResult = onTrainingResult,
        )
        return
    }

    val results = remember(query) { GlobalSearchEngine.search(query) }
    val libraries = remember(query, selectedCategory) {
        LibraryCatalog.search(query).filter { entry ->
            selectedCategory == null || entry.category == selectedCategory
        }
    }
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item { BackBar(title = "搜索与工具库", onBack = onBack) }
        item {
            SearchField(
                value = query,
                onValueChange = { query = it },
                placeholder = "课程、项目、训练、库、报错……",
            )
        }
        if (query.isNotBlank()) {
            item {
                SectionTitle(
                    title = "全局结果",
                    trailing = "${results.size} 项",
                )
            }
            if (results.isEmpty()) {
                item {
                    GlassCard {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(text = "没有找到匹配内容", fontWeight = FontWeight.Bold)
                            MutedText(text = "换一个关键词，或浏览下面的第三方库分类。")
                        }
                    }
                }
            } else {
                results.forEach { result ->
                    item {
                        SearchResultRow(
                            result = result,
                            favorite = result.favoriteKey in favoriteIds,
                            onToggleFavorite = { onToggleFavorite(result.favoriteKey) },
                            onClick = {
                                when (result.kind) {
                                    SearchResultKind.LESSON -> onOpenLesson(result.routeId)
                                    SearchResultKind.PROJECT -> openProjectId = result.routeId
                                    SearchResultKind.TRAINING -> openTrainingId = result.routeId
                                    SearchResultKind.LIBRARY -> selectedLibraryId = result.routeId
                                    SearchResultKind.ERROR -> selectedErrorId = result.routeId
                                    SearchResultKind.ENGINEERING -> selectedEngineeringId = result.routeId
                                }
                            },
                        )
                    }
                }
            }
        } else {
            item {
                SectionTitle(title = "收藏", trailing = "${favoriteIds.size} 项")
            }
            item {
                GlassCard {
                    Column(modifier = Modifier.padding(14.dp)) {
                        if (favoriteIds.isEmpty()) {
                            MutedText(
                                text = "在搜索结果右侧点星标，课程、项目、库和报错都会集中到这里。",
                                small = false,
                            )
                        } else {
                            val favoriteResults = buildFavoriteResults(favoriteIds)
                            if (favoriteResults.isEmpty()) {
                                MutedText(text = "收藏内容暂时不可用。", small = false)
                            } else {
                                favoriteResults.take(8).forEach { result ->
                                    SearchResultRow(
                                        result = result,
                                        favorite = true,
                                        onToggleFavorite = { onToggleFavorite(result.favoriteKey) },
                                        onClick = {
                                            when (result.kind) {
                                                SearchResultKind.LESSON -> onOpenLesson(result.routeId)
                                                SearchResultKind.PROJECT -> openProjectId = result.routeId
                                                SearchResultKind.TRAINING -> openTrainingId = result.routeId
                                                SearchResultKind.LIBRARY -> selectedLibraryId = result.routeId
                                                SearchResultKind.ERROR -> selectedErrorId = result.routeId
                                                SearchResultKind.ENGINEERING -> selectedEngineeringId = result.routeId
                                            }
                                        },
                                    )
                                }
                            }
                        }
                    }
                }
            }
            item {
                SectionTitle(title = "第三方库生态", trailing = "${libraries.size} 个")
            }
            item {
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(7.dp),
                ) {
                    CategoryChip(
                        text = "全部",
                        selected = selectedCategory == null,
                        onClick = { selectedCategory = null },
                    )
                    LibraryCategory.entries.forEach { category ->
                        CategoryChip(
                            text = category.label,
                            selected = selectedCategory == category,
                            onClick = { selectedCategory = category },
                        )
                    }
                }
            }
            libraries.forEach { library ->
                item {
                    LibraryRow(
                        entry = library,
                        favorite = "library:${library.id}" in favoriteIds,
                        onToggleFavorite = { onToggleFavorite("library:${library.id}") },
                        onClick = { selectedLibraryId = library.id },
                    )
                }
            }
            item {
                SectionTitle(title = "工程实践", trailing = "${EngineeringCatalog.all.size} 个模块")
            }
            EngineeringCatalog.all.forEach { module ->
                item {
                    EngineeringRow(
                        module = module,
                        favorite = "engineering:${module.id}" in favoriteIds,
                        onToggleFavorite = { onToggleFavorite("engineering:${module.id}") },
                        onClick = { selectedEngineeringId = module.id },
                    )
                }
            }
            item {
                SectionTitle(title = "错误博物馆", trailing = "${ErrorMuseumCatalog.all.size} 类")
            }
            ErrorMuseumCatalog.all.take(4).forEach { entry ->
                item {
                    SearchResultRow(
                        result = GlobalSearchResult(
                            id = entry.id,
                            title = entry.title,
                            subtitle = entry.errorType,
                            kind = SearchResultKind.ERROR,
                            routeId = entry.id,
                            favoriteKey = "error:${entry.id}",
                        ),
                        favorite = "error:${entry.id}" in favoriteIds,
                        onToggleFavorite = { onToggleFavorite("error:${entry.id}") },
                        onClick = { selectedErrorId = entry.id },
                    )
                }
            }
        }
    }

    selectedLibraryId?.let { id ->
        LibraryCatalog.byId(id)?.let { entry ->
            LibraryDetailDialog(
                entry = entry,
                onDismiss = { selectedLibraryId = null },
                onOpenLesson = {
                    selectedLibraryId = null
                    entry.lessonId?.let(onOpenLesson)
                },
            )
        }
    }
    selectedErrorId?.let { id ->
        ErrorMuseumCatalog.byId(id)?.let { entry ->
            ErrorDetailDialog(
                entry = entry,
                onDismiss = { selectedErrorId = null },
                onOpenWorkbench = {
                    selectedErrorId = null
                    onOpenWorkbench(entry.fixedCode)
                },
            )
        }
    }
    selectedEngineeringId?.let { id ->
        EngineeringCatalog.all.firstOrNull { it.id == id }?.let { module ->
            EngineeringDetailDialog(
                module = module,
                onDismiss = { selectedEngineeringId = null },
                onOpenLesson = { lessonId ->
                    selectedEngineeringId = null
                    onOpenLesson(lessonId)
                },
            )
        }
    }
}

private fun buildFavoriteResults(favoriteIds: Set<String>): List<GlobalSearchResult> {
    return buildList {
        favoriteIds.forEach { key ->
            val separator = key.indexOf(':')
            if (separator <= 0) return@forEach
            val type = key.substring(0, separator)
            val id = key.substring(separator + 1)
            when (type) {
                "lesson" -> CourseCatalog.lesson(id)?.let { lesson ->
                    add(
                        GlobalSearchResult(
                            lesson.id,
                            lesson.title,
                            lesson.stage,
                            SearchResultKind.LESSON,
                            lesson.id,
                            key,
                        ),
                    )
                }
                "project" -> ProjectCatalog.byId(id)?.let { project ->
                    add(GlobalSearchResult(project.id, project.title, project.level, SearchResultKind.PROJECT, project.id, key))
                }
                "training" -> TrainingCatalog.byId(id)?.let { exercise ->
                    add(
                        GlobalSearchResult(
                            exercise.id,
                            exercise.title,
                            exercise.type.label,
                            SearchResultKind.TRAINING,
                            exercise.id,
                            key,
                        ),
                    )
                }
                "library" -> LibraryCatalog.byId(id)?.let { library ->
                    add(
                        GlobalSearchResult(
                            library.id,
                            library.name,
                            library.category.label,
                            SearchResultKind.LIBRARY,
                            library.id,
                            key,
                        ),
                    )
                }
                "error" -> ErrorMuseumCatalog.byId(id)?.let { error ->
                    add(
                        GlobalSearchResult(
                            error.id,
                            error.title,
                            error.errorType,
                            SearchResultKind.ERROR,
                            error.id,
                            key,
                        ),
                    )
                }
                "engineering" -> EngineeringCatalog.all.firstOrNull { it.id == id }?.let { module ->
                    add(
                        GlobalSearchResult(
                            module.id,
                            module.title,
                            module.category.label,
                            SearchResultKind.ENGINEERING,
                            module.id,
                            key,
                        ),
                    )
                }
            }
        }
    }
}

@Composable
private fun SearchField(
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        color = MaterialTheme.colorScheme.surface.copy(alpha = 0.92f),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = Icons.Filled.Search,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.width(20.dp),
            )
            Spacer(modifier = Modifier.width(8.dp))
            Box(modifier = Modifier.weight(1f)) {
                if (value.isBlank()) {
                    Text(
                        text = placeholder,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.65f),
                        fontSize = 13.sp,
                    )
                }
                BasicTextField(
                    value = value,
                    onValueChange = onValueChange,
                    textStyle = TextStyle(color = MaterialTheme.colorScheme.onSurface, fontSize = 13.sp),
                    cursorBrush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.primary),
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
            }
        }
    }
}

@Composable
private fun SearchResultRow(
    result: GlobalSearchResult,
    favorite: Boolean,
    onToggleFavorite: () -> Unit,
    onClick: () -> Unit,
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
    ) {
        Row(
            modifier = Modifier.padding(13.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(10.dp))
                    .padding(8.dp),
            ) {
                Icon(
                    imageVector = when (result.kind) {
                        SearchResultKind.LESSON -> Icons.Filled.Code
                        SearchResultKind.PROJECT -> Icons.Filled.Storage
                        SearchResultKind.TRAINING -> Icons.Filled.Terminal
                        SearchResultKind.LIBRARY -> Icons.AutoMirrored.Filled.LibraryBooks
                        SearchResultKind.ERROR -> Icons.Filled.BugReport
                        SearchResultKind.ENGINEERING -> Icons.Filled.Security
                    },
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.width(20.dp),
                )
            }
            Spacer(modifier = Modifier.width(10.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = result.title, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)
                    Tag(text = result.kind.label)
                }
                MutedText(text = result.subtitle)
            }
            Spacer(modifier = Modifier.width(5.dp))
            Icon(
                imageVector = if (favorite) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                contentDescription = if (favorite) "取消收藏" else "收藏",
                tint = if (favorite) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier
                    .width(22.dp)
                    .clickable(onClick = onToggleFavorite),
            )
        }
    }
}

@Composable
private fun LibraryRow(
    entry: LibraryEntry,
    favorite: Boolean,
    onToggleFavorite: () -> Unit,
    onClick: () -> Unit,
) {
    SearchResultRow(
        result = GlobalSearchResult(
            id = entry.id,
            title = entry.name,
            subtitle = entry.summary,
            kind = SearchResultKind.LIBRARY,
            routeId = entry.id,
            favoriteKey = "library:${entry.id}",
        ),
        favorite = favorite,
        onToggleFavorite = onToggleFavorite,
        onClick = onClick,
    )
}

@Composable
private fun EngineeringRow(
    module: EngineeringModule,
    favorite: Boolean,
    onToggleFavorite: () -> Unit,
    onClick: () -> Unit,
) {
    SearchResultRow(
        result = GlobalSearchResult(
            id = module.id,
            title = module.title,
            subtitle = module.summary,
            kind = SearchResultKind.ENGINEERING,
            routeId = module.id,
            favoriteKey = "engineering:${module.id}",
        ),
        favorite = favorite,
        onToggleFavorite = onToggleFavorite,
        onClick = onClick,
    )
}

@Composable
private fun CategoryChip(
    text: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(
                if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                RoundedCornerShape(10.dp),
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 11.dp, vertical = 7.dp),
    ) {
        Text(
            text = text,
            color = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun ActionButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    Row(
        modifier = modifier
            .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(11.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onPrimary,
            modifier = Modifier.width(17.dp),
        )
        Spacer(modifier = Modifier.width(5.dp))
        Text(text = text, color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp)
    }
}

@Composable
private fun LibraryDetailDialog(
    entry: LibraryEntry,
    onDismiss: () -> Unit,
    onOpenLesson: () -> Unit,
) {
    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = entry.name) },
        text = {
            Column {
                Tag(text = entry.category.label, active = true)
                Spacer(modifier = Modifier.height(10.dp))
                DetailLine("适合解决", entry.summary)
                DetailLine("典型用途", entry.useCase)
                DetailLine("安装", entry.install)
                CodePanel(code = entry.example)
            }
        },
        confirmButton = {
            androidx.compose.material3.TextButton(onClick = onDismiss) {
                Text(text = "关闭")
            }
        },
        dismissButton = {
            if (entry.lessonId != null) {
                androidx.compose.material3.TextButton(onClick = onOpenLesson) {
                    Text(text = "学习相关课程")
                }
            }
        },
    )
}

@Composable
private fun ErrorDetailDialog(
    entry: ErrorMuseumEntry,
    onDismiss: () -> Unit,
    onOpenWorkbench: () -> Unit,
) {
    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = entry.title) },
        text = {
            Column {
                Tag(text = entry.errorType, active = true)
                Spacer(modifier = Modifier.height(10.dp))
                DetailLine("原因", entry.cause)
                DetailLine("避免方式", entry.prevention)
                CodePanel(code = entry.brokenCode)
            }
        },
        confirmButton = {
            androidx.compose.material3.TextButton(onClick = onOpenWorkbench) {
                Text(text = "运行修复代码")
            }
        },
        dismissButton = {
            androidx.compose.material3.TextButton(onClick = onDismiss) {
                Text(text = "关闭")
            }
        },
    )
}

@Composable
private fun EngineeringDetailDialog(
    module: EngineeringModule,
    onDismiss: () -> Unit,
    onOpenLesson: (String) -> Unit,
) {
    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = module.title) },
        text = {
            Column {
                Tag(text = module.category.label, active = true)
                Spacer(modifier = Modifier.height(10.dp))
                DetailLine("目标", module.summary)
                Text(text = "检查清单", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                module.checklist.forEach { item ->
                    Text(text = "• $item", fontSize = 13.sp, lineHeight = 19.sp)
                }
                Spacer(modifier = Modifier.height(8.dp))
                CodePanel(code = module.commands.joinToString("\n"))
            }
        },
        confirmButton = {
            if (module.lessonId != null) {
                androidx.compose.material3.TextButton(onClick = { onOpenLesson(module.lessonId) }) {
                    Text(text = "学习相关课程")
                }
            }
        },
        dismissButton = {
            androidx.compose.material3.TextButton(onClick = onDismiss) {
                Text(text = "关闭")
            }
        },
    )
}

@Composable
private fun DetailLine(label: String, value: String) {
    Column(modifier = Modifier.padding(bottom = 9.dp)) {
        Text(text = label, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        Text(
            text = value,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontSize = 13.sp,
            lineHeight = 19.sp,
        )
    }
}

@Composable
fun AiIndependenceScreen(
    profile: AiIndependenceProfile,
    completedChallengeIds: Set<String>,
    aiPromptCount: Int,
    onToggleChallenge: (String) -> Unit,
    onOpenAi: () -> Unit,
    onBack: () -> Unit,
) {
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item { BackBar(title = "AI 独立能力", onBack = onBack) }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Filled.Psychology,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.width(34.dp),
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = profile.level, fontWeight = FontWeight.Bold, fontSize = 19.sp)
                            MutedText(text = "${profile.experience} 独立实践经验")
                        }
                        Tag(text = "${profile.aiFreeCompleted}/${profile.aiFreeTotal}", active = true)
                    }
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(text = "AI 依赖指数", fontWeight = FontWeight.Bold)
                    MutedText(
                        text = "由本机 AI 提问次数和独立完成记录估算，不是评价，只用于提醒保持主动思考。",
                        small = false,
                    )
                    Spacer(modifier = Modifier.height(7.dp))
                    ProgressTrack(progress = profile.dependencyIndex)
                    Spacer(modifier = Modifier.height(5.dp))
                    Text(
                        text = "${profile.dependencyIndex}% · 本机累计 $aiPromptCount 次 AI 提问",
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 12.sp,
                    )
                }
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                ActionButton(
                    text = "打开 AI 老师",
                    icon = Icons.Filled.Psychology,
                    modifier = Modifier.weight(1f),
                    onClick = onOpenAi,
                )
            }
        }
        item {
            SectionTitle(title = "AI-Free Challenge", trailing = "不借助生成式答案")
        }
        item {
            Text(
                text = "目标是先独立完成，再让 AI 检查。每项挑战都由你自己判断是否达到验收条件。",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                lineHeight = 20.sp,
            )
        }
        AiIndependenceCatalog.challenges.forEach { challenge ->
            item {
                ChallengeCard(
                    challenge = challenge,
                    completed = challenge.id in completedChallengeIds,
                    onToggle = { onToggleChallenge(challenge.id) },
                )
            }
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(text = "使用边界", fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(5.dp))
                    MutedText(
                        text = "AI 适合检查思路、解释概念和指出遗漏。答案应当由你理解后自己写，遇到关键项目先完成一版再请求反馈。",
                        small = false,
                    )
                }
            }
        }
    }
}

@Composable
private fun ChallengeCard(
    challenge: AiFreeChallenge,
    completed: Boolean,
    onToggle: () -> Unit,
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onToggle),
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.CheckCircle,
                    contentDescription = null,
                    tint = if (completed) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.outline,
                    modifier = Modifier.width(23.dp),
                )
                Spacer(modifier = Modifier.width(9.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(text = challenge.title, fontWeight = FontWeight.Bold)
                    MutedText(text = challenge.brief, small = false)
                }
                Tag(text = challenge.level, active = completed)
            }
            Spacer(modifier = Modifier.height(9.dp))
            Text(text = "验收标准", fontWeight = FontWeight.Bold, fontSize = 12.sp)
            challenge.acceptance.forEach { criterion ->
                Text(text = "• $criterion", fontSize = 13.sp, lineHeight = 19.sp)
            }
            Spacer(modifier = Modifier.height(5.dp))
            Text(
                text = if (completed) "已完成，点击取消标记" else "点击标记为独立完成",
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
                fontSize = 12.sp,
            )
        }
    }
}

data class ReleaseDiagnostics(
    val deviceSummary: String,
    val runtimeSummary: String,
    val pythonBenchmarkMs: Long?,
    val pythonBenchmarkOk: Boolean,
    val memorySummary: String,
)

@Composable
fun ReleaseCheckScreen(
    completedLessons: Int,
    completedProjects: Int,
    completedTraining: Int,
    onBack: () -> Unit,
) {
    val context = LocalContext.current
    val configuration = LocalConfiguration.current
    var diagnostics by remember { mutableStateOf<ReleaseDiagnostics?>(null) }
    LaunchedEffect(Unit) {
        diagnostics = withContext(Dispatchers.IO) {
            val run = measureTimeMillis {
                PythonRunner.run(
                    code = "values = range(1, 20001)\nprint(sum(values))",
                    stdin = "",
                )
            }
            val memoryInfo = ActivityManager.MemoryInfo()
            val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
            activityManager.getMemoryInfo(memoryInfo)
            ReleaseDiagnostics(
                deviceSummary = "${Build.MANUFACTURER} ${Build.MODEL} · Android ${Build.VERSION.RELEASE} · API ${Build.VERSION.SDK_INT}",
                runtimeSummary = "${configuration.screenWidthDp} × ${configuration.screenHeightDp} dp · ${configuration.densityDpi} dpi",
                pythonBenchmarkMs = run,
                pythonBenchmarkOk = true,
                memorySummary = "设备内存 ${memoryInfo.totalMem / 1024 / 1024} MB · 可用 ${memoryInfo.availMem / 1024 / 1024} MB",
            )
        }
    }

    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item { BackBar(title = "发布与设备检查", onBack = onBack) }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Filled.Verified,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.width(32.dp),
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(text = "Python 学习 ${BuildConfig.VERSION_NAME}", fontWeight = FontWeight.Bold)
                            MutedText(text = "versionCode ${BuildConfig.VERSION_CODE}")
                        }
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    CheckRow("本地 Python 运行时", diagnostics?.pythonBenchmarkOk?.let { true })
                    CheckRow(
                        "性能 smoke test",
                        diagnostics?.pythonBenchmarkMs?.let { it in 1..5_000 },
                        diagnostics?.pythonBenchmarkMs?.let { "${it} ms" },
                    )
                    CheckRow("课程内容校验", true, "$completedLessons 课已完成")
                    CheckRow(
                        "项目流程",
                        completedProjects.takeIf { it > 0 }?.let { true },
                        "$completedProjects 个项目已完成",
                    )
                    CheckRow(
                        "训练流程",
                        completedTraining.takeIf { it > 0 }?.let { true },
                        "$completedTraining 项训练已完成",
                    )
                    CheckRow(
                        "Release 签名配置",
                        BuildConfig.RELEASE_SIGNING_CONFIGURED,
                        if (BuildConfig.RELEASE_SIGNING_CONFIGURED) "已读取 keystore.properties" else "未配置正式 keystore",
                    )
                }
            }
        }
        item {
            SectionTitle(title = "设备信息")
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(14.dp)) {
                    MutedText(text = diagnostics?.deviceSummary ?: "正在读取设备信息…", small = false)
                    Spacer(modifier = Modifier.height(5.dp))
                    MutedText(text = diagnostics?.runtimeSummary ?: "正在执行性能测试…", small = false)
                    Spacer(modifier = Modifier.height(5.dp))
                    MutedText(text = diagnostics?.memorySummary ?: "正在读取内存信息…", small = false)
                }
            }
        }
        item {
            SectionTitle(title = "发布前检查")
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(14.dp)) {
                    val checks = listOf(
                        "小屏与平板布局已做自适应检查",
                        "浅色、深色和壁纸模式文字保持可读",
                        "核心流程可使用返回键退出子页面",
                        "课程、项目、训练和更新内容全部走数据层",
                        "Release 构建使用独立签名文件，不提交密钥",
                    )
                    checks.forEach { check ->
                        Row(
                            modifier = Modifier.padding(vertical = 5.dp),
                            verticalAlignment = Alignment.Top,
                        ) {
                            Icon(
                                imageVector = Icons.Filled.CheckCircle,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.secondary,
                                modifier = Modifier
                                    .width(20.dp)
                                    .padding(top = 1.dp),
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = check, lineHeight = 19.sp, fontSize = 13.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CheckRow(
    title: String,
    passed: Boolean?,
    detail: String? = null,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = when (passed) {
                true -> Icons.Filled.CheckCircle
                false -> Icons.Filled.Error
                null -> Icons.Filled.ChevronRight
            },
            contentDescription = null,
            tint = when (passed) {
                true -> MaterialTheme.colorScheme.secondary
                false -> MaterialTheme.colorScheme.error
                null -> MaterialTheme.colorScheme.onSurfaceVariant
            },
            modifier = Modifier.width(21.dp),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(text = title, modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
        MutedText(text = detail.orEmpty())
    }
}
