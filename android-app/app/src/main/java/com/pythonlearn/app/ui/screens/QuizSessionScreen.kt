package com.pythonlearn.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Icon
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
import com.pythonlearn.app.data.Quiz
import com.pythonlearn.app.ui.components.CodePanel
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.Tag

@Composable
fun QuizSessionScreen(
    quizzes: List<Quiz>,
    onBack: () -> Unit,
    onRecordWrong: (String) -> Unit,
    onResolveWrong: (String) -> Unit,
) {
    var index by remember { mutableStateOf(0) }
    var selected by remember { mutableStateOf<Int?>(null) }
    var correctCount by remember { mutableStateOf(0) }

    if (index >= quizzes.size) {
        FinishedQuiz(correct = correctCount, total = quizzes.size, onBack = onBack)
        return
    }
    val quiz = quizzes[index]

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 22.dp),
    ) {
        BackBar(title = "退出练习", onBack = onBack)
        Spacer(modifier = Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = "练习 ${index + 1} / ${quizzes.size}",
                modifier = Modifier.weight(1f),
                fontWeight = FontWeight.Bold,
            )
            Tag(text = "已答对 $correctCount", active = true)
        }
        Spacer(modifier = Modifier.height(10.dp))
        GlassCard {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(text = quiz.question, fontWeight = FontWeight.SemiBold, lineHeight = 21.sp)
                Spacer(modifier = Modifier.height(9.dp))
                CodePanel(code = quiz.code)
                Spacer(modifier = Modifier.height(10.dp))
                quiz.options.forEachIndexed { optionIndex, option ->
                    val chosen = selected == optionIndex
                    val correct = optionIndex == quiz.answerIndex
                    val background = when {
                        chosen && correct -> Color(0xFF1C9D6B)
                        chosen && !correct -> Color(0xFFE35B5B)
                        correct && selected != null -> Color(0xFF1C9D6B).copy(alpha = 0.35f)
                        else -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.75f)
                    }
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                            .background(background, RoundedCornerShape(12.dp))
                            .clickable(enabled = selected == null) { selected = optionIndex }
                            .padding(horizontal = 13.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = (('A'.code + optionIndex).toChar()).toString(),
                            modifier = Modifier.width(22.dp),
                            color = if (chosen || (correct && selected != null)) Color.White else MaterialTheme.colorScheme.onSurface,
                            fontWeight = FontWeight.Bold,
                        )
                        Text(
                            text = option,
                            color = if (chosen || (correct && selected != null)) Color.White else MaterialTheme.colorScheme.onSurface,
                        )
                    }
                }
                if (selected != null) {
                    Spacer(modifier = Modifier.height(9.dp))
                    val isCorrect = selected == quiz.answerIndex
                    Text(
                        text = if (isCorrect) "回答正确。" else "还没有选对。",
                        color = if (isCorrect) Color(0xFF1C9D6B) else MaterialTheme.colorScheme.error,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = quiz.explanation,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = 13.sp,
                        lineHeight = 19.sp,
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(13.dp))
                            .clickable {
                                if (isCorrect) {
                                    correctCount += 1
                                    onResolveWrong(quiz.question)
                                } else {
                                    onRecordWrong(quiz.question)
                                }
                                index += 1
                                selected = null
                            }
                            .padding(vertical = 12.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = if (index == quizzes.lastIndex) "完成练习" else "下一题",
                            color = MaterialTheme.colorScheme.onPrimary,
                            fontWeight = FontWeight.Bold,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FinishedQuiz(
    correct: Int,
    total: Int,
    onBack: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            imageVector = Icons.Filled.CheckCircle,
            contentDescription = null,
            modifier = Modifier.width(52.dp).height(52.dp),
            tint = Color(0xFF1C9D6B),
        )
        Spacer(modifier = Modifier.height(10.dp))
        Text(text = "今日练习完成", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(5.dp))
        Text(text = "答对 $correct / $total", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(16.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(14.dp))
                .clickable(onClick = onBack)
                .padding(vertical = 13.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(text = "返回练习", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
        }
    }
}
