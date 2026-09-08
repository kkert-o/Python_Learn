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
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pythonlearn.app.data.ProjectCatalog
import com.pythonlearn.app.data.ProjectInfo
import com.pythonlearn.app.ui.components.CodePanel
import com.pythonlearn.app.ui.components.BackBar
import com.pythonlearn.app.ui.components.GlassCard
import com.pythonlearn.app.ui.components.MutedText
import com.pythonlearn.app.ui.components.Tag

@Composable
fun ProjectDetailScreen(
    project: ProjectInfo = ProjectCatalog.guess,
    onBack: () -> Unit,
    onOpenWorkbench: (String) -> Unit,
    completed: Boolean,
    onComplete: () -> Unit,
) {
    val openedHints = remember { mutableStateListOf<Int>() }
    LazyColumn(
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item {
            BackBar(title = "项目", onBack = onBack)
        }
        item {
            Column {
                MutedText(text = project.level)
                Text(text = project.title, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    project.knowledge.forEach { Tag(text = it, active = true) }
                }
            }
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = "项目目标", fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = project.goal,
                        color = MaterialTheme.colorScheme.onSurface,
                        style = MaterialTheme.typography.bodyMedium,
                        lineHeight = 21.sp,
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(text = "功能需求", fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(5.dp))
                    project.requirements.forEachIndexed { index, requirement ->
                        Row(modifier = Modifier.padding(vertical = 4.dp)) {
                            Text(
                                text = "${index + 1}",
                                modifier = Modifier
                                    .width(24.dp)
                                    .background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(7.dp))
                                    .padding(vertical = 2.dp),
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Bold,
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = requirement, modifier = Modifier.weight(1f))
                        }
                    }
                }
            }
        }
        item {
            Text(text = "思路提示", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        }
        item {
            GlassCard {
                Column(modifier = Modifier.padding(10.dp)) {
                    project.hints.forEachIndexed { index, hint ->
                        val open = index in openedHints
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    if (open) openedHints.remove(index) else openedHints.add(index)
                                }
                                .background(MaterialTheme.colorScheme.surfaceVariant, RoundedCornerShape(12.dp))
                                .padding(12.dp),
                        ) {
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Text(text = "提示 ${index + 1}", modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold)
                                Icon(
                                    imageVector = if (open) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                                    contentDescription = if (open) "收起" else "展开",
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                            if (open) {
                                Spacer(modifier = Modifier.height(6.dp))
                                MutedText(text = hint, small = false)
                            }
                        }
                        Spacer(modifier = Modifier.height(7.dp))
                    }
                }
            }
        }
        item {
            Text(text = "起始代码", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        }
        item {
            CodePanel(code = project.starter)
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "完整答案不会直接给出。先在运行台写结构，再逐步补逻辑。",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = 12.sp,
            )
        }
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.primary, RoundedCornerShape(14.dp))
                    .clickable { onOpenWorkbench(project.starter) }
                    .padding(vertical = 13.dp),
                horizontalArrangement = Arrangement.Center,
            ) {
                Text(text = "打开运行台练习", color = MaterialTheme.colorScheme.onPrimary, fontWeight = FontWeight.Bold)
            }
        }
        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        if (completed) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.secondary,
                        RoundedCornerShape(14.dp),
                    )
                    .clickable(enabled = !completed, onClick = onComplete)
                    .padding(vertical = 13.dp),
                horizontalArrangement = Arrangement.Center,
            ) {
                Text(
                    text = if (completed) "项目已完成" else "标记项目完成",
                    color = if (completed) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onPrimary,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}
