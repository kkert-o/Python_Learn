package com.pythonlearn.app.runtime

import com.chaquo.python.Python
import org.json.JSONObject
import java.util.concurrent.Executors

data class PythonRunResult(
    val ok: Boolean,
    val lines: List<String> = emptyList(),
    val output: String = "",
    val errorType: String = "",
    val rawError: String = "",
    val humanError: String = "",
)

object PythonErrorExplainer {
    fun explain(errorType: String, message: String, traceback: String): String {
        val cleanType = errorType.removePrefix("builtins.")
        val cleanMessage = message.trim()
        return when (cleanType) {
            "NameError" -> explainNameError(cleanMessage)
            "SyntaxError" -> "语法检查没通过。${lineHint(traceback)}请对照示例检查冒号、括号、缩进和引号是否配对。"
            "IndentationError" -> "缩进方式不一致。Python 用缩进表示代码属于哪一层，请检查空格和 Tab 是否混用。${lineHint(traceback)}"
            "TabError" -> "同一段代码里同时用了空格和 Tab。请统一只用 4 个空格。${lineHint(traceback)}"
            "TypeError" -> "这里做了类型不匹配的操作，比如把数字和文字直接相加，或调用了不存在的方法参数。请检查两边的类型。"
            "ValueError" -> "传给函数的值在类型上没问题，但内容不合适。比如把 \"abc\" 转成整数。请检查数据内容。"
            "ZeroDivisionError" -> "出现了除以 0 的计算。除法的右边不能是 0，先检查变量是否为 0，再加判断。"
            "IndexError" -> "索引越界。列表没有这个位置，请检查索引范围或是否少写了 -1。"
            "KeyError" -> "字典里找不到这个键。先确认键名拼写，或改用 .get() 再处理找不到的情况。"
            "AttributeError" -> "这个对象没有你要调用的属性或方法。请检查对象类型，再确认方法名拼写。"
            "ImportError", "ModuleNotFoundError" -> "导入失败：${message.ifBlank { "找不到对应模块" }}。请检查模块名拼写，未安装的模块需要先配置。"
            "UnboundLocalError" -> "变量在赋值前就被使用了，通常是在函数里修改外层变量却忘了写 global。请检查作用域。"
            "RecursionError" -> "递归没有在合适的时候停止，导致不断调用自己。请先检查递归出口条件。"
            "MemoryError" -> "程序需要的内存太多，可能产生了无限循环或非常大的数据。请缩小循环范围后重试。"
            "KeyboardInterrupt" -> "程序被中断。如果是无限循环，请给循环加一个明确的停止条件。"
            "EOFError" -> "程序试图读取用户输入，但运行台没有交互输入。请先给变量直接赋值，或使用课程提供的数据。"
            "SystemExit" -> "程序主动调用了退出。可以删掉 sys.exit()，让代码自然运行到结束。"
            else -> "程序没有按预期运行。${if (cleanMessage.isNotBlank()) "提示：$cleanMessage。" else ""}先缩小到能复现问题的一两行，再逐步检查。"
        }
    }

    private fun explainNameError(message: String): String {
        val name = Regex("name '([^']+)' is not defined").find(message)?.groupValues?.get(1)
        return if (name != null) {
            "找不到名称 $name。请检查变量名是否拼写一致，或是否在它前面完成了赋值。"
        } else {
            "找不到这个名称。请检查变量名拼写和赋值顺序。"
        }
    }

    private fun lineHint(traceback: String): String {
        val line = Regex("<user_code>\", line (\\d+)").find(traceback)?.groupValues?.get(1)
        return if (line != null) "问题可能出现在第 $line 行。" else ""
    }
}

object PythonRunner {
    private val executionLock = Any()
    private val executor = Executors.newSingleThreadExecutor()

    fun run(code: String, stdin: String = ""): PythonRunResult = runSafely(code, stdin)

    fun runAsync(code: String, stdin: String = "", onResult: (PythonRunResult) -> Unit) {
        executor.execute {
            val result = runSafely(code, stdin)
            onResult(result)
        }
    }

    private fun runSafely(code: String, stdin: String): PythonRunResult {
        return try {
            runOnPython(code, stdin)
        } catch (error: Throwable) {
            PythonRunResult(
                ok = false,
                errorType = error.javaClass.simpleName,
                rawError = error.message ?: "",
                humanError = "运行引擎暂时没有启动成功，请稍后再试。如果持续出现，请重新打开应用。",
            )
        }
    }

    private fun runOnPython(code: String, stdin: String): PythonRunResult {
        synchronized(executionLock) {
            val pyModule = Python.getInstance().getModule("runner")
            val result = pyModule.callAttr("run", code, stdin).toString()
            return parseResult(result)
        }
    }

    private fun parseResult(raw: String): PythonRunResult {
        val json = JSONObject(raw)
        val ok = json.optBoolean("ok")
        val output = json.optString("output")
        if (ok) {
            val normalized = output.replace("\r\n", "\n").trimEnd('\n')
            val lines = if (normalized.isEmpty()) emptyList() else normalized.split("\n")
            return PythonRunResult(
                ok = true,
                lines = lines,
                output = output,
            )
        }
        val errorType = json.optString("type")
        val message = json.optString("message")
        val traceback = json.optString("traceback")
        val human = PythonErrorExplainer.explain(errorType, message, traceback)
        return PythonRunResult(
            ok = false,
            lines = output.replace("\r\n", "\n").trimEnd('\n').split("\n").filter { it.isNotBlank() },
            output = output,
            errorType = errorType.removePrefix("builtins."),
            rawError = message,
            humanError = human,
        )
    }
}
