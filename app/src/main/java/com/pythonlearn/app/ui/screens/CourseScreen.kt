package com.pythonlearn.app.ui.screens

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
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material3.Icon
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.CourseStage
import com.pythonlearn.app.data.LessonState
import com.pythonlearn.app.data.LessonSummary
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.Tag

@Composable
fun CourseScreen(
    onOpenLesson: (String) -> Unit,
    completedLessonIds: Set<String>,
    onOpenLearningHub: () -> Unit,
) {
    var expandedIds by remember {
        mutableStateOf(setOf(CourseCatalog.stages[0].name))
    }

    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 18.dp, bottom = 18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column {
                Text(
                    text = "从看懂代码到独立完成项目",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "课程",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        item {
            GlassCard {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Python 学习路线", fontWeight = FontWeight.Bold)
                        MutedText(
                            text = if (completedLessonIds.isEmpty()) {
                                "${CourseCatalog.stages.size} 个阶段 · 尚未开始"
                            } else {
                                "已完成 ${completedLessonIds.size} 个知识点"
                            },
                        )
                    }
                    Text(
                        text = "${CourseCatalog.overallProgress(completedLessonIds)}%",
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp,
                    )
                }
                ProgressTrack(
                    progress = CourseCatalog.overallProgress(completedLessonIds),
                    modifier = Modifier.padding(horizontal = 16.dp),
                )
                Spacer(modifier = Modifier.height(12.dp))
            }
        }

        item {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onOpenLearningHub),
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "查看知识树与掌握度", fontWeight = FontWeight.Bold)
                        MutedText(text = "按知识点查看状态、到期复习和下一步推荐")
                    }
                    Icon(
                        imageVector = Icons.Filled.ChevronRight,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                }
            }
        }

        itemsIndexed(CourseCatalog.stages) { _, stage ->
            CourseStageCard(
                stage = stage,
                expanded = stage.name in expandedIds,
                onToggle = {
                    expandedIds = if (stage.name in expandedIds) {
                        expandedIds - stage.name
                    } else {
                        expandedIds + stage.name
                    }
                },
                onOpenLesson = onOpenLesson,
                completedLessonIds = completedLessonIds,
            )
        }
    }
}

@Composable
private fun CourseStageCard(
    stage: CourseStage,
    expanded: Boolean,
    onToggle: () -> Unit,
    onOpenLesson: (String) -> Unit,
    completedLessonIds: Set<String>,
) {
    GlassCard {
        Column {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onToggle)
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = stage.label,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(text = stage.name, fontWeight = FontWeight.Bold)
                    val stageProgress = CourseCatalog.stageProgress(stage, completedLessonIds)
                    MutedText(
                        text = if (stageProgress == 0) {
                            "尚未开始 · ${stage.lessons.size} 个知识点"
                        } else {
                            "$stageProgress% · ${stage.lessons.size} 个知识点"
                        },
                    )
                }
                if (stage.special) {
                    Tag(text = "安全与合规", active = true)
                    Spacer(modifier = Modifier.width(8.dp))
                }
                Icon(
                    imageVector = if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                    contentDescription = if (expanded) "收起" else "展开",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            if (expanded) {
                HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                stage.lessons.forEach { lesson ->
                    LessonRow(
                        lesson = lesson,
                        computedState = CourseCatalog.lessonState(lesson.id, completedLessonIds),
                        onClick = { onOpenLesson(lesson.id) },
                    )
                }
            }
        }
    }
}

@Composable
private fun LessonRow(
    lesson: LessonSummary,
    computedState: LessonState,
    onClick: () -> Unit,
) {
    val openable = CourseCatalog.lesson(lesson.id) != null && computedState != LessonState.LOCKED
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = openable, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = when (computedState) {
                LessonState.DONE -> Icons.Filled.CheckCircle
                LessonState.DOING -> Icons.Filled.CheckCircle
                LessonState.TODO -> Icons.Filled.RadioButtonUnchecked
                LessonState.LOCKED -> Icons.Filled.Lock
            },
            contentDescription = when (computedState) {
                LessonState.DONE -> "已完成"
                LessonState.DOING -> "学习中"
                LessonState.TODO -> "待学习"
                LessonState.LOCKED -> "未解锁"
            },
            modifier = Modifier.width(24.dp),
            tint = when (computedState) {
                LessonState.DONE -> MaterialTheme.colorScheme.secondary
                LessonState.DOING -> MaterialTheme.colorScheme.primary
                LessonState.TODO -> MaterialTheme.colorScheme.onSurfaceVariant
                LessonState.LOCKED -> MaterialTheme.colorScheme.outline
            },
        )
        Spacer(modifier = Modifier.width(8.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = lesson.title,
                fontWeight = if (computedState == LessonState.LOCKED) FontWeight.Normal else FontWeight.SemiBold,
                color = if (computedState == LessonState.LOCKED) {
                    MaterialTheme.colorScheme.onSurfaceVariant
                } else {
                    MaterialTheme.colorScheme.onSurface
                },
            )
            MutedText(text = "${lesson.minutes} 分钟${stateText(computedState)}")
        }
        if (openable) {
            Icon(
                imageVector = Icons.Filled.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.width(20.dp),
            )
        }
    }
}

private fun stateText(state: LessonState): String = when (state) {
    LessonState.DONE -> " · 已完成"
    LessonState.DOING -> " · 学习中"
    LessonState.TODO -> ""
    LessonState.LOCKED -> ""
}
