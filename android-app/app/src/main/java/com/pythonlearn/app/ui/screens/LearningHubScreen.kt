package com.pythonlearn.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.HourglassBottom
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.KnowledgeNode
import com.pythonlearn.app.data.KnowledgeState
import com.pythonlearn.app.data.LearningDashboard
import com.pythonlearn.app.data.ReviewItem
import com.pythonlearn.app.data.ReviewTargetType
import com.pythonlearn.app.data.TrainingCatalog
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.SectionTitle
import com.pythonlearn.app.ui.components.Tag

@Composable
fun LearningHubScreen(
    dashboard: LearningDashboard,
    onBack: () -> Unit,
    onOpenLesson: (String) -> Unit,
    onOpenReview: (ReviewItem) -> Unit,
) {
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            BackBar(title = "学习中心", onBack = onBack)
        }
        item {
            RecommendationCard(
                dashboard = dashboard,
                onOpenLesson = onOpenLesson,
                onOpenReview = onOpenReview,
            )
        }
        item {
            SectionTitle(
                title = "到期复习",
                trailing = if (dashboard.dueReviews.isEmpty()) "已清空" else "${dashboard.dueReviews.size} 项",
            )
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(12.dp)) {
                    if (dashboard.dueReviews.isEmpty()) {
                        Row(
                            modifier = Modifier.padding(6.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                imageVector = Icons.Filled.CheckCircle,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.secondary,
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(text = "当前没有到期内容", fontWeight = FontWeight.Bold)
                                MutedText(text = "复习会按 1、3、7、14、30 天自动排队。")
                            }
                        }
                    } else {
                        dashboard.dueReviews.forEachIndexed { index, item ->
                            ReviewRow(
                                item = item,
                                onClick = { onOpenReview(item) },
                            )
                            if (index != dashboard.dueReviews.lastIndex) {
                                Spacer(modifier = Modifier.height(6.dp))
                            }
                        }
                    }
                }
            }
        }
        item {
            SectionTitle(
                title = "知识树",
                trailing = "掌握度会随练习更新",
            )
        }
        dashboard.knowledgeTree
            .groupBy { it.stage }
            .forEach { (stage, nodes) ->
                item {
                    GlassCard {
                        Column(modifier = Modifier.padding(14.dp)) {
                            Text(text = stage, fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(8.dp))
                            nodes.forEach { node ->
                                KnowledgeNodeRow(
                                    node = node,
                                    onClick = { onOpenLesson(node.lessonId) },
                                )
                            }
                        }
                    }
                }
            }
    }
}

@Composable
private fun RecommendationCard(
    dashboard: LearningDashboard,
    onOpenLesson: (String) -> Unit,
    onOpenReview: (ReviewItem) -> Unit,
) {
    val recommendation = dashboard.recommendation
    GlassCard {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(12.dp))
                        .padding(10.dp),
                ) {
                    Icon(
                        imageVector = Icons.Filled.PlayCircle,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    MutedText(text = "下一步推荐")
                    Text(
                        text = recommendation.title,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                    )
                    MutedText(text = recommendation.reason, small = false)
                }
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(12.dp))
                    .clickable {
                        val review = dashboard.dueReviews.firstOrNull {
                            it.targetKey == recommendation.reviewTargetKey
                        }
                        when {
                            review != null -> onOpenReview(review)
                            recommendation.lessonId != null -> onOpenLesson(recommendation.lessonId)
                        }
                    }
                    .padding(vertical = 11.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (recommendation.reviewTargetKey != null) "开始复习" else "继续学习",
                    color = MaterialTheme.colorScheme.onPrimary,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

@Composable
private fun ReviewRow(
    item: ReviewItem,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Filled.Refresh,
            contentDescription = null,
            tint = if (item.overdueDays > 0) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary,
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(text = item.title, fontWeight = FontWeight.SemiBold)
            MutedText(
                text = when {
                    item.overdueDays > 0 -> "已逾期 ${item.overdueDays} 天"
                    item.targetType == ReviewTargetType.LESSON -> "课程复习"
                    item.targetType == ReviewTargetType.TRAINING -> "专项训练复习"
                    else -> "错题复习"
                },
            )
        }
        Tag(
            text = when (item.targetType) {
                ReviewTargetType.LESSON -> "课程"
                ReviewTargetType.TRAINING -> "训练"
                ReviewTargetType.QUIZ -> "错题"
            },
            active = item.priority >= 5,
        )
    }
}

@Composable
private fun KnowledgeNodeRow(
    node: KnowledgeNode,
    onClick: () -> Unit,
) {
    val openable = node.state != KnowledgeState.LOCKED
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = openable, onClick = onClick)
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = when (node.state) {
                KnowledgeState.MASTERED,
                KnowledgeState.COMPLETED,
                -> Icons.Filled.CheckCircle

                KnowledgeState.LEARNING -> Icons.Filled.PlayCircle
                KnowledgeState.NEEDS_REVIEW -> Icons.Filled.HourglassBottom
                KnowledgeState.LOCKED -> Icons.Filled.Lock
                KnowledgeState.NOT_STARTED -> Icons.Filled.RadioButtonUnchecked
            },
            contentDescription = null,
            modifier = Modifier.width(23.dp),
            tint = when (node.state) {
                KnowledgeState.MASTERED -> MaterialTheme.colorScheme.secondary
                KnowledgeState.COMPLETED -> MaterialTheme.colorScheme.primary
                KnowledgeState.LEARNING -> MaterialTheme.colorScheme.tertiary
                KnowledgeState.NEEDS_REVIEW -> MaterialTheme.colorScheme.error
                KnowledgeState.LOCKED -> MaterialTheme.colorScheme.onSurfaceVariant
                KnowledgeState.NOT_STARTED -> MaterialTheme.colorScheme.onSurfaceVariant
            },
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = node.title,
                    modifier = Modifier.weight(1f),
                    fontWeight = FontWeight.SemiBold,
                    color = if (openable) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = "${node.masteryScore}%",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            ProgressTrack(progress = node.masteryScore)
            Spacer(modifier = Modifier.height(4.dp))
            MutedText(text = knowledgeStateLabel(node.state))
        }
    }
}

private fun knowledgeStateLabel(state: KnowledgeState): String = when (state) {
    KnowledgeState.NOT_STARTED -> "未学习"
    KnowledgeState.LEARNING -> "学习中"
    KnowledgeState.COMPLETED -> "已完成"
    KnowledgeState.MASTERED -> "熟练"
    KnowledgeState.NEEDS_REVIEW -> "需要复习"
    KnowledgeState.LOCKED -> "未解锁"
}

fun ReviewItem.toWorkbenchCode(): String? = when (targetType) {
    ReviewTargetType.TRAINING -> TrainingCatalog.byId(targetId)?.code
    ReviewTargetType.QUIZ -> CourseCatalog.quizByQuestion(targetId)?.code
    ReviewTargetType.LESSON -> null
}
