package com.pythonlearn.app.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.graphics.Color
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ManageSearch
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.BugReport
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.School
import androidx.compose.material3.Icon
import androidx.compose.foundation.background
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.Quiz
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.data.TrainingExercise
import com.pythonlearn.app.data.TrainingType
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.SectionTitle
import com.pythonlearn.app.ui.components.Tag

@Composable
fun PracticeScreen(
    onOpenWorkbench: (String?) -> Unit,
    wrongQuizIds: Set<String>,
    completedTrainingIds: Set<String>,
    wrongTrainingIds: Set<String>,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
    onTrainingResult: (exerciseId: String, correct: Boolean) -> Unit,
    dueReviewCount: Int,
    onOpenLearningHub: () -> Unit,
    onOpenErrorMuseum: () -> Unit,
    onOpenSearch: () -> Unit,
) {
    var showQuiz by remember { mutableStateOf(false) }
    var trainingExercises by remember { mutableStateOf<List<TrainingExercise>?>(null) }
    var reviewQuestion by remember { mutableStateOf<String?>(null) }
    var reviewSession by remember { mutableStateOf<List<Quiz>?>(null) }
    BackHandler(
        enabled = reviewSession != null ||
            trainingExercises != null ||
            reviewQuestion != null ||
            showQuiz,
    ) {
        when {
            reviewSession != null -> reviewSession = null
            trainingExercises != null -> trainingExercises = null
            reviewQuestion != null -> reviewQuestion = null
            showQuiz -> showQuiz = false
        }
    }
    val quizzes = remember {
        listOfNotNull(
            CourseCatalog.lesson("if")?.quiz,
            CourseCatalog.lesson("for")?.quiz,
            Quiz(
                question = "运行下面的代码，输出是什么？",
                code = "name = \"小林\"\nage = 18\nprint(name, \"今年\", age, \"岁\")",
                options = listOf("小林 今年 18 岁", "name 今年 age 岁", "会报错", "小林 18"),
                answerIndex = 0,
                explanation = "print 会把逗号分隔的内容按顺序输出，并用一个空格分隔。",
            ),
            Quiz(
                question = "下面程序运行时会发生什么？",
                code = "score = 85\nif score >= 60:\n    print(socre)",
                options = listOf("NameError", "SyntaxError", "正常运行", "ValueError"),
                answerIndex = 0,
                explanation = "score 与 socre 拼写不一致，Python 找不到 socre 这个名称，所以抛 NameError。",
            ),
        )
    }
    val reviewQuiz = reviewQuestion?.let { question ->
        CourseCatalog.quizByQuestion(question) ?: quizzes.firstOrNull { it.question == question }
    }
    if (reviewSession != null) {
        QuizSessionScreen(
            quizzes = reviewSession.orEmpty(),
            onBack = {
                reviewSession = null
                showQuiz = false
            },
            onRecordWrong = onRecordWrong,
            onResolveWrong = onResolveWrong,
        )
        return
    }
    if (trainingExercises != null) {
        TrainingSessionScreen(
            exercises = trainingExercises.orEmpty(),
            onBack = { trainingExercises = null },
            onOpenWorkbench = { code -> onOpenWorkbench(code) },
            onResult = onTrainingResult,
        )
        return
    }
    if (reviewQuiz != null) {
        QuizSessionScreen(
            quizzes = listOf(reviewQuiz),
            onBack = {
                reviewQuestion = null
                showQuiz = false
            },
            onRecordWrong = onRecordWrong,
            onResolveWrong = onResolveWrong,
        )
        return
    }
    if (showQuiz && quizzes.isNotEmpty()) {
        QuizSessionScreen(
            quizzes = quizzes,
            onBack = { showQuiz = false },
            onRecordWrong = onRecordWrong,
            onResolveWrong = onResolveWrong,
        )
        return
    }
    val exercises = listOf(
        "变量与输出" to "基础",
        "条件判断" to "程序控制",
        "for 循环" to "程序控制",
        "找错误" to "综合",
    )
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 18.dp, bottom = 18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column {
                MutedText(text = "4 道题 · 预计 10 分钟")
                Text(
                    text = "练习",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = "今日练习", fontWeight = FontWeight.Bold)
                            MutedText(text = "4 道题 · 即时判题")
                        }
                        Tag(text = "待开始", active = true)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    exercises.forEach { exercise ->
                        Row(modifier = Modifier.padding(vertical = 6.dp)) {
                            Icon(
                                imageVector = Icons.Filled.RadioButtonUnchecked,
                                contentDescription = null,
                                modifier = Modifier.width(24.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Text(text = exercise.first, modifier = Modifier.weight(1f))
                            Tag(text = exercise.second)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(12.dp))
                            .clickable { showQuiz = true }
                            .padding(vertical = 10.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(text = "开始今日练习", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
        item {
            GlassCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onOpenWorkbench(null) }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = Icons.Filled.Code,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Python 运行台", fontWeight = FontWeight.Bold)
                        MutedText(text = "用手机内置 Python 3.11 运行代码")
                    }
                    Icon(
                        imageVector = Icons.Filled.ChevronRight,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                }
            }
        }
        item {
            SectionTitle(
                title = "学习工具",
                trailing = if (dueReviewCount == 0) "今日复习已清空" else "$dueReviewCount 项到期",
            )
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(10.dp)) {
                    ToolEntryRow(
                        title = "知识树与复习队列",
                        subtitle = "查看掌握度、到期复习和下一步推荐",
                        icon = Icons.Filled.School,
                        onClick = onOpenLearningHub,
                    )
                    ToolEntryRow(
                        title = "错误博物馆",
                        subtitle = "按错误类型查找原因、修复方式和预防方法",
                        icon = Icons.Filled.BugReport,
                        onClick = onOpenErrorMuseum,
                    )
                    ToolEntryRow(
                        title = "全局搜索与收藏",
                        subtitle = "搜索课程、项目、训练、第三方库和工程实践",
                        icon = Icons.AutoMirrored.Filled.ManageSearch,
                        onClick = onOpenSearch,
                    )
                }
            }
        }
        item {
            SectionTitle(
                title = "能力训练",
                trailing = "已完成 ${completedTrainingIds.size}/${TrainingCatalog.all.size}",
            )
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(10.dp)) {
                    TrainingType.entries.forEach { type ->
                        val allForType = remember(type) { TrainingCatalog.byType(type) }
                        val completedForType = allForType.count { it.id in completedTrainingIds }
                        TrainingTypeRow(
                            type = type,
                            completed = completedForType,
                            total = allForType.size,
                            onClick = { trainingExercises = allForType },
                        )
                    }
                }
            }
        }
        if (wrongTrainingIds.isNotEmpty()) {
            item {
                SectionTitle(title = "训练错题", trailing = "${wrongTrainingIds.size} 条待复习")
            }
            item {
                GlassCard {
                    Column(modifier = Modifier.padding(14.dp)) {
                        MutedText(
                            text = "这些是刚才没有通过检查的训练题，重新完成一次就会移出。",
                            small = false,
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(12.dp))
                                .clickable {
                                    trainingExercises = TrainingCatalog.byIds(wrongTrainingIds)
                                }
                                .padding(vertical = 10.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                text = "复习全部训练错题",
                                color = MaterialTheme.colorScheme.onPrimary,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                    }
                }
            }
        }
        item {
            SectionTitle(title = "错题本", trailing = "${wrongQuizIds.size} 条待复习")
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    if (wrongQuizIds.isEmpty()) {
                        MutedText(text = "完成练习后，做错的题会自动出现在这里。", small = false)
                    } else {
                        val reviewableWrong = wrongQuizIds.mapNotNull { question ->
                            CourseCatalog.quizByQuestion(question) ?: quizzes.firstOrNull { it.question == question }
                        }
                        wrongQuizIds.take(8).forEach { question ->
                            val canReview = reviewableWrong.any { it.question == question }
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable(enabled = canReview) { reviewQuestion = question }
                                    .padding(vertical = 10.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Text(text = "!", color = MaterialTheme.colorScheme.error, fontWeight = FontWeight.Bold)
                                Spacer(modifier = Modifier.width(9.dp))
                                Text(text = question.take(28), modifier = Modifier.weight(1f))
                                Text(
                                    text = if (canReview) "复习" else "待复习",
                                    color = if (canReview) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontWeight = FontWeight.Bold,
                                )
                            }
                            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.25f))
                        }
                        if (reviewableWrong.size > 1) {
                            Spacer(modifier = Modifier.height(6.dp))
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(12.dp))
                                    .clickable {
                                        reviewSession = reviewableWrong
                                    }
                                    .padding(vertical = 10.dp),
                                contentAlignment = Alignment.Center,
                            ) {
                                Text(text = "复习全部 ${reviewableWrong.size} 道错题", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ToolEntryRow(
    title: String,
    subtitle: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 6.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.width(24.dp),
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(text = title, fontWeight = FontWeight.Bold)
            MutedText(text = subtitle)
        }
        Icon(
            imageVector = Icons.Filled.ChevronRight,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun TrainingTypeRow(
    type: TrainingType,
    completed: Int,
    total: Int,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 6.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = type.label, fontWeight = FontWeight.Bold)
            MutedText(text = type.description)
        }
        Tag(text = "$completed/$total", active = completed == total)
        Spacer(modifier = Modifier.width(7.dp))
        Icon(
            imageVector = Icons.Filled.ChevronRight,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
        )
    }
}

