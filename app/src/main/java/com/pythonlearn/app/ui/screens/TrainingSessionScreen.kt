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
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.TrainingCheckResult
import com.pythonlearn.app.data.TrainingExercise
import com.pythonlearn.app.data.TrainingGrader
import com.pythonlearn.app.runtime.PythonRunResult
import com.pythonlearn.app.runtime.PythonRunner
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.CodePanel
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.Tag
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun TrainingSessionScreen(
    exercises: List<TrainingExercise>,
    onBack: () -> Unit,
    onOpenWorkbench: (String) -> Unit,
    onResult: (exerciseId: String, correct: Boolean) -> Unit,
) {
    if (exercises.isEmpty()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Text(text = "暂时没有可训练的内容", fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "先完成一节课，再来这里做专项训练。",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(16.dp))
            Box(
                modifier = Modifier
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(13.dp))
                    .clickable(onClick = onBack)
                    .padding(horizontal = 18.dp, vertical = 11.dp),
            ) {
                Text(text = "返回", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
            }
        }
        return
    }

    var index by remember(exercises) { mutableStateOf(0) }
    var selectedOption by remember(exercises) { mutableStateOf<Int?>(null) }
    var codeInput by remember(exercises) {
        mutableStateOf(exercises.first().starterCode ?: exercises.first().code)
    }
    var checkedResult by remember(exercises) { mutableStateOf<TrainingCheckResult?>(null) }
    var showHints by remember(exercises) { mutableStateOf(false) }
    var showSolution by remember(exercises) { mutableStateOf(false) }
    var runResult by remember(exercises) { mutableStateOf<PythonRunResult?>(null) }
    var running by remember(exercises) { mutableStateOf(false) }
    var finished by remember(exercises) { mutableStateOf(false) }
    var solvedCount by remember(exercises) { mutableStateOf(0) }
    val creditedExercises = remember(exercises) { mutableStateOf<Set<String>>(emptySet()) }
    val scope = rememberCoroutineScope()

    val exercise = exercises[index]
    val isChoiceTask = !exercise.isCodeTask
    val selectedCorrectly = isChoiceTask && TrainingGrader.checkChoice(exercise, selectedOption)
    val taskReadyToContinue = if (isChoiceTask) selectedOption != null else checkedResult?.correct == true

    fun resetTask() {
        selectedOption = null
        codeInput = exercise.starterCode ?: exercise.code
        checkedResult = null
        showHints = false
        showSolution = false
        runResult = null
        running = false
    }

    fun record(correct: Boolean) {
        if (!correct || exercise.id !in creditedExercises.value) {
            onResult(exercise.id, correct)
        }
        if (correct && exercise.id !in creditedExercises.value) {
            creditedExercises.value = creditedExercises.value + exercise.id
            solvedCount += 1
        }
    }

    fun goNext() {
        if (index == exercises.lastIndex) {
            finished = true
        } else {
            index += 1
        }
    }

    if (finished) {
        TrainingFinished(
            solved = solvedCount,
            total = exercises.size,
            onBack = onBack,
        )
        return
    }

    LaunchedTaskReset(exercise) {
        resetTask()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 18.dp, end = 18.dp, bottom = 24.dp),
    ) {
        BackBar(title = exercise.type.label, onBack = onBack)
        Spacer(modifier = Modifier.height(8.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = exercise.title,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )
                MutedText(text = "训练 ${index + 1} / ${exercises.size}")
            }
            Tag(text = exercise.type.label, active = true)
        }
        Spacer(modifier = Modifier.height(10.dp))

        GlassCard {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = exercise.prompt,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 13.sp,
                    lineHeight = 19.sp,
                )
                Spacer(modifier = Modifier.height(10.dp))
                if (isChoiceTask) {
                    CodePanel(code = exercise.code)
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(text = exercise.question, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    exercise.options.forEachIndexed { optionIndex, option ->
                        val chosen = selectedOption == optionIndex
                        val isCorrect = optionIndex == exercise.answerIndex
                        val background = when {
                            chosen && isCorrect -> MaterialTheme.colorScheme.secondary.copy(alpha = 0.25f)
                            chosen && !isCorrect -> MaterialTheme.colorScheme.error.copy(alpha = 0.18f)
                            selectedOption != null && isCorrect -> MaterialTheme.colorScheme.secondary.copy(alpha = 0.16f)
                            else -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.75f)
                        }
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                                .background(background, RoundedCornerShape(12.dp))
                                .clickable(enabled = selectedOption == null) {
                                    selectedOption = optionIndex
                                    val correct = optionIndex == exercise.answerIndex
                                    record(correct)
                                }
                                .padding(horizontal = 13.dp, vertical = 11.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = "${'A' + optionIndex}",
                                modifier = Modifier.width(22.dp),
                                fontWeight = FontWeight.Bold,
                            )
                            Text(text = option)
                        }
                    }
                    if (selectedOption != null) {
                        Spacer(modifier = Modifier.height(9.dp))
                        Text(
                            text = if (selectedCorrectly) "回答正确。" else "这次还不对，看看下面的原因。",
                            color = if (selectedCorrectly) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error,
                            fontWeight = FontWeight.Bold,
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = exercise.explanation,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontSize = 13.sp,
                            lineHeight = 19.sp,
                        )
                        if (exercise.type == TrainingTypeForPrediction) {
                            Spacer(modifier = Modifier.height(10.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                RunCheckButton(
                                    running = running,
                                    onClick = {
                                        if (!running) {
                                            running = true
                                            runResult = null
                                            scope.launch {
                                                runResult = withContext(Dispatchers.IO) {
                                                    PythonRunner.run(exercise.code, exercise.stdin)
                                                }
                                                running = false
                                            }
                                        }
                                    },
                                )
                                Spacer(modifier = Modifier.width(9.dp))
                                MutedText(text = "运行只用于验证预测")
                            }
                        }
                    }
                } else {
                    CodePanel(code = exercise.code)
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(text = exercise.question, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(8.dp))
                    Surface(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(190.dp),
                        shape = RoundedCornerShape(14.dp),
                        color = Color(0xFF10151A),
                    ) {
                        BasicTextField(
                            value = codeInput,
                            onValueChange = {
                                codeInput = it
                                checkedResult = null
                            },
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(12.dp),
                            textStyle = TextStyle(
                                color = Color(0xFFDCE6ED),
                                fontFamily = FontFamily.Monospace,
                                fontSize = 13.sp,
                                lineHeight = 20.sp,
                            ),
                            cursorBrush = androidx.compose.ui.graphics.SolidColor(Color.White),
                        )
                    }
                    Spacer(modifier = Modifier.height(9.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        HintButton(
                            text = if (showHints) "收起提示" else "查看提示",
                            onClick = { showHints = !showHints },
                        )
                        Spacer(modifier = Modifier.weight(1f))
                        CheckCodeButton(
                            onClick = {
                                val result = TrainingGrader.checkCode(exercise, codeInput)
                                checkedResult = result
                                record(result.correct)
                            },
                        )
                    }
                    if (showHints) {
                        Spacer(modifier = Modifier.height(9.dp))
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(12.dp))
                                .padding(11.dp),
                        ) {
                            exercise.hints.forEachIndexed { hintIndex, hint ->
                                Text(
                                    text = "${hintIndex + 1}. $hint",
                                    fontSize = 12.sp,
                                    lineHeight = 18.sp,
                                )
                                if (hintIndex != exercise.hints.lastIndex) {
                                    Spacer(modifier = Modifier.height(4.dp))
                                }
                            }
                        }
                    }
                    checkedResult?.let { result ->
                        Spacer(modifier = Modifier.height(9.dp))
                        Text(
                            text = result.message,
                            color = if (result.correct) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error,
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp,
                        )
                        if (!result.correct && exercise.referenceSolution != null) {
                            Spacer(modifier = Modifier.height(7.dp))
                            HintButton(
                                text = if (showSolution) "隐藏参考实现" else "必要时查看参考实现",
                                onClick = { showSolution = !showSolution },
                            )
                        }
                    }
                    if (showSolution && exercise.referenceSolution != null) {
                        Spacer(modifier = Modifier.height(9.dp))
                        CodePanel(code = exercise.referenceSolution)
                    }
                    Spacer(modifier = Modifier.height(9.dp))
                    HintButton(
                        text = "在运行台继续编辑",
                        onClick = { onOpenWorkbench(codeInput) },
                    )
                }
            }
        }

        runResult?.let { result ->
            Spacer(modifier = Modifier.height(10.dp))
            RunOutput(result = result)
        }

        Spacer(modifier = Modifier.height(10.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    if (taskReadyToContinue) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                    RoundedCornerShape(14.dp),
                )
                .clickable(enabled = taskReadyToContinue, onClick = ::goNext)
                .padding(vertical = 13.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = if (taskReadyToContinue) {
                    if (index == exercises.lastIndex) "完成训练" else "下一题"
                } else if (isChoiceTask) {
                    "先选择一个答案"
                } else {
                    "先通过代码检查"
                },
                color = if (taskReadyToContinue) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun LaunchedTaskReset(
    exercise: TrainingExercise,
    reset: () -> Unit,
) {
    // Keep the reset hook visible at the call site: changing exercise must clear old input.
    androidx.compose.runtime.LaunchedEffect(exercise.id) {
        reset()
    }
}

private val TrainingTypeForPrediction = com.pythonlearn.app.data.TrainingType.PREDICT_OUTPUT

@Composable
private fun HintButton(
    text: String,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 11.dp, vertical = 8.dp),
    ) {
        Text(text = text, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun CheckCodeButton(onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(10.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 15.dp, vertical = 9.dp),
    ) {
        Text(
            text = "检查代码",
            color = MaterialTheme.colorScheme.onPrimary,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}

@Composable
private fun RunCheckButton(
    running: Boolean,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(
                if (running) MaterialTheme.colorScheme.surfaceVariant else Color(0xFF1C9D6B),
                RoundedCornerShape(10.dp),
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 13.dp, vertical = 8.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = Icons.Filled.PlayArrow,
                contentDescription = null,
                modifier = Modifier.height(15.dp).width(15.dp),
                tint = if (running) MaterialTheme.colorScheme.onSurfaceVariant else Color.White,
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = if (running) "运行中" else "运行验证",
                color = if (running) MaterialTheme.colorScheme.onSurfaceVariant else Color.White,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun RunOutput(result: PythonRunResult) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (result.ok) Color(0xFF0D1216) else Color(0xFF2A161A),
                RoundedCornerShape(14.dp),
            )
            .padding(13.dp),
    ) {
        Text(
            text = if (result.ok) "运行结果" else "运行错误",
            color = if (result.ok) Color(0xFFD7DFE5) else Color(0xFFFFC2C2),
            fontWeight = FontWeight.Bold,
        )
        Spacer(modifier = Modifier.height(6.dp))
        if (result.ok) {
            Text(
                text = result.lines.joinToString("\n").ifEmpty { "（没有输出内容）" },
                color = Color(0xFFD7DFE5),
                fontFamily = FontFamily.Monospace,
                fontSize = 13.sp,
            )
        } else {
            Text(
                text = "${result.errorType}: ${result.rawError}",
                color = Color(0xFFFFC2C2),
                fontFamily = FontFamily.Monospace,
                fontSize = 12.sp,
            )
            Spacer(modifier = Modifier.height(5.dp))
            Text(text = result.humanError, color = Color(0xFFFFD9D9), fontSize = 13.sp, lineHeight = 19.sp)
        }
    }
}

@Composable
private fun TrainingFinished(
    solved: Int,
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
            modifier = Modifier.height(54.dp).width(54.dp),
            tint = MaterialTheme.colorScheme.secondary,
        )
        Spacer(modifier = Modifier.height(10.dp))
        Text(text = "训练完成", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(5.dp))
        Text(text = "本次完成 $solved / $total 题", color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(16.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(14.dp))
                .clickable(onClick = onBack)
                .padding(vertical = 13.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(text = "返回训练中心", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
        }
    }
}
