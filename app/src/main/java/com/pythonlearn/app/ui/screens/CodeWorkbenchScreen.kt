package com.pythonlearn.app.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.FormatAlignLeft
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.TextIncrease
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.OffsetMapping
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.input.TransformedText
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.CourseCatalog
import com.pythonlearn.app.runtime.PythonRunResult
import com.pythonlearn.app.runtime.PythonRunner
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private val ifSample = CourseCatalog.lesson("if")?.example ?: ""
private val forSample = CourseCatalog.lesson("for")?.example ?: ""
private val errorSample = "score = 85\nif score >= 60:\n    print(socre)"

private data class CodeTheme(
    val id: String,
    val label: String,
    val background: Color,
    val selection: Color,
    val text: Color,
    val keyword: Color,
    val string: Color,
    val number: Color,
    val comment: Color,
    val function: Color,
    val type: Color,
    val error: Color,
)

private val codeThemes = listOf(
    CodeTheme(
        id = "dark",
        label = "Dark",
        background = Color(0xFF10151A),
        selection = Color(0xFF28526B),
        text = Color(0xFFDCE6ED),
        keyword = Color(0xFFFF7B72),
        string = Color(0xFFA5D6FF),
        number = Color(0xFFD2A8FF),
        comment = Color(0xFF8B949E),
        function = Color(0xFFD2A8FF),
        type = Color(0xFF7EE787),
        error = Color(0xFFFFA198),
    ),
    CodeTheme(
        id = "light",
        label = "Light",
        background = Color(0xFFF7F8FA),
        selection = Color(0xFFB6D7FF),
        text = Color(0xFF24292F),
        keyword = Color(0xFFCF222E),
        string = Color(0xFF0A3069),
        number = Color(0xFF0550AE),
        comment = Color(0xFF6E7781),
        function = Color(0xFF8250DF),
        type = Color(0xFF116329),
        error = Color(0xFFCF222E),
    ),
    CodeTheme(
        id = "dracula",
        label = "Dracula",
        background = Color(0xFF282A36),
        selection = Color(0xFF44475A),
        text = Color(0xFFF8F8F2),
        keyword = Color(0xFFFF79C6),
        string = Color(0xFFF1FA8C),
        number = Color(0xFFBD93F9),
        comment = Color(0xFF6272A4),
        function = Color(0xFF50FA7B),
        type = Color(0xFF8BE9FD),
        error = Color(0xFFFF5555),
    ),
    CodeTheme(
        id = "monokai",
        label = "Monokai",
        background = Color(0xFF272822),
        selection = Color(0xFF49483E),
        text = Color(0xFFF8F8F2),
        keyword = Color(0xFFF92672),
        string = Color(0xFFE6DB74),
        number = Color(0xFFAE81FF),
        comment = Color(0xFF75715E),
        function = Color(0xFFA6E22E),
        type = Color(0xFF66D9EF),
        error = Color(0xFFF92672),
    ),
    CodeTheme(
        id = "github",
        label = "GitHub",
        background = Color(0xFF0D1117),
        selection = Color(0xFF1F3A5F),
        text = Color(0xFFC9D1D9),
        keyword = Color(0xFFFF7B72),
        string = Color(0xFFA5D6FF),
        number = Color(0xFFD2A8FF),
        comment = Color(0xFF8B949E),
        function = Color(0xFFD2A8FF),
        type = Color(0xFF7EE787),
        error = Color(0xFFFFA198),
    ),
    CodeTheme(
        id = "solarized",
        label = "Solarized",
        background = Color(0xFF002B36),
        selection = Color(0xFF174956),
        text = Color(0xFFEEE8D5),
        keyword = Color(0xFF859900),
        string = Color(0xFF2AA198),
        number = Color(0xFFD33682),
        comment = Color(0xFF657B83),
        function = Color(0xFF268BD2),
        type = Color(0xFFB58900),
        error = Color(0xFFDC322F),
    ),
    CodeTheme(
        id = "one-dark",
        label = "One Dark",
        background = Color(0xFF1E2127),
        selection = Color(0xFF3E4451),
        text = Color(0xFFABB2BF),
        keyword = Color(0xFFC678DD),
        string = Color(0xFF98C379),
        number = Color(0xFFD19A66),
        comment = Color(0xFF5C6370),
        function = Color(0xFF61AFEF),
        type = Color(0xFFE5C07B),
        error = Color(0xFFE06C75),
    ),
)

private val customThemeId = "custom"

