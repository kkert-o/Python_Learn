package com.pythonlearn.app.data

enum class TrainingType(
    val label: String,
    val description: String,
) {
    READ_CODE("看代码", "读懂变量、条件和循环"),
    PREDICT_OUTPUT("预测输出", "先判断结果，再运行验证"),
    COMPLETE_CODE("代码补全", "补上缺失的表达式或语句"),
    DEBUG_LAB("Debug Lab", "定位错误并写出修正后的代码"),
}

data class TrainingExercise(
    val id: String,
    val lessonId: String,
    val type: TrainingType,
    val title: String,
    val prompt: String,
    val code: String,
    val question: String,
    val options: List<String> = emptyList(),
    val answerIndex: Int = -1,
    val explanation: String,
    val hints: List<String> = emptyList(),
    val starterCode: String? = null,
    val requiredSnippets: List<String> = emptyList(),
    val forbiddenSnippets: List<String> = emptyList(),
    val stdin: String = "",
    val referenceSolution: String? = null,
) {
    val isCodeTask: Boolean
        get() = starterCode != null
}

data class TrainingCheckResult(
    val correct: Boolean,
    val message: String,
)

object TrainingGrader {
    fun checkChoice(exercise: TrainingExercise, selectedIndex: Int?): Boolean {
        return selectedIndex != null && selectedIndex == exercise.answerIndex
    }

    fun checkCode(exercise: TrainingExercise, submittedCode: String): TrainingCheckResult {
        val normalized = submittedCode.normalizeForTraining()
        val starter = exercise.starterCode.orEmpty().normalizeForTraining()
        val forbidden = exercise.forbiddenSnippets.firstOrNull { snippet ->
            normalized.contains(snippet.normalizeForTraining())
        }
        if (forbidden != null) {
            return TrainingCheckResult(false, "代码里仍然保留了错误写法：$forbidden")
        }

        if (normalized.isBlank() || normalized == starter) {
            return TrainingCheckResult(false, "还没有完成修改，先补上缺失部分或修复错误。")
        }

        val missing = exercise.requiredSnippets.filterNot { snippet ->
            normalized.contains(snippet.normalizeForTraining())
        }
        if (missing.isNotEmpty()) {
            return TrainingCheckResult(
                correct = false,
                message = "还缺少必要的代码结构：${missing.joinToString("、")}",
            )
        }

        return TrainingCheckResult(true, "检查通过。代码已经包含完成任务所需的关键结构。")
    }
}

private fun String.normalizeForTraining(): String {
    return lineSequence()
        .joinToString("\n") { line ->
            line.substringBefore("#").filterNot(Char::isWhitespace)
        }
}