@Composable
fun ProjectScreen(
    onOpenLesson: (String) -> Unit,
    onOpenWorkbench: (String) -> Unit,
    completedProjectIds: Set<String>,
    onCompleteProject: (String) -> Unit,
) {
    var openProjectId by remember { mutableStateOf<String?>(null) }
    BackHandler(enabled = openProjectId != null) {
        openProjectId = null
    }
    val openProject = openProjectId?.let(ProjectCatalog::byId)
    if (openProject != null) {
        ProjectDetailScreen(
            project = openProject,
            onBack = { openProjectId = null },
            onOpenWorkbench = { onOpenWorkbench(openProject.starter) },
            completed = openProject.id in completedProjectIds,
            onComplete = {
                onCompleteProject(openProject.id)
                openProjectId = null
            },
        )
        return
    }
    val rows = ProjectCatalog.all.map { project ->
        ProjectRowData(
            level = project.level,
            id = project.id,
            subtitle = project.goal,
        )
    }
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 18.dp, bottom = 18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column {
                MutedText(text = "从需求出发，不直接给完整答案")
                Text(
                    text = "项目实战",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
        item {
            MutedText(
                text = "每个项目只给需求和提示，先在运行台写出结构，再逐步补逻辑。",
                small = false,
            )
        }
        rows.groupBy { it.level }.forEach { (level, grouped) ->
            item {
                SectionTitle(title = level)
            }
            item {
                GlassCard {
                    Column(modifier = Modifier.padding(12.dp)) {
                        grouped.forEach { row ->
                            val project = ProjectCatalog.byId(row.id)
                            if (project != null) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable { openProjectId = project.id }
                                        .background(
                                            if (project.id in completedProjectIds) {
                                                MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f)
                                            } else {
                                                MaterialTheme.colorScheme.surface.copy(alpha = 0.7f)
                                            },
                                            RoundedCornerShape(13.dp),
                                        )
                                        .padding(horizontal = 12.dp, vertical = 11.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                ) {
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(text = project.title, fontWeight = FontWeight.Bold)
                                        Text(
                                            text = row.subtitle,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                                            style = MaterialTheme.typography.bodySmall,
                                            maxLines = 2,
                                            overflow = TextOverflow.Ellipsis,
                                        )
                                    }
                                    Tag(
                                        text = if (project.id in completedProjectIds) "已完成" else "开始",
                                        active = project.id in completedProjectIds,
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private data class ProjectRowData(
    val level: String,
    val id: String,
    val subtitle: String,
)
