package com.pythonlearn.app.ui.screens

import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.data.ErrorExample
import com.pythonlearn.app.data.LessonDetail
import com.pythonlearn.app.ui.components.CodePanel
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.ProgressTrack
import com.pythonlearn.app.ui.components.Tag

@Composable
fun LessonScreen(
    lesson: LessonDetail,
    onBack: () -> Unit,
    onOpenLesson: (String) -> Unit,
    onCompleteLesson: () -> Unit,
    legalRegionLabel: String,
    onOpenWorkbench: () -> Unit,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
) {
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            BackBar(title = "课程", onBack = onBack)
        }

        item {
            Column {
                MutedText(text = "${lesson.stage} · ${lesson.level}")
                Text(
                    text = lesson.title,
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    Tag(text = "⏱ ${lesson.minutes} 分钟")
                    Tag(text = lesson.legalRisk, active = true)
                }
                Spacer(modifier = Modifier.height(12.dp))
                ProgressTrack(progress = 72)
            }
        }

        item {
            LessonStep(number = "①", title = "知识讲解") {
                lesson.knowledge.forEach { paragraph ->
                    Paragraph(text = paragraph)
                }
                CodePanel(code = lesson.example)
                Spacer(modifier = Modifier.height(9.dp))
                lesson.exampleNotes.forEach { note ->
                    Row(modifier = Modifier.padding(vertical = 2.dp)) {
                        Text(
                            text = note.first,
                            modifier = Modifier.width(128.dp),
                            color = MaterialTheme.colorScheme.primary,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                        MutedText(text = note.second)
                    }
                }
            }
        }

        item {
            LessonStep(number = "②", title = "为什么需要它") {
                lesson.why.forEach { Paragraph(text = it) }
            }
        }

        item {
            LessonStep(number = "③", title = "它在真实项目中的用途") {
                Paragraph(text = lesson.purpose)
            }
        }

        item {
            LessonStep(number = "④", title = "Python 示例") {
                CodePanel(code = lesson.example)
            }
        }

        item {
            LessonStep(number = "⑤", title = "在线运行代码") {
                Paragraph(text = "直接运行本节示例，观察输出。运行台内置 Python 3.11，并把常见报错翻译成容易理解的提示。")
                Spacer(modifier = Modifier.height(8.dp))
                CodePanel(code = lesson.example)
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(14.dp))
                        .clickable(onClick = onOpenWorkbench)
                        .padding(vertical = 12.dp),
                    horizontalArrangement = Arrangement.Center,
                ) {
                    Text(text = "打开运行台运行本节代码", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
                }
            }
        }

        item {
            LessonStep(number = "⑥", title = "小练习") {
                PracticeQuiz(
                    lesson = lesson,
                    onRecordWrong = onRecordWrong,
                    onResolveWrong = onResolveWrong,
                )
            }
        }

        item {
            LessonStep(number = "⑦", title = "常见错误") {
                lesson.errors.forEach { error ->
                    ErrorBlock(error = error)
                }
            }
        }

        item {
            LessonStep(number = "⑧", title = "项目中的实际使用") {
                Paragraph(text = "它不会单独出现，而是会和其他知识一起组成真实程序。")
                CodePanel(code = lesson.projectCode)
            }
        }

        item {
            LessonStep(number = "⑨", title = "法律与合规") {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f), RoundedCornerShape(14.dp))
                        .padding(13.dp),
                ) {
                    Row {
                        Tag(text = lesson.legalRisk, active = true)
                        Spacer(modifier = Modifier.width(6.dp))
                        Tag(text = legalRegionLabel)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Paragraph(text = lesson.legalNote)
                    MutedText(text = "${lesson.legalBasis}\n更新时间：${lesson.legalUpdated}")
                }
            }
        }

        if (lesson.next.isNotEmpty()) {
            item {
                LessonStep(number = "⑩", title = "下一步学习") {
                    lesson.next.forEach { next ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable(enabled = CourseCatalog.lesson(next.id) != null) {
                                    onOpenLesson(next.id)
                                }
                                .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.8f), RoundedCornerShape(14.dp))
                                .padding(13.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(text = next.title, fontWeight = FontWeight.Bold)
                                MutedText(text = "进入下一节")
                            }
                            Icon(
                                imageVector = Icons.Filled.ChevronRight,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.width(20.dp),
                            )
                        }
                    }
                }
            }
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(14.dp))
                    .clickable(onClick = onCompleteLesson)
                    .padding(vertical = 14.dp),
                horizontalArrangement = Arrangement.Center,
            ) {
                Text(text = "完成本节", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun LessonStep(
    number: String,
    title: String,
    content: @Composable () -> Unit,
) {
    GlassCard {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = number,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            content()
        }
    }
}

@Composable
private fun Paragraph(text: String) {
    Text(
        text = text,
        modifier = Modifier.padding(bottom = 9.dp),
        color = MaterialTheme.colorScheme.onSurface,
        style = MaterialTheme.typography.bodyMedium,
        lineHeight = 22.sp,
    )
}

@Composable
private fun PracticeQuiz(
    lesson: LessonDetail,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
) {
    var selected by remember(lesson.id) { mutableStateOf<Int?>(null) }
    val answeredCorrectly = selected == lesson.quiz.answerIndex
    val answeredWrong = selected != null && !answeredCorrectly
    Column {
        Paragraph(text = lesson.quiz.question)
        CodePanel(code = lesson.quiz.code)
        Spacer(modifier = Modifier.height(10.dp))
        lesson.quiz.options.forEachIndexed { index, option ->
            val chosen = selected == index
            val isCorrect = index == lesson.quiz.answerIndex
            val background = when {
                chosen && isCorrect -> MaterialTheme.colorScheme.secondary.copy(alpha = 0.18f)
                chosen && !isCorrect -> Color(0xFFFFE2E2)
                isCorrect && selected != null -> MaterialTheme.colorScheme.secondary.copy(alpha = 0.18f)
                else -> MaterialTheme.colorScheme.surface.copy(alpha = 0.76f)
            }
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .background(background, RoundedCornerShape(13.dp))
                    .clickable(enabled = selected == null) {
                        selected = index
                        if (index == lesson.quiz.answerIndex) {
                            onResolveWrong(lesson.quiz.question)
                        } else {
                            onRecordWrong(lesson.quiz.question)
                        }
                    }
                    .padding(horizontal = 13.dp, vertical = 11.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = "${'A' + index}",
                    modifier = Modifier.width(22.dp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = FontWeight.Bold,
                )
                Text(text = option, color = MaterialTheme.colorScheme.onSurface)
            }
        }
        if (selected != null) {
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = if (answeredCorrectly) "回答正确。" else "还没有选对。",
                color = if (answeredCorrectly) {
                    MaterialTheme.colorScheme.secondary
                } else {
                    MaterialTheme.colorScheme.error
                },
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = lesson.quiz.explanation,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall,
                lineHeight = 18.sp,
            )
            if (answeredWrong) {
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    modifier = Modifier
                        .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(11.dp))
                        .clickable { selected = null }
                        .padding(horizontal = 13.dp, vertical = 7.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(text = "再试一次", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun ErrorBlock(error: ErrorExample) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.8f), RoundedCornerShape(14.dp))
            .padding(12.dp),
    ) {
        Row {
            Text(
                text = "!",
                color = MaterialTheme.colorScheme.error,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
            )
            Spacer(modifier = Modifier.width(9.dp))
            Column {
                Text(text = error.title, fontWeight = FontWeight.Bold)
                MutedText(text = error.detail)
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        CodePanel(code = error.code)
    }
}