object TrainingCatalog {
    val all: List<TrainingExercise> = listOf(
        TrainingExercise(
            id = "read-variable",
            lessonId = "variable",
            type = TrainingType.READ_CODE,
            title = "变量保存了什么",
            prompt = "先阅读代码，不要急着运行。",
            code = """
                name = "小林"
                age = 18
                print(name, age)
            """.trimIndent(),
            question = "关于这段代码，哪项说法正确？",
            options = listOf(
                "name 保存字符串，age 保存整数",
                "name 和 age 都保存字符串",
                "age 会被自动打印成字符串 18 岁",
                "代码会报 NameError",
            ),
            answerIndex = 0,
            explanation = "引号中的内容是字符串，18 没有引号，是整数。print 会把两者依次显示。",
            hints = listOf(
                "先看等号右边的值有没有引号。",
                "再确认 print 使用的是已经定义过的变量。",
            ),
        ),
        TrainingExercise(
            id = "read-if",
            lessonId = "if",
            type = TrainingType.READ_CODE,
            title = "条件分支会走哪里",
            prompt = "阅读条件判断，判断哪个分支会执行。",
            code = """
                score = 60
                if score >= 60:
                    print("通过")
                else:
                    print("继续加油")
            """.trimIndent(),
            question = "score 正好等于 60 时，程序会输出什么？",
            options = listOf("通过", "继续加油", "两个都输出", "什么也不输出"),
            answerIndex = 0,
            explanation = ">= 表示大于或等于，60 >= 60 成立，所以执行 if 分支。",
            hints = listOf(
                "注意 >= 和 > 的区别。",
                "条件为 True 时执行缩进在 if 下面的代码。",
            ),
        ),
        TrainingExercise(
            id = "read-loop",
            lessonId = "for",
            type = TrainingType.READ_CODE,
            title = "循环执行几次",
            prompt = "观察 range 的起止值。",
            code = """
                for number in range(1, 4):
                    print(number)
            """.trimIndent(),
            question = "循环体会执行几次？",
            options = listOf("2 次", "3 次", "4 次", "无限次"),
            answerIndex = 1,
            explanation = "range(1, 4) 产生 1、2、3，不包含结束值 4，所以执行 3 次。",
            hints = listOf(
                "range 的第二个参数不包含在结果中。",
                "列出 range 实际产生的数字。",
            ),
        ),
        TrainingExercise(
            id = "read-function",
            lessonId = "function",
            type = TrainingType.READ_CODE,
            title = "函数返回了什么",
            prompt = "先找函数定义，再找函数调用。",
            code = """
                def add(a, b):
                    return a + b

                result = add(1, 2)
                print(result)
            """.trimIndent(),
            question = "最终输出的结果是什么？",
            options = listOf("a + b", "3", "12", "None"),
            answerIndex = 1,
            explanation = "调用 add(1, 2) 时，a 是 1、b 是 2，return 返回 3。",
            hints = listOf(
                "把实参依次代入形参。",
                "return 会把计算结果交给调用处。",
            ),
        ),
        TrainingExercise(
            id = "predict-add",
            lessonId = "variable",
            type = TrainingType.PREDICT_OUTPUT,
            title = "增量赋值",
            prompt = "先选择你预测的输出，再运行代码验证。",
            code = """
                x = 10
                x += 5
                print(x)
            """.trimIndent(),
            question = "这段代码会输出什么？",
            options = listOf("10", "15", "5", "报错"),
            answerIndex = 1,
            explanation = "x += 5 等价于 x = x + 5，所以 10 加 5 后得到 15。",
            hints = listOf("把 += 展开成普通赋值语句。"),
        ),
        TrainingExercise(
            id = "predict-else",
            lessonId = "if",
            type = TrainingType.PREDICT_OUTPUT,
            title = "判断奇偶",
            prompt = "先判断条件结果，再运行验证。",
            code = """
                number = 7
                if number % 2 == 0:
                    print("偶数")
                else:
                    print("奇数")
            """.trimIndent(),
            question = "这段代码会输出什么？",
            options = listOf("偶数", "奇数", "7", "报错"),
            answerIndex = 1,
            explanation = "7 除以 2 的余数是 1，条件为 False，因此执行 else 分支。",
            hints = listOf(
                "% 表示取余数。",
                "偶数除以 2 的余数才是 0。",
            ),
        ),
        TrainingExercise(
            id = "predict-list",
            lessonId = "list",
            type = TrainingType.PREDICT_OUTPUT,
            title = "列表追加",
            prompt = "注意列表在什么位置被修改。",
            code = """
                numbers = [1, 2]
                numbers.append(3)
                print(numbers)
            """.trimIndent(),
            question = "这段代码会输出什么？",
            options = listOf("[1, 2]", "[1, 2, 3]", "3", "报错"),
            answerIndex = 1,
            explanation = "append(3) 会把 3 加到列表末尾，原来的列表变成 [1, 2, 3]。",
            hints = listOf(
                "append 修改的是原列表。",
                "print 输出的是修改后的完整列表。",
            ),
        ),
        TrainingExercise(
            id = "predict-dict",
            lessonId = "dict",
            type = TrainingType.PREDICT_OUTPUT,
            title = "字典读取",
            prompt = "找到键对应的值。",
            code = """
                person = {"name": "小林", "city": "上海"}
                print(person["name"])
            """.trimIndent(),
            question = "这段代码会输出什么？",
            options = listOf("name", "小林", "上海", "报错"),
            answerIndex = 1,
            explanation = "字典通过键 \"name\" 找到对应的值 \"小林\"。",
            hints = listOf("方括号里的是键，不是位置编号。"),
        ),
        TrainingExercise(
            id = "complete-range",
            lessonId = "for",
            type = TrainingType.COMPLETE_CODE,
            title = "输出 1 到 100",
            prompt = "补全 range，让程序输出 1、2、3 一直到 100。",
            code = "for number in range(____):\n    print(number)",
            question = "在编辑器中补全代码后点击检查。",
            explanation = "range(1, 101) 会产生 1 到 100。结束值 101 本身不会出现。",
            hints = listOf(
                "range 的起点是 1。",
                "想要包含 100，结束值要写 101。",
            ),
            starterCode = "for number in range(____):\n    print(number)",
            requiredSnippets = listOf("for", "range(1,101)", "print"),
            referenceSolution = "for number in range(1, 101):\n    print(number)",
        ),
        TrainingExercise(
            id = "complete-function",
            lessonId = "function",
            type = TrainingType.COMPLETE_CODE,
            title = "补全求和函数",
            prompt = "让 add 函数返回两个参数的和。",
            code = "def add(a, b):\n    ____",
            question = "在编辑器中补全函数体后点击检查。",
            explanation = "函数体使用 return a + b，把计算结果返回给调用处。",
            hints = listOf(
                "函数需要把结果交回调用处。",
                "使用关键字 return。",
            ),
            starterCode = "def add(a, b):\n    ____",
            requiredSnippets = listOf("defadd(a,b)", "returna+b"),
            referenceSolution = "def add(a, b):\n    return a + b",
        ),
        TrainingExercise(
            id = "complete-dict-get",
            lessonId = "dict",
            type = TrainingType.COMPLETE_CODE,
            title = "安全读取联系人",
            prompt = "键不存在时不要报错，而是返回“未找到”。",
            code = """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.____
                print(phone)
            """.trimIndent(),
            question = "补全字典读取代码后点击检查。",
            explanation = "使用 contacts.get(name, \"未找到\")，不存在键时会返回默认值。",
            hints = listOf(
                "字典的 get 方法可以设置默认值。",
                "要把变量 name 当作键传进去。",
            ),
            starterCode = """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.____
                print(phone)
            """.trimIndent(),
            requiredSnippets = listOf("contacts.get(name,\"未找到\")", "print"),
            referenceSolution = """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.get(name, "未找到")
                print(phone)
            """.trimIndent(),
        ),
        TrainingExercise(
            id = "complete-file-write",
            lessonId = "file",
            type = TrainingType.COMPLETE_CODE,
            title = "写入文本文件",
            prompt = "以写入模式打开文件，并写入一行内容。",
            code = """
                with open("notes.txt", ____) as file:
                    file.____("今天学习了 Python")
            """.trimIndent(),
            question = "补全打开模式和写入方法后点击检查。",
            explanation = "写入模式是 \"w\"，file.write(...) 会把字符串写入文件。",
            hints = listOf(
                "只写内容应使用 write 模式。",
                "打开模式的参数是字符串 \"w\"。",
            ),
            starterCode = """
                with open("notes.txt", ____) as file:
                    file.____("今天学习了 Python")
            """.trimIndent(),
            requiredSnippets = listOf("open(\"notes.txt\",\"w\")", "file.write"),
            referenceSolution = """
                with open("notes.txt", "w") as file:
                    file.write("今天学习了 Python")
            """.trimIndent(),
        ),
        TrainingExercise(
            id = "debug-name",
            lessonId = "errors",
            type = TrainingType.DEBUG_LAB,
            title = "变量名拼写错误",
            prompt = "先判断哪一行有问题，再修改代码让它正常运行。",
            code = """
                name = "Tom"
                print(nam)
            """.trimIndent(),
            question = "请在编辑器中修复错误。",
            explanation = "定义的是 name，打印时却写成了 nam，Python 找不到这个名称。",
            hints = listOf(
                "错误类型通常是 NameError。",
                "比较 print 里的名字和第一行变量名。",
            ),
            starterCode = """
                name = "Tom"
                print(nam)
            """.trimIndent(),
            requiredSnippets = listOf("name=\"Tom\"", "print(name)"),
            forbiddenSnippets = listOf("print(nam)"),
            referenceSolution = "name = \"Tom\"\nprint(name)",
        ),
        TrainingExercise(
            id = "debug-compare",
            lessonId = "if",
            type = TrainingType.DEBUG_LAB,
            title = "比较运算符写错",
            prompt = "修复条件判断，让程序能够正常运行。",
            code = """
                score = 85
                if score = 85:
                    print("正确")
            """.trimIndent(),
            question = "请在编辑器中修复错误。",
            explanation = "= 是赋值，== 才是比较是否相等。if 条件中应使用 ==。",
            hints = listOf(
                "错误会在运行代码之前被 Python 发现。",
                "检查 if 条件中的等号数量。",
            ),
            starterCode = """
                score = 85
                if score = 85:
                    print("正确")
            """.trimIndent(),
            requiredSnippets = listOf("ifscore==85:", "print"),
            forbiddenSnippets = listOf("ifscore=85:"),
            referenceSolution = "score = 85\nif score == 85:\n    print(\"正确\")",
        ),
        TrainingExercise(
            id = "debug-range",
            lessonId = "for",
            type = TrainingType.DEBUG_LAB,
            title = "少输出了一个数字",
            prompt = "程序应该输出 1 到 5，但现在只输出到 4。",
            code = """
                for number in range(1, 5):
                    print(number)
            """.trimIndent(),
            question = "请在编辑器中修复范围。",
            explanation = "range 不包含结束值，要输出 5，结束值需要写成 6。",
            hints = listOf(
                "先列出 range(1, 5) 实际产生的数字。",
                "把结束值增加 1。",
            ),
            starterCode = """
                for number in range(1, 5):
                    print(number)
            """.trimIndent(),
            requiredSnippets = listOf("range(1,6)", "print"),
            forbiddenSnippets = listOf("range(1,5)"),
            referenceSolution = "for number in range(1, 6):\n    print(number)",
        ),
        TrainingExercise(
            id = "debug-list-method",
            lessonId = "list",
            type = TrainingType.DEBUG_LAB,
            title = "列表方法不存在",
            prompt = "把数字加入列表，但当前方法名不正确。",
            code = """
                scores = [80, 90]
                scores.add(100)
                print(scores)
            """.trimIndent(),
            question = "请在编辑器中修复方法名。",
            explanation = "列表在末尾添加元素使用 append，add 不是列表方法。",
            hints = listOf(
                "错误类型通常是 AttributeError。",
                "回忆列表添加元素使用哪个方法。",
            ),
            starterCode = """
                scores = [80, 90]
                scores.add(100)
                print(scores)
            """.trimIndent(),
            requiredSnippets = listOf("scores.append(100)", "print"),
            forbiddenSnippets = listOf("scores.add(100)"),
            referenceSolution = "scores = [80, 90]\nscores.append(100)\nprint(scores)",
        ),
    )

    fun byId(id: String): TrainingExercise? = all.firstOrNull { it.id == id }

    fun byType(type: TrainingType): List<TrainingExercise> = all.filter { it.type == type }

    fun byIds(ids: Set<String>): List<TrainingExercise> = all.filter { it.id in ids }
}
