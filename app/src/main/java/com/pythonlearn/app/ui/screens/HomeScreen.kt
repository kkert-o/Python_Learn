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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.AutoStories
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.School
import androidx.compose.material.icons.filled.SmartToy
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.DemoStats
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.DailyLearningStats
import com.pythonlearn.app.data.LearningDashboard
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.IconAvatar
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.SectionTitle
import com.pythonlearn.app.ui.components.Tag

@Composable
fun HomeScreen(
    onOpenLesson: (String) -> Unit,
    onOpenAi: () -> Unit,
    onOpenLearningHub: () -> Unit,
    completedLessonIds: Set<String>,
    dashboard: LearningDashboard,
    dailyLearningStats: DailyLearningStats,
) {
    val completedCount = completedLessonIds.size
    val nextLessonId = remember(completedLessonIds) {
        CourseCatalog.nextLessonId(completedLessonIds)
    }
    val nextLesson = nextLessonId?.let { CourseCatalog.lesson(it) }
    val tasks = listOf(
        TaskRowData(
            title = "学习 15 分钟",
            subtitle = "今天已完成 ${dailyLearningStats.minutes} 分钟",
            done = dailyLearningStats.minutes >= 15,
        ),
        TaskRowData(
            title = "完成 4 道练习",
            subtitle = "今天已作答 ${dailyLearningStats.quizAnswers.coerceAtMost(4)} / 4 道",
            done = dailyLearningStats.quizAnswers >= 4,
        ),
        TaskRowData(
            title = "完成今日挑战",
            subtitle = "完成一次预测输出训练",
            done = dailyLearningStats.challengeCompleted,
        ),
    )
    val doneCount = tasks.count { it.done }

    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 18.dp, bottom = 18.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Column {
                Text(
                    text = "Python 学习",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = "你好，今天也继续",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        item {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(enabled = nextLesson != null) {
                        nextLessonId?.let(onOpenLesson)
                    },
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column {
                            Text(
                                text = if (completedCount == 0) DemoStats.pythonLevel else "Python Lv.${(completedCount / 3).coerceAtLeast(1) + 1}",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                            )
                            MutedText(
                                text = if (completedCount == 0) {
                                    "尚未获得经验"
                                } else {
                                    "已完成 $completedCount 个知识点"
                                },
                            )
                        }
                        Tag(
                            text = if (completedCount == 0) "未开始" else "学习中",
                            active = completedCount > 0,
                        )
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    ProgressTrack(progress = CourseCatalog.overallProgress(completedLessonIds))
                }
            }
        }

        item {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onOpenLearningHub),
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    IconAvatar(
                        imageVector = Icons.Filled.School,
                        contentDescription = "学习中心",
                        modifier = Modifier.width(46.dp),
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        MutedText(text = "知识树 · 复习 · 推荐")
                        Text(
                            text = dashboard.recommendation.title,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        MutedText(text = dashboard.recommendation.reason)
                    }
                    Tag(
                        text = if (dashboard.dueReviews.isEmpty()) "推荐" else "复习 ${dashboard.dueReviews.size}",
                        active = true,
                    )
                }
            }
        }

        item {
            GlassCard(
                modifier = if (nextLesson != null) {
                    Modifier
                        .fillMaxWidth()
                        .clickable { nextLessonId?.let(onOpenLesson) }
                } else {
                    Modifier.fillMaxWidth()
                },
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    IconAvatar(
                        imageVector = if (nextLesson == null) Icons.Filled.School else Icons.Filled.AutoStories,
                        contentDescription = if (nextLesson == null) "课程完成" else "课程",
                        modifier = Modifier.width(46.dp),
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        MutedText(
                            text = if (nextLesson == null) {
                                "当前已发布课程已学完"
                            } else if (completedCount == 0) {
                                "开始学习"
                            } else {
                                "继续学习"
                            },
                            small = false,
                        )
                        Text(
                            text = nextLesson?.title ?: "新课程正在准备中",
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.bodyLarge,
                        )
                        MutedText(
                            text = if (completedCount == 0) {
                                "从第一课开始建立 Python 知识体系"
                            } else if (nextLesson == null) {
                                "后续课程会在这里继续出现"
                            } else {
                                "继续下一个知识点"
                            },
                        )
                    }
                    if (nextLesson != null) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = "开始",
                            tint = MaterialTheme.colorScheme.primary,
                        )
                    }
                }
                ProgressTrack(
                    progress = CourseCatalog.overallProgress(completedLessonIds),
                    modifier = Modifier.padding(horizontal = 16.dp),
                )
                Spacer(modifier = Modifier.height(12.dp))
            }
        }

        item {
            SectionTitle(
                title = "今日学习",
                trailing = if (doneCount == tasks.size) "已完成" else "$doneCount / ${tasks.size}",
            )
        }

        item {
            GlassCard {
                Column {
                    tasks.forEach { task ->
                        val done = task.done
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 14.dp, vertical = 11.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(
                                imageVector = if (done) Icons.Filled.CheckCircle else Icons.Filled.RadioButtonUnchecked,
                                contentDescription = if (done) "已完成" else "未完成",
                                modifier = Modifier.width(24.dp),
                                tint = if (done) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Spacer(modifier = Modifier.width(9.dp))
                            Column {
                                Text(text = task.title, fontWeight = FontWeight.SemiBold)
                                MutedText(text = task.subtitle)
                            }
                        }
                    }
                }
            }
        }

        item {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(enabled = nextLesson != null) {
                        nextLessonId?.let(onOpenLesson)
                    },
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = Icons.Filled.LocalFireDepartment,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = if (dailyLearningStats.streakDays == 0) {
                                "从今天开始学习"
                            } else {
                                "连续学习 ${dailyLearningStats.streakDays} 天"
                            },
                            fontWeight = FontWeight.Bold,
                        )
                        MutedText(
                            text = if (dailyLearningStats.streakDays == 0) {
                                "完成第一个知识点后开始计算连续天数"
                            } else {
                                "本周已学习 ${dailyLearningStats.weekDays} 天"
                            },
                        )
                    }
                    Tag(text = "本周 ${dailyLearningStats.weekDays}/7", active = true)
                }
            }
        }

        item {
            GlassCard(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onOpenAi),
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    IconAvatar(
                        imageVector = Icons.Filled.SmartToy,
                        contentDescription = "AI 老师",
                        modifier = Modifier.width(46.dp),
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "AI Python 老师", fontWeight = FontWeight.Bold)
                        MutedText(text = "老师模式已开启")
                    }
                    Tag(text = "老师模式已开启", active = true)
                }
            }
        }
    }
}

private data class TaskRowData(
    val title: String,
    val subtitle: String,
    val done: Boolean,
)