@Composable
fun CodeWorkbenchScreen(
    onBack: () -> Unit,
    initialCode: String? = null,
) {
    val context = LocalContext.current
    val preferences = remember {
        context.getSharedPreferences("code_workbench_settings", Context.MODE_PRIVATE)
    }
    var value by remember(initialCode) {
        mutableStateOf(
            TextFieldValue(
                text = initialCode ?: ifSample,
                selection = TextRange((initialCode ?: ifSample).length),
            ),
        )
    }
    var stdin by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<PythonRunResult?>(null) }
    var running by remember { mutableStateOf(false) }
    var runJob by remember { mutableStateOf<Job?>(null) }
    var settingsOpen by remember { mutableStateOf(false) }
    var themeId by remember {
        mutableStateOf(preferences.getString("theme", "dark") ?: "dark")
    }
    var customTheme by remember { mutableStateOf(loadCustomTheme(preferences)) }
    var fontSize by remember { mutableStateOf(preferences.getInt("font_size", 13)) }
    var lineHeight by remember { mutableStateOf(preferences.getInt("line_height", 20)) }
    var lineNumbers by remember { mutableStateOf(preferences.getBoolean("line_numbers", true)) }
    var wrapLines by remember { mutableStateOf(preferences.getBoolean("wrap_lines", false)) }
    var indentGuides by remember { mutableStateOf(preferences.getBoolean("indent_guides", true)) }
    val theme = if (themeId == customThemeId) {
        customTheme
    } else {
        codeThemes.firstOrNull { it.id == themeId } ?: codeThemes.first()
    }
    val scope = rememberCoroutineScope()

    LaunchedEffect(themeId, customTheme, fontSize, lineHeight, lineNumbers, wrapLines, indentGuides) {
        preferences.edit()
            .putString("theme", themeId)
            .putInt("font_size", fontSize)
            .putInt("line_height", lineHeight)
            .putBoolean("line_numbers", lineNumbers)
            .putBoolean("wrap_lines", wrapLines)
            .putBoolean("indent_guides", indentGuides)
            .putString("custom_background", customTheme.background.toHex())
            .putString("custom_text", customTheme.text.toHex())
            .putString("custom_keyword", customTheme.keyword.toHex())
            .putString("custom_string", customTheme.string.toHex())
            .putString("custom_number", customTheme.number.toHex())
            .putString("custom_comment", customTheme.comment.toHex())
            .putString("custom_function", customTheme.function.toHex())
            .putString("custom_type", customTheme.type.toHex())
            .putString("custom_error", customTheme.error.toHex())
            .apply()
    }

    val bracketsBalanced = remember(value.text) { hasBalancedBrackets(value.text) }
    val editorTextStyle = TextStyle(
        color = theme.text,
        fontFamily = FontFamily.Monospace,
        fontSize = fontSize.sp,
        lineHeight = lineHeight.sp,
    )
    val lineCount = value.text.lineSequence().count().coerceAtLeast(1)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(start = 18.dp, end = 18.dp, bottom = 24.dp),
    ) {
        BackBar(title = "Python 运行台", onBack = onBack)

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(7.dp),
        ) {
            ToolButton("if 示例") {
                value = TextFieldValue(ifSample, TextRange(ifSample.length))
                result = null
            }
            ToolButton("for 示例") {
                value = TextFieldValue(forSample, TextRange(forSample.length))
                result = null
            }
            ToolButton("错误示例") {
                value = TextFieldValue(errorSample, TextRange(errorSample.length))
                result = null
            }
            ToolButton("设置", icon = Icons.Filled.Settings) {
                settingsOpen = !settingsOpen
            }
        }

        if (settingsOpen) {
            Spacer(modifier = Modifier.height(9.dp))
            EditorSettingsCard(
                themeId = themeId,
                onThemeChange = { themeId = it },
                fontSize = fontSize,
                onFontSizeChange = { fontSize = it.coerceIn(11, 22) },
                lineHeight = lineHeight,
                onLineHeightChange = { lineHeight = it.coerceIn(16, 32) },
                lineNumbers = lineNumbers,
                onLineNumbersChange = { lineNumbers = it },
                wrapLines = wrapLines,
                onWrapLinesChange = { wrapLines = it },
                indentGuides = indentGuides,
                onIndentGuidesChange = { indentGuides = it },
                customTheme = customTheme,
                onCustomThemeChange = { customTheme = it },
            )
        }

        Spacer(modifier = Modifier.height(10.dp))
        GlassCard {
            Column(modifier = Modifier.padding(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(text = "main.py", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
                    Text(
                        text = if (bracketsBalanced) "括号匹配" else "括号未闭合",
                        color = if (bracketsBalanced) theme.type else theme.error,
                        fontSize = 11.sp,
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = "Python 3.11", color = MaterialTheme.colorScheme.primary, fontSize = 12.sp)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height((lineHeight * lineCount.coerceIn(8, 18) + 24).dp),
                    shape = RoundedCornerShape(14.dp),
                    color = theme.background,
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(vertical = 12.dp),
                    ) {
                        if (lineNumbers) {
                            Column(
                                modifier = Modifier
                                    .width(42.dp)
                                    .padding(end = 7.dp),
                                horizontalAlignment = Alignment.End,
                            ) {
                                repeat(lineCount) { index ->
                                    Text(
                                        text = "${index + 1}",
                                        color = theme.comment,
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = (fontSize - 1).sp,
                                        lineHeight = lineHeight.sp,
                                    )
                                }
                            }
                        }
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .let { modifier ->
                                    if (indentGuides) {
                                        modifier.drawBehind {
                                            val step = fontSize.sp.toPx() * 2.45f
                                            repeat(6) { index ->
                                                val x = step * (index + 1)
                                                drawLine(
                                                    color = theme.comment.copy(alpha = 0.18f),
                                                    start = Offset(x, 0f),
                                                    end = Offset(x, size.height),
                                                    strokeWidth = 1f,
                                                )
                                            }
                                        }
                                    } else {
                                        modifier
                                    }
                                }
                                .then(if (wrapLines) Modifier else Modifier.horizontalScroll(rememberScrollState()))
                                .padding(end = 12.dp),
                        ) {
                            BasicTextField(
                                value = value,
                                onValueChange = { next ->
                                    value = next.withAutoIndent(previous = value)
                                    result = null
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .let { if (wrapLines) it else it.widthIn(min = 560.dp) },
                                textStyle = editorTextStyle,
                                cursorBrush = SolidColor(theme.text),
                                visualTransformation = PythonSyntaxTransformation(theme),
                                onTextLayout = {},
                            )
                        }
                    }
                }
                Spacer(modifier = Modifier.height(9.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(7.dp),
                ) {
                    ToolButton("复制", Icons.Filled.ContentCopy) {
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                        clipboard.setPrimaryClip(ClipData.newPlainText("Python code", value.text))
                    }
                    ToolButton("清空", Icons.Filled.Clear) {
                        value = TextFieldValue("", TextRange(0))
                        result = null
                    }
                    ToolButton("格式化", Icons.AutoMirrored.Filled.FormatAlignLeft) {
                        val formatted = formatPython(value.text)
                        value = TextFieldValue(formatted, TextRange(formatted.length))
                        result = null
                    }
                    ToolButton("- 字号", Icons.Filled.Remove) {
                        fontSize = (fontSize - 1).coerceAtLeast(11)
                        lineHeight = (lineHeight - 1).coerceAtLeast(16)
                    }
                    ToolButton("+ 字号", Icons.Filled.TextIncrease) {
                        fontSize = (fontSize + 1).coerceAtMost(22)
                        lineHeight = (lineHeight + 1).coerceAtMost(32)
                    }
                }
                Spacer(modifier = Modifier.height(10.dp))
                Text(text = "输入", fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                Spacer(modifier = Modifier.height(6.dp))
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp),
                    shape = RoundedCornerShape(13.dp),
                    color = theme.background,
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
                            color = theme.text,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                        ),
                        cursorBrush = SolidColor(theme.text),
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = if (bracketsBalanced) Icons.Filled.CheckCircle else Icons.Filled.Clear,
                            contentDescription = null,
                            tint = if (bracketsBalanced) MaterialTheme.colorScheme.secondary else MaterialTheme.colorScheme.error,
                            modifier = Modifier.width(16.dp),
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        MutedText(text = "$lineCount 行 · ${value.text.length} 字符")
                    }
                    Spacer(modifier = Modifier.weight(1f))
                    if (running) {
                        StopButton {
                            runJob?.cancel()
                            runJob = null
                            running = false
                        }
                        Spacer(modifier = Modifier.width(7.dp))
                    }
                    RunButton(
                        running = running,
                        onClick = {
                            if (!running) {
                                running = true
                                result = null
                                val codeToRun = value.text
                                val inputToRun = stdin
                                runJob = scope.launch {
                                    val run = withContext(Dispatchers.IO) {
                                        PythonRunner.run(codeToRun, inputToRun)
                                    }
                                    result = run
                                    running = false
                                    runJob = null
                                }
                            }
                        },
                    )
                }
                if (running) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        CircularProgressIndicator(
                            modifier = Modifier
                                .height(14.dp)
                                .width(14.dp),
                            strokeWidth = 2.dp,
                            color = MaterialTheme.colorScheme.primary,
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "正在运行，可随时停止界面等待...",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
        }

        result?.let { run ->
            Spacer(modifier = Modifier.height(10.dp))
            ResultPanel(run = run)
        }
    }
}

