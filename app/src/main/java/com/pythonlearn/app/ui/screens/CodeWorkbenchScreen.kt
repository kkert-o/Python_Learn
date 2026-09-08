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
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.runtime.PythonRunResult
import com.pythonlearn.app.runtime.PythonRunner
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.MutedText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private val ifSample = CourseCatalog.lesson("if")?.example ?: ""
private val forSample = CourseCatalog.lesson("for")?.example ?: ""
private val errorSample = "score = 85\nif score >= 60:\n    print(socre)"

@Composable
fun CodeWorkbenchScreen(
    onBack: () -> Unit,
    initialCode: String? = null,
) {
    var code by remember(initialCode) { mutableStateOf(initialCode ?: ifSample) }
    var stdin by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<PythonRunResult?>(null) }
    var running by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 18.dp, end = 18.dp, bottom = 24.dp),
    ) {
        BackBar(title = "Python 运行台", onBack = onBack)

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ToolButton(text = "if 示例", onClick = { code = ifSample; result = null })
            ToolButton(text = "for 示例", onClick = { code = forSample; result = null })
            ToolButton(text = "错误示例", onClick = { code = errorSample; result = null })
        }

        Spacer(modifier = Modifier.height(10.dp))
        GlassCard {
            Column(modifier = Modifier.padding(12.dp)) {
                Row(modifier = Modifier.fillMaxWidth()) {
                    Text(text = "main.py", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
                    Text(text = "Python 3.11", color = MaterialTheme.colorScheme.primary)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(230.dp),
                    shape = RoundedCornerShape(14.dp),
                    color = Color(0xFF10151A),
                ) {
                    BasicTextField(
                        value = code,
                        onValueChange = {
                            code = it
                            result = null
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
                Spacer(modifier = Modifier.height(10.dp))
                Text(text = "输入", fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                Spacer(modifier = Modifier.height(6.dp))
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp),
                    shape = RoundedCornerShape(13.dp),
                    color = Color(0xFF20282E),
                ) {
                    BasicTextField(
                        value = stdin,
                        onValueChange = {
                            stdin = it
                            result = null
                        },
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                        textStyle = TextStyle(
                            color = Color(0xFFDCE6ED),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                        ),
                        cursorBrush = androidx.compose.ui.graphics.SolidColor(Color.White),
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Spacer(modifier = Modifier.weight(1f))
                    RunButton(
                        running = running,
                        onClick = {
                            if (!running) {
                                running = true
                                result = null
                                scope.launch {
                                    val run = withContext(Dispatchers.IO) {
                                        PythonRunner.run(code, stdin)
                                    }
                                    result = run
                                    running = false
                                }
                            }
                        },
                    )
                }
                if (running) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(
                            modifier = Modifier.height(14.dp).width(14.dp),
                            strokeWidth = 2.dp,
                            color = MaterialTheme.colorScheme.primary,
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "正在运行...",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        result?.let { run ->
            Spacer(modifier = Modifier.height(10.dp))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        if (run.ok) Color(0xFF0D1216) else Color(0xFF2A161A),
                        RoundedCornerShape(14.dp),
                    )
                    .padding(13.dp),
            ) {
                Row(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = if (run.ok) "运行结果" else "程序运行错误",
                        modifier = Modifier.weight(1f),
                        color = if (run.ok) Color(0xFFD7DFE5) else Color(0xFFFFC2C2),
                        fontWeight = FontWeight.Bold,
                    )
                    if (!run.ok) {
                        Text(text = run.errorType, color = Color(0xFFFF9D9D), fontSize = 12.sp)
                    }
                }
                Spacer(modifier = Modifier.height(6.dp))
                if (run.ok) {
                    Text(
                        text = run.lines.joinToString("\n").ifEmpty { "（程序没有输出内容）" },
                        color = Color(0xFFD7DFE5),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 13.sp,
                    )
                } else {
                    if (run.lines.isNotEmpty()) {
                        Text(
                            text = run.lines.joinToString("\n"),
                            color = Color(0xFFFFE2C2),
                            fontFamily = FontFamily.Monospace,
                            fontSize = 12.sp,
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                    }
                    Text(
                        text = "${run.errorType}: ${run.rawError}",
                        color = Color(0xFFFFC2C2),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 12.sp,
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = run.humanError, color = Color(0xFFFFD9D9), fontSize = 13.sp, lineHeight = 19.sp)
                }
            }
        }
    }
}

@Composable
private fun ToolButton(
    text: String,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(11.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 11.dp, vertical = 8.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text = text, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun RunButton(
    running: Boolean,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .background(
                if (running) MaterialTheme.colorScheme.surfaceVariant else Color(0xFF1C9D6B),
                RoundedCornerShape(11.dp),
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 18.dp, vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = Icons.Filled.PlayArrow,
                contentDescription = null,
                modifier = Modifier.height(16.dp).width(16.dp),
                tint = if (running) MaterialTheme.colorScheme.onSurfaceVariant else Color.White,
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = if (running) "运行中" else "运行",
                color = if (running) MaterialTheme.colorScheme.onSurfaceVariant else Color.White,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
