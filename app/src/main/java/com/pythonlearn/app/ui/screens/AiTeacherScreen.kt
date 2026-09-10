package com.pythonlearn.app.ui.screens

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
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.runtime.AiConfig
import com.pythonlearn.app.runtime.AiTeacherClient
import com.pythonlearn.app.ui.components.BackBar
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private data class ChatMessage(val role: String, val text: String)

private val aiModes = listOf("老师模式", "只给思路", "普通提示", "只指出错误", "直接答案")

@Composable
fun AiTeacherScreen(
    onBack: () -> Unit,
    aiConfig: AiConfig,
    onAiConfigChange: (AiConfig) -> Unit,
    onAiPrompt: () -> Unit,
) {
    var mode by remember { mutableStateOf("老师模式") }
    var input by remember { mutableStateOf("") }
    var settingsOpen by remember { mutableStateOf(false) }
    var waiting by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    var messages by remember {
        mutableStateOf(
            listOf(
                ChatMessage(
                    role = "bot",
                    text = "你好，我是 Python 学习老师。当前是老师模式：我会先引导你自己想，不会直接替你把作业写完。",
                ),
            ),
        )
    }
    val chatListState = rememberLazyListState()
    fun submitText(text: String) {
        if (waiting) return
        val trimmed = text.trim()
        if (trimmed.isEmpty()) return
        onAiPrompt()
        val history = messages.map { it.role to it.text }
        messages = messages + ChatMessage("user", trimmed)
        input = ""
        waiting = true
        scope.launch {
            val reply = try {
                if (aiConfig.apiKey.isBlank()) {
                    replyFor(trimmed, mode)
                } else {
                    withContext(Dispatchers.IO) {
                        AiTeacherClient.ask(
                            config = aiConfig,
                            systemPrompt = systemPromptFor(mode),
                            history = history,
                            userText = trimmed,
                        )
                    }
                }
            } catch (error: Throwable) {
                "AI 连接失败：${error.message ?: "未知错误"}\n\n已先用本地引导模式回答：\n${replyFor(trimmed, mode)}"
            }
            messages = messages + ChatMessage("bot", reply)
            waiting = false
        }
    }
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            chatListState.animateScrollToItem(messages.lastIndex)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .imePadding()
            .padding(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 12.dp),
    ) {
        BackBar(title = "AI Python 老师", onBack = onBack)

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 6.dp),
            horizontalArrangement = Arrangement.End,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(10.dp))
                    .clickable { settingsOpen = true }
                    .padding(horizontal = 9.dp, vertical = 6.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Filled.Settings,
                        contentDescription = null,
                        modifier = Modifier.height(15.dp).width(15.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = if (aiConfig.apiKey.isBlank()) "本地引导模式" else "大模型已配置",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState())
                .padding(top = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            aiModes.forEach { item ->
                val selected = mode == item
                Box(
                    modifier = Modifier
                        .background(
                            if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                            RoundedCornerShape(10.dp),
                        )
                        .clickable { mode = item }
                        .padding(horizontal = 9.dp, vertical = 7.dp),
                ) {
                    Text(
                        text = item,
                        color = if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
        }

        if (waiting) {
            Row(modifier = Modifier.padding(top = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                CircularProgressIndicator(
                    modifier = Modifier.height(13.dp).width(13.dp),
                    strokeWidth = 2.dp,
                )
                Spacer(modifier = Modifier.width(7.dp))
                Text(text = "AI 正在思考...", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }

        Spacer(modifier = Modifier.height(10.dp))
        LazyColumn(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            state = chatListState,
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(messages) { message ->
                val isUser = message.role == "user"
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = if (isUser) Alignment.CenterEnd else Alignment.CenterStart,
                ) {
                    Text(
                        text = message.text,
                        modifier = Modifier
                            .background(
                                if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surface.copy(alpha = 0.9f),
                                RoundedCornerShape(
                                    topStart = 15.dp,
                                    topEnd = 15.dp,
                                    bottomStart = if (isUser) 15.dp else 5.dp,
                                    bottomEnd = if (isUser) 5.dp else 15.dp,
                                ),
                            )
                            .padding(horizontal = 12.dp, vertical = 10.dp),
                        color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
                        fontSize = 13.sp,
                        lineHeight = 20.sp,
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            QuickChip("为什么报错说变量没定义？") {
                submitText(it)
            }
            QuickChip("猜数字项目思路？") {
                submitText(it)
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Surface(
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(13.dp),
                color = MaterialTheme.colorScheme.surfaceVariant,
            ) {
                Box {
                    if (input.isEmpty()) {
                        Text(
                            text = "输入问题或代码",
                            modifier = Modifier.padding(start = 12.dp, top = 11.dp, bottom = 11.dp, end = 12.dp),
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.65f),
                            fontSize = 13.sp,
                        )
                    }
                    BasicTextField(
                        value = input,
                        onValueChange = { input = it },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 12.dp, vertical = 11.dp),
                        textStyle = TextStyle(color = MaterialTheme.colorScheme.onSurface, fontSize = 13.sp),
                        cursorBrush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.primary),
                    )
                }
            }
            Spacer(modifier = Modifier.width(7.dp))
            Box(
                modifier = Modifier
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(13.dp))
                    .clickable {
                        val text = input.trim()
                        submitText(text)
                    }
                    .padding(horizontal = 17.dp, vertical = 11.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(text = "发送", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
            }
        }
    }

    if (settingsOpen) {
        AiSettingsDialog(
            config = aiConfig,
            onDismiss = { settingsOpen = false },
            onSave = {
                onAiConfigChange(it)
                settingsOpen = false
            },
        )
    }
}

@Composable
private fun QuickChip(text: String, onSend: (String) -> Unit) {
    Box(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(10.dp))
            .clickable { onSend(text) }
            .padding(horizontal = 10.dp, vertical = 7.dp),
    ) {
        Text(text = text, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurface)
    }
}

@Composable
private fun AiSettingsDialog(
    config: AiConfig,
    onDismiss: () -> Unit,
    onSave: (AiConfig) -> Unit,
) {
    var endpoint by remember { mutableStateOf(config.endpoint) }
    var apiKey by remember { mutableStateOf(config.apiKey) }
    var model by remember { mutableStateOf(config.model) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(text = "AI 模型连接") },
        text = {
            Column {
                DialogInput(
                    label = "接口地址",
                    value = endpoint,
                    onValueChange = { endpoint = it },
                )
                Spacer(modifier = Modifier.height(9.dp))
                DialogInput(
                    label = "API Key",
                    value = apiKey,
                    onValueChange = { apiKey = it },
                )
                Spacer(modifier = Modifier.height(9.dp))
                DialogInput(
                    label = "模型名称",
                    value = model,
                    onValueChange = { model = it },
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Key 只保存在本机。未配置时 AI 老师使用本地引导模式。",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    onSave(
                        AiConfig(
                            endpoint = endpoint.trim(),
                            apiKey = apiKey.trim(),
                            model = model.trim(),
                        ),
                    )
                },
            ) {
                Text(text = "保存")
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
private fun DialogInput(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
) {
    Column {
        Text(text = label, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(modifier = Modifier.height(4.dp))
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            color = MaterialTheme.colorScheme.surfaceVariant,
        ) {
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier.padding(horizontal = 11.dp, vertical = 9.dp),
                textStyle = TextStyle(color = MaterialTheme.colorScheme.onSurface, fontSize = 13.sp),
                cursorBrush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.primary),
            )
        }
    }
}

private fun systemPromptFor(mode: String): String {
    return "你是一位耐心的 Python 学习老师。用户是初学者，目标是学会自己分析问题并完成可运行项目。" +
        "当前学习模式：$mode。" +
        "老师模式：先引导思考，再给提示；只给思路：不给可直接粘贴的完整答案；普通提示：给关键提示；" +
        "只指出错误：先指出问题范围；直接答案：才提供可直接使用的代码。回答保持简短、清晰，使用中文。"
}

private fun replyFor(question: String, mode: String): String {
    return when {
        question.contains("变量没定义") || question.contains("NameError") || question.contains("nameerror") -> when (mode) {
            "只指出错误" -> "错误指向变量名。先检查拼写，再确认变量在 print 前已经被赋值。"
            "只给思路" -> "思路：检查拼写 → 确认赋值顺序 → 先打印变量。"
            "直接答案" -> "例如先写 nickname = \"小林\"，再写 print(nickname)。"
            else -> "先别急着加代码。看看报错里的名字和你上一行写的变量是否完全一致，通常改一个字母就行。"
        }
        question.contains("猜数字") -> when (mode) {
            "直接答案" -> "结构是：生成答案、while 接收输入、比较大小、猜对结束，最后打印次数。"
            else -> "先拆成四步：生成答案、接收输入、比较、结束。先只实现输入一次并判断大小，跑通后再考虑 while。"
        }
        else -> when (mode) {
            "只给思路" -> "告诉我你当前卡在哪一步，我先只讲思路。"
            "普通提示" -> "把相关代码或报错发给我，我会只给具体提示。"
            "只指出错误" -> "请发代码，我只指出可能有问题的地方。"
            "直接答案" -> "直接答案会降低你的练习效果。建议先试一次，我再帮你检查。"
            else -> "可以把代码或报错发给我。老师模式下，我会先帮你缩小范围，再让你自己完成。"
        }
    }
}