@Composable
private fun EditorSettingsCard(
    themeId: String,
    onThemeChange: (String) -> Unit,
    fontSize: Int,
    onFontSizeChange: (Int) -> Unit,
    lineHeight: Int,
    onLineHeightChange: (Int) -> Unit,
    lineNumbers: Boolean,
    onLineNumbersChange: (Boolean) -> Unit,
    wrapLines: Boolean,
    onWrapLinesChange: (Boolean) -> Unit,
    indentGuides: Boolean,
    onIndentGuidesChange: (Boolean) -> Unit,
    customTheme: CodeTheme,
    onCustomThemeChange: (CodeTheme) -> Unit,
) {
    var customDialogOpen by remember { mutableStateOf(false) }
    GlassCard {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(text = "代码主题", fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                codeThemes.forEach { item ->
                    val selected = item.id == themeId
                    Box(
                        modifier = Modifier
                            .background(
                                if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                                RoundedCornerShape(9.dp),
                            )
                            .clickable { onThemeChange(item.id) }
                            .padding(horizontal = 10.dp, vertical = 7.dp),
                    ) {
                        Text(
                            text = item.label,
                            color = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                }
                val selected = themeId == customThemeId
                Box(
                    modifier = Modifier
                        .background(
                            if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                            RoundedCornerShape(9.dp),
                        )
                        .clickable {
                            onThemeChange(customThemeId)
                            customDialogOpen = true
                        }
                        .padding(horizontal = 10.dp, vertical = 7.dp),
                ) {
                    Text(
                        text = "自定义",
                        color = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            SettingStepper("字号", "$fontSize sp", onDecrease = { onFontSizeChange(fontSize - 1) }, onIncrease = { onFontSizeChange(fontSize + 1) })
            SettingStepper("行高", "$lineHeight sp", onDecrease = { onLineHeightChange(lineHeight - 1) }, onIncrease = { onLineHeightChange(lineHeight + 1) })
            BooleanSetting("显示行号", lineNumbers, onLineNumbersChange)
            BooleanSetting("自动换行", wrapLines, onWrapLinesChange)
            BooleanSetting("显示缩进线", indentGuides, onIndentGuidesChange)
        }
    }
    if (customDialogOpen) {
        CustomCodeThemeDialog(
            theme = customTheme,
            onDismiss = { customDialogOpen = false },
            onSave = {
                onCustomThemeChange(it)
                onThemeChange(customThemeId)
                customDialogOpen = false
            },
        )
    }
}

@Composable
private fun CustomCodeThemeDialog(
    theme: CodeTheme,
    onDismiss: () -> Unit,
    onSave: (CodeTheme) -> Unit,
) {
    var background by remember { mutableStateOf(theme.background.toHex()) }
    var text by remember { mutableStateOf(theme.text.toHex()) }
    var keyword by remember { mutableStateOf(theme.keyword.toHex()) }
    var string by remember { mutableStateOf(theme.string.toHex()) }
    var number by remember { mutableStateOf(theme.number.toHex()) }
    var comment by remember { mutableStateOf(theme.comment.toHex()) }
    var function by remember { mutableStateOf(theme.function.toHex()) }
    var type by remember { mutableStateOf(theme.type.toHex()) }
    var error by remember { mutableStateOf(theme.error.toHex()) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "自定义代码主题") },
        text = {
            Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                Text(
                    text = "输入 #RRGGBB 颜色，例如 #10151A。",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                )
                Spacer(modifier = Modifier.height(8.dp))
                ThemeColorInput("背景", background) { background = it }
                ThemeColorInput("文字", text) { text = it }
                ThemeColorInput("关键字", keyword) { keyword = it }
                ThemeColorInput("字符串", string) { string = it }
                ThemeColorInput("数字", number) { number = it }
                ThemeColorInput("注释", comment) { comment = it }
                ThemeColorInput("函数", function) { function = it }
                ThemeColorInput("类与类型", type) { type = it }
                ThemeColorInput("错误", error) { error = it }
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    onSave(
                        theme.copy(
                            background = parseHexOrDefault(background, theme.background),
                            text = parseHexOrDefault(text, theme.text),
                            keyword = parseHexOrDefault(keyword, theme.keyword),
                            string = parseHexOrDefault(string, theme.string),
                            number = parseHexOrDefault(number, theme.number),
                            comment = parseHexOrDefault(comment, theme.comment),
                            function = parseHexOrDefault(function, theme.function),
                            type = parseHexOrDefault(type, theme.type),
                            error = parseHexOrDefault(error, theme.error),
                        ),
                    )
                },
            ) {
                Text(text = "应用")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text(text = "取消")
            }
        },
    )
}

@Composable
private fun ThemeColorInput(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text = label, modifier = Modifier.weight(1f), fontSize = 12.sp)
        Surface(
            modifier = Modifier.width(130.dp),
            shape = RoundedCornerShape(8.dp),
            color = MaterialTheme.colorScheme.surfaceVariant,
        ) {
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier.padding(horizontal = 9.dp, vertical = 7.dp),
                textStyle = TextStyle(
                    color = MaterialTheme.colorScheme.onSurface,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 11.sp,
                ),
                singleLine = true,
                cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
            )
        }
    }
}

@Composable
private fun SettingStepper(
    label: String,
    value: String,
    onDecrease: () -> Unit,
    onIncrease: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text = label, modifier = Modifier.weight(1f))
        ToolButton("-", Icons.Filled.Remove, onDecrease)
        Spacer(modifier = Modifier.width(8.dp))
        Text(text = value, modifier = Modifier.width(54.dp), fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.width(8.dp))
        ToolButton("+", Icons.Filled.TextIncrease, onIncrease)
    }
}

@Composable
private fun BooleanSetting(
    label: String,
    selected: Boolean,
    onSelectedChange: (Boolean) -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onSelectedChange(!selected) }
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text = label, modifier = Modifier.weight(1f))
        Box(
            modifier = Modifier
                .background(
                    if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                    RoundedCornerShape(8.dp),
                )
                .padding(horizontal = 10.dp, vertical = 5.dp),
        ) {
            Text(
                text = if (selected) "开" else "关",
                color = if (selected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun ResultPanel(run: PythonRunResult) {
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
            Text(
                text = run.humanError,
                color = Color(0xFFFFD9D9),
                fontSize = 13.sp,
                lineHeight = 19.sp,
            )
        }
    }
}

@Composable
private fun ToolButton(
    text: String,
    icon: ImageVector? = null,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(11.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icon != null) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.width(15.dp),
            )
            Spacer(modifier = Modifier.width(4.dp))
        }
        Text(text = text, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun RunButton(
    running: Boolean,
    onClick: () -> Unit,
) {
    Row(
        modifier = Modifier
            .background(
                if (running) MaterialTheme.colorScheme.surfaceVariant else Color(0xFF1C9D6B),
                RoundedCornerShape(11.dp),
            )
            .clickable(enabled = !running, onClick = onClick)
            .padding(horizontal = 18.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Filled.PlayArrow,
            contentDescription = null,
            modifier = Modifier
                .height(16.dp)
                .width(16.dp),
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

@Composable
private fun StopButton(onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.errorContainer, RoundedCornerShape(11.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 12.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = Icons.Filled.Stop,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onErrorContainer,
            modifier = Modifier
                .height(16.dp)
                .width(16.dp),
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = "停止",
            color = MaterialTheme.colorScheme.onErrorContainer,
            fontWeight = FontWeight.Bold,
        )
    }
}

private class PythonSyntaxTransformation(
    private val theme: CodeTheme,
) : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        val source = text.text
        val highlighted = buildAnnotatedString {
            append(source)
            val keywords = setOf(
                "and", "as", "assert", "async", "await", "break", "class", "continue",
                "def", "del", "elif", "else", "except", "False", "finally", "for",
                "from", "global", "if", "import", "in", "is", "lambda", "None",
                "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
                "while", "with", "yield",
            )
            Regex("""#[^\n]*""").findAll(source).forEach { token ->
                addStyle(SpanStyle(color = theme.comment), token.range.first, token.range.last + 1)
            }
            Regex("""("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')""").findAll(source).forEach { token ->
                addStyle(SpanStyle(color = theme.string), token.range.first, token.range.last + 1)
            }
            Regex("""\b\d+(?:\.\d+)?\b""").findAll(source).forEach { token ->
                addStyle(SpanStyle(color = theme.number), token.range.first, token.range.last + 1)
            }
            Regex("""\b[A-Za-z_]\w*(?=\s*\()""").findAll(source).forEach { token ->
                addStyle(SpanStyle(color = theme.function), token.range.first, token.range.last + 1)
            }
            Regex("""\b[A-Za-z_]\w*\b""").findAll(source).forEach { token ->
                val word = token.value
                if (word in keywords) {
                    addStyle(SpanStyle(color = theme.keyword, fontWeight = FontWeight.Bold), token.range.first, token.range.last + 1)
                } else if (word.firstOrNull()?.isUpperCase() == true) {
                    addStyle(SpanStyle(color = theme.type), token.range.first, token.range.last + 1)
                }
            }
        }
        return TransformedText(highlighted, OffsetMapping.Identity)
    }
}

private fun TextFieldValue.withAutoIndent(previous: TextFieldValue): TextFieldValue {
    val cursor = selection.start
    val insertedNewline = text.length == previous.text.length + 1 &&
        text.count { it == '\n' } == previous.text.count { it == '\n' } + 1 &&
        cursor > 0 &&
        text.getOrNull(cursor - 1) == '\n'
    if (!insertedNewline) return this

    val previousLineStart = previous.text.lastIndexOf('\n', (previous.selection.start - 1).coerceAtLeast(0))
        .let { if (it < 0) 0 else it + 1 }
    val previousLine = previous.text.substring(previousLineStart, previous.selection.start)
    val indent = previousLine.takeWhile { it == ' ' || it == '\t' }
    if (indent.isEmpty()) return this
    val adjustedText = text.substring(0, cursor) + indent + text.substring(cursor)
    return copy(
        text = adjustedText,
        selection = TextRange(cursor + indent.length),
    )
}

private fun hasBalancedBrackets(code: String): Boolean {
    val stack = ArrayDeque<Char>()
    var inSingle = false
    var inDouble = false
    var escaped = false
    code.forEach { character ->
        if (escaped) {
            escaped = false
            return@forEach
        }
        if (character == '\\' && (inSingle || inDouble)) {
            escaped = true
            return@forEach
        }
        if (character == '\'' && !inDouble) {
            inSingle = !inSingle
            return@forEach
        }
        if (character == '"' && !inSingle) {
            inDouble = !inDouble
            return@forEach
        }
        if (inSingle || inDouble) return@forEach
        when (character) {
            '(', '[', '{' -> stack.addLast(character)
            ')' -> if (stack.removeLastOrNull() != '(') return false
            ']' -> if (stack.removeLastOrNull() != '[') return false
            '}' -> if (stack.removeLastOrNull() != '{') return false
        }
    }
    return stack.isEmpty() && !inSingle && !inDouble
}

private fun formatPython(code: String): String {
    return code.replace("\t", "    ")
        .lineSequence()
        .joinToString("\n") { it.trimEnd() }
        .trimEnd() + "\n"
}

private fun loadCustomTheme(
    preferences: android.content.SharedPreferences,
): CodeTheme {
    val fallback = codeThemes.first()
    return CodeTheme(
        id = customThemeId,
        label = "自定义",
        background = parseHexOrDefault(preferences.getString("custom_background", null), fallback.background),
        selection = fallback.selection,
        text = parseHexOrDefault(preferences.getString("custom_text", null), fallback.text),
        keyword = parseHexOrDefault(preferences.getString("custom_keyword", null), fallback.keyword),
        string = parseHexOrDefault(preferences.getString("custom_string", null), fallback.string),
        number = parseHexOrDefault(preferences.getString("custom_number", null), fallback.number),
        comment = parseHexOrDefault(preferences.getString("custom_comment", null), fallback.comment),
        function = parseHexOrDefault(preferences.getString("custom_function", null), fallback.function),
        type = parseHexOrDefault(preferences.getString("custom_type", null), fallback.type),
        error = parseHexOrDefault(preferences.getString("custom_error", null), fallback.error),
    )
}

private fun parseHexOrDefault(
    value: String?,
    fallback: Color,
): Color {
    if (value.isNullOrBlank()) return fallback
    return runCatching {
        Color(android.graphics.Color.parseColor(value.trim()))
    }.getOrDefault(fallback)
}

private fun Color.toHex(): String {
    return "#%06X".format(toArgb() and 0xFFFFFF)
}
