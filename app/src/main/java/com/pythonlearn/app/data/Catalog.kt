package com.pythonlearn.app.data

enum class LessonState {
    DONE,
    DOING,
    TODO,
    LOCKED,
}

data class LessonSummary(
    val id: String,
    val title: String,
    val minutes: Int,
    val state: LessonState,
)

data class CourseStage(
    val label: String,
    val name: String,
    val progress: Int,
    val lessons: List<LessonSummary>,
    val special: Boolean = false,
)

data class Quiz(
    val question: String,
    val code: String,
    val options: List<String>,
    val answerIndex: Int,
    val explanation: String,
)

data class ErrorExample(
    val title: String,
    val detail: String,
    val code: String,
)

data class LessonDetail(
    val id: String,
    val title: String,
    val stage: String,
    val level: String,
    val minutes: Int,
    val knowledge: List<String>,
    val why: List<String>,
    val purpose: String,
    val example: String,
    val exampleNotes: List<Pair<String, String>>,
    val quiz: Quiz,
    val errors: List<ErrorExample>,
    val projectCode: String,
    val legalRisk: String,
    val legalNote: String,
    val legalBasis: String,
    val legalUpdated: String,
    val next: List<LessonSummary>,
)

data class ProjectInfo(
    val id: String,
    val title: String,
    val level: String,
    val goal: String,
    val requirements: List<String>,
    val knowledge: List<String>,
    val hints: List<String>,
    val starter: String,
)

object CourseCatalog {
    private val basics = CourseStage(
        label = "第一阶段",
        name = "Python 基础",
        progress = 0,
        lessons = listOf(
            LessonSummary("python", "Python 是什么", 8, LessonState.TODO),
            LessonSummary("hello", "第一个 Python 程序", 12, LessonState.LOCKED),
            LessonSummary("print", "print() 输出", 10, LessonState.LOCKED),
            LessonSummary("input", "input() 输入", 11, LessonState.LOCKED),
            LessonSummary("variable", "变量", 14, LessonState.LOCKED),
            LessonSummary("types", "数据类型", 16, LessonState.LOCKED),
        ),
    )

    private val control = CourseStage(
        label = "第二阶段",
        name = "程序控制",
        progress = 0,
        lessons = listOf(
            LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
            LessonSummary("for", "for 循环", 18, LessonState.LOCKED),
            LessonSummary("while", "while 循环", 17, LessonState.LOCKED),
            LessonSummary("break", "break / continue", 12, LessonState.LOCKED),
            LessonSummary("nested", "嵌套与综合控制", 20, LessonState.LOCKED),
        ),
    )

    private val dataStructures = CourseStage(
        label = "第三阶段",
        name = "数据结构",
        progress = 0,
        lessons = listOf(
            LessonSummary("list", "list 列表", 19, LessonState.LOCKED),
            LessonSummary("tuple", "tuple 元组", 13, LessonState.LOCKED),
            LessonSummary("set", "set 集合", 15, LessonState.LOCKED),
            LessonSummary("dict", "dict 字典", 21, LessonState.LOCKED),
            LessonSummary("comprehension", "推导式", 18, LessonState.LOCKED),
        ),
    )

    private val functionsAndFiles = CourseStage(
        label = "第四阶段",
        name = "函数与文件",
        progress = 0,
        lessons = listOf(
            LessonSummary("function", "函数", 22, LessonState.LOCKED),
            LessonSummary("file", "读写文件", 20, LessonState.LOCKED),
            LessonSummary("module", "模块", 15, LessonState.LOCKED),
            LessonSummary("oop", "类与对象", 25, LessonState.LOCKED),
            LessonSummary("errors", "异常处理", 19, LessonState.LOCKED),
        ),
    )

    private val crawler = CourseStage(
        label = "爬虫专项",
        name = "网络与爬虫",
        progress = 0,
        lessons = listOf(
            LessonSummary("http", "HTTP 请求与响应", 18, LessonState.LOCKED),
            LessonSummary("requests", "requests 基础", 21, LessonState.LOCKED),
            LessonSummary("html", "HTML 与 BeautifulSoup", 22, LessonState.LOCKED),
            LessonSummary("session", "Cookie 与 Session", 19, LessonState.LOCKED),
            LessonSummary("api", "API 的正确用法", 17, LessonState.LOCKED),
            LessonSummary("legal", "爬虫安全与法律", 24, LessonState.TODO),
        ),
        special = true,
    )

    val stages = listOf(basics, control, dataStructures, functionsAndFiles, crawler)
    val orderedLessonIds: List<String> = stages.flatMap { stage -> stage.lessons.map { it.id } }

    fun lesson(id: String): LessonDetail? = lessons[id]

    fun lessonState(id: String, completedIds: Set<String>): LessonState {
        if (id in completedIds) return LessonState.DONE
        if (lesson(id) == null) return LessonState.LOCKED
        val index = orderedLessonIds.indexOf(id)
        if (index <= 0) return LessonState.TODO
        if (orderedLessonIds.getOrNull(index - 1) in completedIds) return LessonState.TODO
        return LessonState.LOCKED
    }

    fun stageProgress(stage: CourseStage, completedIds: Set<String>): Int {
        val completedCount = stage.lessons.count { it.id in completedIds }
        return completedCount * 100 / stage.lessons.size
    }

    fun nextLessonId(completedIds: Set<String>): String? {
        return orderedLessonIds.firstOrNull { id ->
            id !in completedIds && lesson(id) != null && lessonState(id, completedIds) == LessonState.TODO
        }
    }

    fun overallProgress(completedIds: Set<String>): Int {
        return completedIds.count { it in orderedLessonIds } * 100 / orderedLessonIds.size
    }

    val allQuizzes: List<Quiz>
        get() = lessons.values.map { it.quiz }

    fun quizByQuestion(question: String): Quiz? {
        return lessons.values.firstOrNull { it.quiz.question == question }?.quiz
    }

    private val lessons: Map<String, LessonDetail> = mapOf(
        "python" to LessonDetail(
            id = "python",
            title = "Python 是什么",
            stage = "Python 基础",
            level = "入门",
            minutes = 8,
            knowledge = listOf(
                "Python 是一种适合初学者的编程语言：写法接近自然语言，能很快看到运行结果。",
                "它的应用范围很广，包括自动化、数据处理、爬虫、AI 和 Web 开发。",
            ),
            why = listOf(
                "先了解“能做什么”，才不会把 Python 当成一堆需要背的语法。",
                "你可以从写小程序开始，慢慢扩展到处理真实文件、网页和项目。",
            ),
            purpose = "自动整理文件、抓取网页公开数据、生成报告、写 Web 接口，都是 Python 常见用途。",
            example = "print(\"Hello Python\")\nprint(\"你好，Python\")",
            exampleNotes = listOf(
                "print(" to "把内容输出到屏幕",
                "\"Hello Python\"" to "要显示的文字",
            ),
            quiz = Quiz(
                question = "运行 print(\"Hello\") 后，屏幕上会显示什么？",
                code = "print(\"Hello\")",
                options = listOf("Hello", "print", "错误", "什么也不显示"),
                answerIndex = 0,
                explanation = "print() 会把括号里的文字输出到屏幕，所以显示 Hello。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "漏掉括号或引号",
                    detail = "print 后面的括号和字符串引号需要成对出现。",
                    code = "print(Hello)  # 错\nprint(\"Hello\")  # 对",
                ),
                ErrorExample(
                    title = "中英文符号混用",
                    detail = "Python 代码使用英文标点，中文标点会导致语法错误。",
                    code = "print（\"Hello\"）  # 错\nprint(\"Hello\")  # 对",
                ),
            ),
            projectCode = "# 第一课先完成一个小目标：\n# 让程序说出一句你想说的话\nprint(\"我学会了 Python\")",
            legalRisk = "🟢 较低风险",
            legalNote = "本节只介绍 Python 是什么，属于通用编程知识。开始具体项目时再根据访问对象、数据类型和使用目的评估合规性。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-04",
            next = listOf(
                LessonSummary("print", "print() 输出", 10, LessonState.LOCKED),
                LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
            ),
        ),
        "hello" to LessonDetail(
            id = "hello",
            title = "第一个 Python 程序",
            stage = "Python 基础",
            level = "入门",
            minutes = 12,
            knowledge = listOf(
                "写第一个程序不用复杂。用 print() 把文字显示出来，程序就运行了。",
                "文件保存后运行，从上到下逐行执行。",
            ),
            why = listOf(
                "第一课的目标不是背语法，而是让“写代码 → 运行 → 看到结果”这个循环真实发生一次。",
            ),
            purpose = "每一个自动化和项目都从一个能运行的小程序开始。",
            example = "print(\"Hello Python\")\nprint(\"这是你的第一个程序\")",
            exampleNotes = listOf(
                "print(" to "把内容输出到屏幕",
                "print(\"Hello Python\")" to "英文和中文文字都能显示",
            ),
            quiz = Quiz(
                question = "哪一行程序可以让屏幕显示 Hello?",
                code = "# 选一个答案\nprint(\"Hello\")",
                options = listOf("print(\"Hello\")", "print(Hello)", "显示 Hello", "print Hello"),
                answerIndex = 0,
                explanation = "print 后需要有括号，文字需要用英文引号包裹。",
            ),
            errors = listOf(
                ErrorExample("忘记引号", "字符串需要放在引号里。", "print(Hello)  # 错"),
                ErrorExample("文件没有保存", "改了代码却看到旧结果，通常是运行前没有保存。", "# 保存后再运行"),
            ),
            projectCode = "# 试着把你想说的话放进 print 里\nprint(\"Hello Python\")",
            legalRisk = "🟢 较低风险",
            legalNote = "这是通用入门编程练习，不涉及第三方数据访问。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-04",
            next = listOf(
                LessonSummary("print", "print() 输出", 10, LessonState.LOCKED),
                LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
            ),
        ),
        "print" to LessonDetail(
            id = "print",
            title = "print() 输出",
            stage = "Python 基础",
            level = "入门",
            minutes = 10,
            knowledge = listOf(
                "print() 是最常用的输出方式，可以把文字、数字和变量显示在屏幕上。",
                "括号里的多个内容用逗号隔开，输出时自动用空格连接。",
            ),
            why = listOf(
                "你看到的报错、结果、调试信息，都依赖输出能力。",
            ),
            purpose = "查看运行结果、调试程序、把程序处理后的内容告诉用户。",
            example = "print(\"Hello\", \"Python\")\nprint(1 + 1)",
            exampleNotes = listOf(
                "print(\"Hello\", \"Python\")" to "输出 Hello Python",
                "print(1 + 1)" to "输出 2",
            ),
            quiz = Quiz(
                question = "print(2 + 3) 会输出什么？",
                code = "print(2 + 3)",
                options = listOf("2 + 3", "5", "23", "错误"),
                answerIndex = 1,
                explanation = "Python 会先计算 2 + 3，再把结果 5 输出。",
            ),
            errors = listOf(
                ErrorExample("忘记括号", "print 是一个函数，调用时必须带括号。", "print \"Hello\"  # 错\nprint(\"Hello\")  # 对"),
                ErrorExample("忘记引号", "文字内容需要引号，数字不需要。", "print(Hello)  # 错\nprint(\"Hello\")  # 对"),
            ),
            projectCode = "name = \"Python\"\nprint(\"我在学习\", name)",
            legalRisk = "🟢 较低风险",
            legalNote = "输出功能属于通用编程基础。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-04",
            next = listOf(
                LessonSummary("variable", "变量", 14, LessonState.LOCKED),
                LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
            ),
        ),
        "input" to LessonDetail(
            id = "input",
            title = "input() 输入",
            stage = "Python 基础",
            level = "入门",
            minutes = 11,
            knowledge = listOf(
                "input() 会在运行台输入区读取一行内容，并把读取到的内容作为字符串返回。",
                "它可以帮助程序根据用户不同输入做出不同反应，而不是永远只输出固定内容。",
            ),
            why = listOf(
                "很多程序的价值来自“接收用户信息再处理”：姓名、成绩、数量、搜索词，都需要输入。",
                "input() 是你第一次让程序和外界的用户发生真实对话。",
            ),
            purpose = "表单信息收集、命令行工具参数、练习题中的成绩判断、简单问答程序都依赖输入。",
            example = "name = input(\"请输入名字：\")\nprint(\"你好\", name)",
            exampleNotes = listOf(
                "input(\"请输入名字：\")" to "先显示提示文字，再等待输入区的内容",
                "name" to "变量保存输入后返回的字符串",
            ),
            quiz = Quiz(
                question = "运行台输入区填了 小林，运行下面代码会输出什么？",
                code = "name = input(\"名字：\")\nprint(\"你好，\" + name)",
                options = listOf("你好，小林", "名字：小林", "小林", "会报错"),
                answerIndex = 0,
                explanation = "input 返回小林，字符串相加后得到 你好，小林。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "忘了输入区内容",
                    detail = "代码使用 input() 时，运行台输入区至少要有一行内容，否则会提示输入用完。",
                    code = "name = input()\nprint(name)",
                ),
                ErrorExample(
                    title = "把输入内容当数字用",
                    detail = "input() 返回的是字符串。需要计算时，先转成 int() 或 float()。",
                    code = "age = input(\"年龄：\")\nage = int(age)",
                ),
            ),
            projectCode = "# 先把名字读进来，再和固定的问候语组合\nname = input(\"你的名字：\")\nprint(\"欢迎学习 Python，\" + name)",
            legalRisk = "🟢 较低风险",
            legalNote = "输入功能属于通用编程基础。实际项目收集姓名、年龄等个人信息时，应遵循最小必要、明示目的并取得合法依据。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("variable", "变量", 14, LessonState.LOCKED),
                LessonSummary("types", "数据类型", 16, LessonState.LOCKED),
            ),
        ),
        "variable" to LessonDetail(
            id = "variable",
            title = "变量",
            stage = "Python 基础",
            level = "入门",
            minutes = 14,
            knowledge = listOf(
                "变量像一个贴了标签的盒子。你可以把文字、数字、列表等数据放进去，之后用标签名来使用它。",
                "Python 变量不需要提前声明类型，直接赋值即可：变量名 = 值。",
            ),
            why = listOf(
                "真实程序里的数据是不断变化的：同一个变量今天保存成绩，下一次保存新的成绩。",
                "不用变量，你就只能写死每一处内容，程序无法处理变化。",
            ),
            purpose = "保存用户输入、计算结果、列表元素，让代码可复用并更容易读懂。",
            example = "name = \"小林\"\nage = 18\nscore = age + 2\nprint(name, score)",
            exampleNotes = listOf(
                "name = \"小林\"" to "把文字放进变量 name",
                "score = age + 2" to "先计算结果 20，再放进变量 score",
                "print(name, score)" to "读取两个变量的值",
            ),
            quiz = Quiz(
                question = "运行下面代码，会输出什么？",
                code = "x = 8\nx = x + 5\nprint(x)",
                options = listOf("8", "13", "x + 5", "会报错"),
                answerIndex = 1,
                explanation = "x = x + 5 会先取出旧的 8，加 5 得到 13，再存回 x。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "变量名拼写不一致",
                    detail = "Python 区分大小写，age 和 Age 是两个不同名称。",
                    code = "name = \"小林\"\nprint(nmae)  # 拼写错误",
                ),
                ErrorExample(
                    title = "给文字内容忘记引号",
                    detail = "字符串必须加引号，否则 Python 会认为它是变量名。",
                    code = "city = 北京  # 错\ncity = \"北京\"  # 对",
                ),
            ),
            projectCode = "# 先收集信息，再做一点计算\nname = input(\"名字：\")\nage = int(input(\"年龄：\"))\nprint(name, \"明年\", age + 1, \"岁\")",
            legalRisk = "🟢 较低风险",
            legalNote = "变量是通用编程知识。用变量保存个人信息时，应当只保存完成任务所需的信息，并限制使用范围。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("types", "数据类型", 16, LessonState.LOCKED),
                LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
            ),
        ),
        "types" to LessonDetail(
            id = "types",
            title = "数据类型",
            stage = "Python 基础",
            level = "入门",
            minutes = 16,
            knowledge = listOf(
                "Python 中常见类型有字符串 str、整数 int、浮点数 float、布尔 bool 和列表 list。",
                "不同类型适合不同操作。字符串用来显示文字，数字用来计算，布尔值表示真或假。",
            ),
            why = listOf(
                "报错里的 TypeError 大多和类型有关：数字不能直接和文字相加，input 返回的是字符串。",
                "知道类型，才能判断何时需要 int()、str()、len() 等转换和函数。",
            ),
            purpose = "把用户输入转成数字、生成报告、判断空数据、统计列表长度，类型概念贯穿所有真实程序。",
            example = "age = \"18\"\nreal_age = int(age)\nprint(real_age + 1)\nprint(type(real_age))",
            exampleNotes = listOf(
                "age = \"18\"" to "这是字符串，不是数字",
                "int(age)" to "把字符串 18 转成整数 18",
                "type(real_age)" to "查看当前类型",
            ),
            quiz = Quiz(
                question = "运行 int(\"12\") + 3，会得到什么？",
                code = "print(int(\"12\") + 3)",
                options = listOf("123", "15", "会报错", "\"12\" 3"),
                answerIndex = 1,
                explanation = "int(\"12\") 转成整数 12，再加 3 得到 15。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "字符串和数字直接相加",
                    detail = "\"年龄\" + 18 会报 TypeError，需要 str(18) 或先转为数字。",
                    code = "print(\"年龄\" + 18)  # 错\nprint(\"年龄\" + str(18))  # 对",
                ),
                ErrorExample(
                    title = "不能把非数字转成 int",
                    detail = "int(\"abc\") 没有可转换内容，会报 ValueError。",
                    code = "int(\"abc\")  # 会报错",
                ),
            ),
            projectCode = "# 收集价格和数量，完成金额计算\nprice = float(input(\"单价：\"))\ncount = int(input(\"数量：\"))\nprint(\"总价\", price * count)",
            legalRisk = "🟢 较低风险",
            legalNote = "数据类型是通用编程知识。处理真实数据时，身份、地址、联系方式等个人信息仍应遵循收集与使用的最小必要原则。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("if", "if 条件判断", 18, LessonState.LOCKED),
                LessonSummary("list", "list 列表", 19, LessonState.LOCKED),
            ),
        ),
        "if" to LessonDetail(
            id = "if",
            title = "if 条件判断",
            stage = "程序控制",
            level = "基础",
            minutes = 18,
            knowledge = listOf(
                "if 让程序走到岔路口时，根据一个“是不是真的”的条件，选择执行其中一部分代码。",
                "写 if 时，先写条件和冒号，再把符合条件时要运行的代码放进下一层缩进。",
            ),
            why = listOf(
                "现实中的程序很少只是从上到下执行。用户输入什么、页面返回什么、数据是否为空，都会让程序做出不同的决定。",
                "if 是把这些决定写下来最基本的方式。",
            ),
            purpose = "成绩判断、表单校验、商品库存检查、根据用户身份显示不同内容，都会用到条件判断。",
            example = "score = 85\nif score >= 60:\n    print(\"通过\")\nelse:\n    print(\"继续加油\")",
            exampleNotes = listOf(
                "score = 85" to "保存成绩：右边先计算，再放进左边的变量",
                "if score >= 60:" to "条件：成绩是否大于等于 60",
                "    print(\"通过\")" to "条件成立时才执行；空格表示它属于 if",
                "else:" to "不满足条件时走这一条路",
            ),
            quiz = Quiz(
                question = "运行下面的代码，屏幕会输出什么？",
                code = "x = 7\nif x % 2 == 0:\n    print(\"偶数\")\nelse:\n    print(\"奇数\")",
                options = listOf("偶数", "奇数", "什么也不输出", "程序报错"),
                answerIndex = 1,
                explanation = "7 除以 2 的余数是 1，所以条件为 False，程序会执行 else 后的 print(\"奇数\")。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "把 = 和 == 混淆",
                    detail = "= 是赋值，== 才是比较是否相等。if 后面需要用 ==。",
                    code = "if score = 85:  # 错\nif score == 85:  # 对",
                ),
                ErrorExample(
                    title = "忘记冒号",
                    detail = "if、elif、else 那一行结束时必须有冒号。",
                    code = "if score >= 60  # 错\nif score >= 60:  # 对",
                ),
                ErrorExample(
                    title = "缩进不一致",
                    detail = "同一段 if 代码要使用同样的缩进，一般统一使用 4 个空格。",
                    code = "if ok:\n    print(\"A\")\n   print(\"B\")  # 缩进不齐",
                ),
            ),
            projectCode = "guess = int(input(\"猜一个数字：\"))\n\nif guess == secret:\n    print(\"猜对了\")\nelif guess < secret:\n    print(\"再大一点\")\nelse:\n    print(\"再小一点\")",
            legalRisk = "🟢 较低风险",
            legalNote = "本节只介绍 Python 基础编程知识。学习与在自己程序中编写这些语句通常风险较低。如果后续用程序访问第三方网站或处理第三方数据，需要结合网站规则、数据性质、访问方式和使用目的另行判断。",
            legalBasis = "参考原则：网络安全法、数据安全法、个人信息保护法",
            legalUpdated = "2026-09-04",
            next = listOf(
                LessonSummary("for", "for 循环", 18, LessonState.LOCKED),
                LessonSummary("while", "while 循环", 17, LessonState.TODO),
            ),
        ),
        "for" to LessonDetail(
            id = "for",
            title = "for 循环",
            stage = "程序控制",
            level = "基础",
            minutes = 18,
            knowledge = listOf(
                "for 用来重复做有规律的事情。它会把一个可迭代对象里的元素依次取出来，每取一次执行一次循环体。",
                "range(1, 6) 会产生 1、2、3、4、5，所以下面的代码会输出 1 到 5。",
            ),
            why = listOf(
                "处理列表、读取文件每一行时，如果一段代码要执行很多次，不应该把它复制粘贴几十遍。",
                "for 让你写一次代码，交给程序去重复执行。",
            ),
            purpose = "批量转换数据、遍历列表生成报表、下载多个文件、对多页结果做统一处理，都是 for 的常见场景。",
            example = "for i in range(1, 6):\n    print(i)",
            exampleNotes = listOf(
                "for i in range(1, 6):" to "从 range 里依次取出 i",
                "    print(i)" to "每取一个数字就执行一次",
            ),
            quiz = Quiz(
                question = "range(2, 5) 会产生哪些数字？",
                code = "for n in range(2, 5):\n    print(n)",
                options = listOf("2, 3, 4", "2, 3, 4, 5", "3, 4, 5", "1, 2, 3, 4"),
                answerIndex = 0,
                explanation = "range(start, stop) 会从 start 开始，到 stop 之前结束，所以这里取到 2、3、4。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "漏掉冒号",
                    detail = "for 开头这一行必须以冒号结尾，下一行再写要重复的代码。",
                    code = "for i in range(3)  # 错\nfor i in range(3):  # 对",
                ),
                ErrorExample(
                    title = "循环体没有缩进",
                    detail = "要重复执行的代码必须比 for 多一层缩进。",
                    code = "for i in range(3):\nprint(i)  # 需要缩进",
                ),
                ErrorExample(
                    title = "把 stop 当包含值",
                    detail = "range(1, 5) 不包含 5。需要包含它时写成 range(1, 6)。",
                    code = "range(1, 5)  # 1,2,3,4\nrange(1, 6)  # 1,2,3,4,5",
                ),
            ),
            projectCode = "for level in [\"入门\", \"基础\", \"综合\", \"高级\", \"毕业\"]:\n    print(\"开始\", level, \"项目\")",
            legalRisk = "🟢 较低风险",
            legalNote = "for 循环属于通用编程技术。学习循环本身不需要特殊法律判断；把它用于实际项目时，再按访问对象和数据用途评估。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-04",
            next = listOf(
                LessonSummary("while", "while 循环", 17, LessonState.TODO),
                LessonSummary("list", "list 列表", 19, LessonState.LOCKED),
            ),
        ),
        "while" to LessonDetail(
            id = "while",
            title = "while 循环",
            stage = "程序控制",
            level = "基础",
            minutes = 17,
            knowledge = listOf(
                "while 会在条件为 True 时反复执行循环体，直到条件变成 False 才继续往后走。",
                "循环体里必须改变条件相关的变量，否则会变成无限循环。",
            ),
            why = listOf(
                "猜数字要“一直猜，直到猜对”，文件处理要“一直读到没有内容”，这时 while 比 for 更自然。",
                "while 擅长处理“不知道会重复多少次”的任务。",
            ),
            purpose = "实现直到猜对才停止、重试请求、等待用户输入正确内容等重复逻辑。",
            example = "n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1\nprint(\"开始！\")",
            exampleNotes = listOf(
                "while n > 0:" to "每次进入循环前判断条件",
                "n = n - 1" to "改变 n，让循环有机会结束",
                "print(\"开始！\")" to "条件为 False 后才会执行",
            ),
            quiz = Quiz(
                question = "运行下面的代码，第一次输出是什么？",
                code = "n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1",
                options = listOf("3", "2", "1", "没有输出"),
                answerIndex = 0,
                explanation = "第一次进入循环时 n 还是 3，所以先输出 3，再把 n 改成 2。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "忘记让条件改变",
                    detail = "循环体里没有 n = n - 1 之类代码，n 永远是 3，程序不会停下来。",
                    code = "n = 3\nwhile n > 0:\n    print(n)",
                ),
                ErrorExample(
                    title = "条件方向写反",
                    detail = "如果条件一开始就是 False，循环体一次也不会执行。",
                    code = "n = 3\nwhile n < 0:\n    print(n)",
                ),
            ),
            projectCode = "answer = 42\nguess = 0\nwhile guess != answer:\n    guess = int(input(\"猜一个数字：\"))\nprint(\"猜对了\")",
            legalRisk = "🟢 较低风险",
            legalNote = "while 是通用控制流程。真正的风险不来自循环本身，而来自循环访问的对象和数据用途。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("break", "break / continue", 12, LessonState.LOCKED),
                LessonSummary("nested", "嵌套与综合控制", 20, LessonState.LOCKED),
            ),
        ),
        "break" to LessonDetail(
            id = "break",
            title = "break / continue",
            stage = "程序控制",
            level = "基础",
            minutes = 12,
            knowledge = listOf(
                "break 会立即结束当前循环，continue 会跳过本次循环剩下的代码，直接进入下一次。",
                "它们让循环可以在找到答案时提前停止，或跳过不需要处理的数据。",
            ),
            why = listOf(
                "搜索到目标后没必要继续遍历全部数据；遇到无效数据时也要跳过而不是停止整个程序。",
                "这两种语句让循环更精准。",
            ),
            purpose = "提前结束搜索、过滤无效数据、实现退出菜单等。",
            example = "for n in range(1, 6):\n    if n == 3:\n        continue\n    if n == 5:\n        break\n    print(n)",
            exampleNotes = listOf(
                "if n == 3: continue" to "遇到 3 时跳过后面的 print",
                "if n == 5: break" to "n 到 5 时直接结束循环",
                "print(n)" to "会输出 1、2、4",
            ),
            quiz = Quiz(
                question = "下面代码会输出哪些数字？",
                code = "for n in range(1, 6):\n    if n == 3:\n        continue\n    if n == 5:\n        break\n    print(n)",
                options = listOf("1 2 4", "1 2 3 4", "1 2 3", "1 2 4 5"),
                answerIndex = 0,
                explanation = "3 被 continue 跳过，5 触发 break，所以只输出 1、2、4。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "break 不在循环里",
                    detail = "break 只能写在 for 或 while 循环内部，否则会报错。",
                    code = "if n == 3:\n    break  # 不在循环里会报错",
                ),
                ErrorExample(
                    title = "continue 后忘记要处理的代码",
                    detail = "continue 会跳过它之后的所有代码，需要重复执行的代码应写在后面。",
                    code = "for n in range(3):\n    continue\n    print(n)  # 不会执行",
                ),
            ),
            projectCode = "for user in [\"小明\", \"\", \"小林\"]:\n    if not user:\n        continue\n    print(\"处理\", user)",
            legalRisk = "🟢 较低风险",
            legalNote = "break 和 continue 是通用编程知识。在真实项目中提前终止访问或跳过数据，仍要遵守访问对象与数据使用规则。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("nested", "嵌套与综合控制", 20, LessonState.TODO),
                LessonSummary("list", "list 列表", 19, LessonState.LOCKED),
            ),
        ),
        "nested" to LessonDetail(
            id = "nested",
            title = "嵌套与综合控制",
            stage = "程序控制",
            level = "基础",
            minutes = 20,
            knowledge = listOf(
                "嵌套是指 if、for、while 等结构彼此包含。外层每执行一次，内层可能完整执行一轮。",
                "缩进决定代码属于哪一层，写嵌套时要尤其注意。",
            ),
            why = listOf(
                "真实任务很少只有一层循环：多个班级里的学生、多个页面里的数据，都需要多层处理。",
                "嵌套把复杂任务拆成“外层分组、内层逐项”的结构。",
            ),
            purpose = "批量处理分组数据、二维表格、多级菜单等。",
            example = "for level in [\"入门\", \"进阶\"]:\n    for task in [\"复习\", \"练习\"]:\n        print(level, task)",
            exampleNotes = listOf(
                "外层循环" to "依次取出 入门、进阶",
                "内层循环" to "对每个 level 都完整执行一轮",
                "print(level, task)" to "一共输出 4 行",
            ),
            quiz = Quiz(
                question = "运行上面的两层循环，一共会输出几行？",
                code = "for level in [\"入门\", \"进阶\"]:\n    for task in [\"复习\", \"练习\"]:\n        print(level, task)",
                options = listOf("2 行", "4 行", "6 行", "会报错"),
                answerIndex = 1,
                explanation = "外层有 2 个值，内层有 2 个值，2 乘 2 等于 4 行。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "缩进不属于预期层",
                    detail = "print 多缩进或少缩进，就会改变它属于哪一层循环。",
                    code = "for a in range(2):\nfor b in range(2):\n    print(a, b)  # 缩进错误",
                ),
                ErrorExample(
                    title = "循环层数过深",
                    detail = "超过三层嵌套后代码很难读。应先把内层逻辑抽成函数。",
                    code = "# 深嵌套应拆成函数",
                ),
            ),
            projectCode = "products = [[\"可乐\", 3], [\"牛奶\", 5]]\nfor product in products:\n    print(product[0], product[1], \"元\")",
            legalRisk = "🟢 较低风险",
            legalNote = "嵌套控制属于通用编程技术。批量访问外部对象时，频率、范围和使用目的都应保持合理。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("list", "list 列表", 19, LessonState.TODO),
                LessonSummary("function", "函数", 22, LessonState.LOCKED),
            ),
        ),
        "list" to LessonDetail(
            id = "list",
            title = "list 列表",
            stage = "数据结构",
            level = "基础",
            minutes = 19,
            knowledge = listOf(
                "列表用方括号表示，可以按顺序保存多个数据：[85, 92, 76]。",
                "下标从 0 开始，scores[0] 是第一个元素；append() 添加末尾元素，len() 获取长度。",
            ),
            why = listOf(
                "只有一个成绩变量不够用。真实程序需要把一组商品、用户或日志放在一起遍历。",
                "列表是 Python 中最常用的“装一组数据”的容器。",
            ),
            purpose = "保存待办列表、批量遍历数据、按位置访问、动态增加元素。",
            example = "scores = [85, 92, 76]\nscores.append(88)\nprint(scores[1])\nprint(len(scores))",
            exampleNotes = listOf(
                "scores[1]" to "取第二个元素 92",
                "append(88)" to "在末尾新增 88",
                "len(scores)" to "长度变成 4",
            ),
            quiz = Quiz(
                question = "运行下面代码会输出什么？",
                code = "names = [\"小林\", \"小明\", \"小红\"]\nprint(names[0])",
                options = listOf("小林", "小明", "小红", "会报错"),
                answerIndex = 0,
                explanation = "列表下标从 0 开始，names[0] 是第一个元素小林。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "下标越界",
                    detail = "列表只有 3 个元素时，names[3] 会报 IndexError。",
                    code = "names = [\"a\", \"b\", \"c\"]\nprint(names[3])",
                ),
                ErrorExample(
                    title = "忘记元素之间的逗号",
                    detail = "列表元素之间必须用英文逗号分隔。",
                    code = "scores = [90 85]  # 错\nscores = [90, 85]  # 对",
                ),
            ),
            projectCode = "tasks = []\ntask = input(\"待办：\")\nwhile task:\n    tasks.append(task)\n    task = input(\"继续输入，空行结束：\")\nfor task in tasks:\n    print(\"待办\", task)",
            legalRisk = "🟢 较低风险",
            legalNote = "列表是通用数据结构。批量保存联系人、用户等个人信息时，应先确认存储目的与保存期限。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("tuple", "tuple 元组", 13, LessonState.LOCKED),
                LessonSummary("set", "set 集合", 15, LessonState.LOCKED),
            ),
        ),
        "tuple" to LessonDetail(
            id = "tuple",
            title = "tuple 元组",
            stage = "数据结构",
            level = "基础",
            minutes = 13,
            knowledge = listOf(
                "元组用圆括号表示，和列表很像，但创建后不能修改：point = (3, 5)。",
                "不能修改让元组更安全，适合保存一组固定且相关的值。",
            ),
            why = listOf(
                "坐标、颜色 RGB、函数返回的多个结果，都适合用元组表达“固定的一组值”。",
                "元组还可以防止代码不小心改写重要配置。",
            ),
            purpose = "保存不会改变的配置、解包多个返回值、作为字典键等。",
            example = "point = (3, 5)\nx, y = point\nprint(\"坐标\", x, y)\nprint(len(point))",
            exampleNotes = listOf(
                "(3, 5)" to "创建含两个值的元组",
                "x, y = point" to "解包：把 3 给 x，把 5 给 y",
                "len(point)" to "元组长度是 2",
            ),
            quiz = Quiz(
                question = "运行下面代码，会发生什么？",
                code = "p = (1, 2)\np[0] = 9",
                options = listOf("p 变成 (9, 2)", "会报错", "p 变成 [9, 2]", "没有变化"),
                answerIndex = 1,
                explanation = "元组创建后不可修改，执行赋值会抛 TypeError。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "尝试修改元组",
                    detail = "需要可变数据时应使用 list，而不是 tuple。",
                    code = "p = (1, 2)\np[0] = 9  # 会报错",
                ),
                ErrorExample(
                    title = "单元素元组漏逗号",
                    detail = "(1) 只是数字 1，(1,) 才是只有一个元素的元组。",
                    code = "one = (1)  # int\none = (1,)  # tuple",
                ),
            ),
            projectCode = "rgb = (18, 128, 82)\nred, green, blue = rgb\nprint(\"RGB\", red, green, blue)",
            legalRisk = "🟢 较低风险",
            legalNote = "元组是通用数据结构，本节不涉及特殊法律风险。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("set", "set 集合", 15, LessonState.TODO),
                LessonSummary("dict", "dict 字典", 21, LessonState.LOCKED),
            ),
        ),
        "set" to LessonDetail(
            id = "set",
            title = "set 集合",
            stage = "数据结构",
            level = "基础",
            minutes = 15,
            knowledge = listOf(
                "集合用花括号表示，会自动去掉重复元素，并支持快速判断“元素是否存在”。",
                "集合元素不能重复，也不能放入列表这种可变数据。",
            ),
            why = listOf(
                "去重、找共同好友、判断某个词是否已经处理过，这些任务用集合写起来最直接。",
                "集合在做存在性判断时通常比列表更快。",
            ),
            purpose = "数据去重、集合交集差集、快速判断是否出现过。",
            example = "tags = [\"python\", \"基础\", \"python\"]\nunique = set(tags)\nprint(\"python\" in unique)\nprint(len(unique))",
            exampleNotes = listOf(
                "set(tags)" to "去掉重复的 python",
                "\"python\" in unique" to "判断元素是否存在",
                "len(unique)" to "只剩 2 个不同值",
            ),
            quiz = Quiz(
                question = "运行后 len(unique) 是多少？",
                code = "values = [\"A\", \"B\", \"A\", \"C\"]\nunique = set(values)\nprint(len(unique))",
                options = listOf("3", "4", "2", "会报错"),
                answerIndex = 0,
                explanation = "重复的 A 只保留一个，所以集合里有 A、B、C 共 3 个元素。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "把列表放进集合",
                    detail = "列表可修改，不能作为集合元素。",
                    code = "s = {[1, 2]}  # 会报错",
                ),
                ErrorExample(
                    title = "依赖集合顺序",
                    detail = "集合不保证固定顺序，需要顺序时使用列表。",
                    code = "# set 的输出顺序可能变化",
                ),
            ),
            projectCode = "crawled = {\"home\", \"list\"}\nnew_url = \"detail\"\nif new_url not in crawled:\n    print(\"需要处理\", new_url)",
            legalRisk = "🟢 较低风险",
            legalNote = "集合是通用数据结构。即使做了去重，也不等于访问方式一定合规，仍需确认访问授权和数据用途。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("dict", "dict 字典", 21, LessonState.TODO),
                LessonSummary("comprehension", "推导式", 18, LessonState.LOCKED),
            ),
        ),
        "dict" to LessonDetail(
            id = "dict",
            title = "dict 字典",
            stage = "数据结构",
            level = "基础",
            minutes = 21,
            knowledge = listOf(
                "字典用花括号保存键值对：user = {\"name\": \"小林\", \"level\": 2}。",
                "通过键取值比位置更明确：user[\"name\"] 得到小林；get() 可以在找不到时给默认值。",
            ),
            why = listOf(
                "真实数据通常不是一堆孤立数字，而是“名称、年龄、地址”这样一组相关属性。",
                "字典让每条数据有明确含义，也方便按名字查找。",
            ),
            purpose = "保存用户资料、网页返回的 JSON、配置信息、统计结果等。",
            example = "user = {\"name\": \"小林\", \"level\": 2}\nprint(user[\"name\"])\nuser[\"score\"] = 100\nprint(user.get(\"city\", \"未知\"))",
            exampleNotes = listOf(
                "user[\"name\"]" to "用键 name 取值",
                "user[\"score\"] = 100" to "新增一个键值对",
                "get(\"city\", \"未知\")" to "找不到 city 时返回 未知",
            ),
            quiz = Quiz(
                question = "运行下面代码，会输出什么？",
                code = "d = {\"a\": 1, \"b\": 2}\nprint(d[\"a\"] + d[\"b\"])",
                options = listOf("3", "12", "ab", "会报错"),
                answerIndex = 0,
                explanation = "d[\"a\"] 是 1，d[\"b\"] 是 2，相加得到 3。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "访问不存在的键",
                    detail = "直接使用 d[\"city\"] 在键不存在时会报 KeyError，可用 get() 提供默认值。",
                    code = "user = {\"name\": \"小林\"}\nprint(user[\"city\"])  # KeyError",
                ),
                ErrorExample(
                    title = "写键名忘了引号",
                    detail = "字符串键必须加引号，否则 Python 会当成变量名。",
                    code = "user = {name: \"小林\"}  # 错\nuser = {\"name\": \"小林\"}  # 对",
                ),
            ),
            projectCode = "record = {\"name\": \"小林\", \"course\": \"Python\", \"score\": 88}\nprint(record[\"name\"], record[\"course\"], record[\"score\"])",
            legalRisk = "🟢 较低风险",
            legalNote = "字典是通用数据结构。用字典保存可识别到个人的信息时，应限制收集范围并保护存储安全。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("comprehension", "推导式", 18, LessonState.TODO),
                LessonSummary("function", "函数", 22, LessonState.LOCKED),
            ),
        ),
        "comprehension" to LessonDetail(
            id = "comprehension",
            title = "推导式",
            stage = "数据结构",
            level = "基础",
            minutes = 18,
            knowledge = listOf(
                "列表推导式用一行代码生成新列表：squares = [n * n for n in range(1, 6)]。",
                "它本质是“对每个元素做一次转换，再收集结果”。条件还可以用 if 过滤。",
            ),
            why = listOf(
                "先用 for 循环写出结果，再改成推导式，代码会更短、更接近英语句子。",
                "推导式能减少临时变量和额外空列表。",
            ),
            purpose = "批量转换成绩、过滤无效数据、快速生成统计列表。",
            example = "squares = [n * n for n in range(1, 6)]\nprint(squares)",
            exampleNotes = listOf(
                "n * n" to "对每个 n 做的转换",
                "for n in range(1, 6)" to "数据来源",
                "结果" to "[1, 4, 9, 16, 25]",
            ),
            quiz = Quiz(
                question = "运行下面代码，会得到什么列表？",
                code = "result = [n * 2 for n in range(3)]\nprint(result)",
                options = listOf("[0, 2, 4]", "[2, 4, 6]", "[0, 1, 2]", "会报错"),
                answerIndex = 0,
                explanation = "range(3) 依次给 n 赋 0、1、2，乘以 2 后得到 [0, 2, 4]。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "推导式语法顺序写反",
                    detail = "表达式要写在 for 前面，过滤条件写在 for 后面。",
                    code = "[for n in range(3) n]  # 错\n[n for n in range(3)]  # 对",
                ),
                ErrorExample(
                    title = "一次写太长",
                    detail = "超过两层循环或复杂条件时，应改回普通 for 循环，保证别人能读懂。",
                    code = "# 复杂逻辑用普通循环更清楚",
                ),
            ),
            projectCode = "scores = [58, 92, 76, 49]\npassed = [score for score in scores if score >= 60]\nprint(\"及格名单\", passed)",
            legalRisk = "🟢 较低风险",
            legalNote = "推导式是通用语法。对真实名单或个人信息做筛选时，只应保留任务必需的字段。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("function", "函数", 22, LessonState.TODO),
                LessonSummary("file", "读写文件", 20, LessonState.LOCKED),
            ),
        ),
        "function" to LessonDetail(
            id = "function",
            title = "函数",
            stage = "函数与文件",
            level = "基础",
            minutes = 22,
            knowledge = listOf(
                "函数用 def 定义：把一段会重复使用的逻辑包起来，需要时通过函数名调用。",
                "return 可以把计算结果交回调用处；没有 return 时函数返回 None。",
            ),
            why = listOf(
                "把重复代码复制粘贴很多次，会让程序越来越难维护。",
                "函数让一段逻辑只写一次，名字还能表达它的用途。",
            ),
            purpose = "封装计算、格式化输出、校验输入、复用项目里的小工具。",
            example = "def greet(name):\n    return \"你好，\" + name\n\nprint(greet(\"小林\"))",
            exampleNotes = listOf(
                "def greet(name):" to "定义名为 greet、接收 name 的函数",
                "return" to "把结果交回调用处",
                "greet(\"小林\")" to "传入参数并调用函数",
            ),
            quiz = Quiz(
                question = "下面的函数调用后输出什么？",
                code = "def add(a, b):\n    return a + b\n\nprint(add(2, 3))",
                options = listOf("5", "23", "None", "会报错"),
                answerIndex = 0,
                explanation = "add(2, 3) 把参数 a 设为 2、b 设为 3，return 返回 5。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "忘了 return",
                    detail = "函数内部只 print 而不 return，调用处拿到的是 None。",
                    code = "def add(a, b):\n    print(a + b)\n\nresult = add(2, 3)\nprint(result)  # None",
                ),
                ErrorExample(
                    title = "定义后没有调用",
                    detail = "函数不会自己运行，必须用 函数名() 调用。",
                    code = "def hello():\n    print(\"hi\")\n\nhello()  # 别忘了调用",
                ),
            ),
            projectCode = "def calc_total(price, count):\n    return price * count\n\nprint(\"总价\", calc_total(5.5, 3))",
            legalRisk = "🟢 较低风险",
            legalNote = "函数是通用编程知识。把处理个人信息的逻辑封装进函数时，仍需控制参数范围和输出内容。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("file", "读写文件", 20, LessonState.TODO),
                LessonSummary("errors", "异常处理", 19, LessonState.LOCKED),
            ),
        ),
        "file" to LessonDetail(
            id = "file",
            title = "读写文件",
            stage = "函数与文件",
            level = "基础",
            minutes = 20,
            knowledge = listOf(
                "open(path, mode) 打开文件：\"w\" 写入、\"r\" 读取、\"a\" 追加。",
                "推荐使用 with 语句，程序会在代码块结束后自动关闭文件。",
            ),
            why = listOf(
                "数据如果只在内存里，程序一关就没了。文件能长期保存记录和结果。",
                "日志、配置、导出报表都依赖文件读写。",
            ),
            purpose = "保存学习记录、生成报告、读取配置文件、处理批量数据。",
            example = "with open(\"memo.txt\", \"w\", encoding=\"utf-8\") as f:\n    f.write(\"今天学会了文件读写\\n\")\nwith open(\"memo.txt\", \"r\", encoding=\"utf-8\") as f:\n    print(f.read())",
            exampleNotes = listOf(
                "\"w\"" to "写入模式，会创建或覆盖文件",
                "\"r\"" to "读取模式",
                "with ... as f" to "代码块结束后自动关闭文件",
            ),
            quiz = Quiz(
                question = "使用 with open(\"a.txt\", \"w\") 写入后，如何读取？",
                code = "with open(\"a.txt\", \"w\", encoding=\"utf-8\") as f:\n    f.write(\"hello\")\nwith open(\"a.txt\", \"r\", encoding=\"utf-8\") as f:\n    print(f.read())",
                options = listOf("hello", "hellohello", "会报错", "None"),
                answerIndex = 0,
                explanation = "先写入 hello，再用读取模式读出同一内容。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "读取不存在的文件",
                    detail = "用 \"r\" 打开不存在的文件会报 FileNotFoundError，先确认路径或使用异常处理。",
                    code = "with open(\"no.txt\", \"r\") as f:\n    print(f.read())",
                ),
                ErrorExample(
                    title = "忘了指定编码",
                    detail = "包含中文时最好指定 encoding=\"utf-8\"，否则不同系统可能乱码。",
                    code = "open(\"memo.txt\", \"w\", encoding=\"utf-8\")",
                ),
            ),
            projectCode = "record = \"小林 完成了猜数字\\n\"\nwith open(\"record.txt\", \"a\", encoding=\"utf-8\") as f:\n    f.write(record)\nprint(\"记录已保存\")",
            legalRisk = "🟢 较低风险",
            legalNote = "文件读写是通用技术。保存他人个人信息时，应设置访问权限、限制保存期限并防止文件泄露。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("module", "模块", 15, LessonState.TODO),
                LessonSummary("oop", "类与对象", 25, LessonState.LOCKED),
            ),
        ),
        "module" to LessonDetail(
            id = "module",
            title = "模块",
            stage = "函数与文件",
            level = "基础",
            minutes = 15,
            knowledge = listOf(
                "模块是包含 Python 代码的文件，通过 import 可以复用别人写好的功能。",
                "import random 后用 random.randint(...)，或 import math 后用 math.floor(...)。",
            ),
            why = listOf(
                "很多通用功能不必自己重新实现。Python 标准库和第三方模块能大幅减少重复造轮子。",
                "模块也帮助你把程序拆成多个文件，方便维护。",
            ),
            purpose = "随机数、日期时间、JSON、正则、网络请求等功能都可以通过模块复用。",
            example = "import random\nprint(random.randint(1, 100))",
            exampleNotes = listOf(
                "import random" to "把 random 模块引入程序",
                "random.randint(1, 100)" to "生成 1 到 100 之间的随机整数",
            ),
            quiz = Quiz(
                question = "运行 math.floor(2.7) 会得到什么？",
                code = "import math\nprint(math.floor(2.7))",
                options = listOf("2", "3", "2.7", "会报错"),
                answerIndex = 0,
                explanation = "floor 会向下取整，2.7 的下取整结果是 2。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "模块名拼写错误",
                    detail = "找不到模块通常是因为名字拼错，或没有安装对应包。",
                    code = "import randoms  # ModuleNotFoundError",
                ),
                ErrorExample(
                    title = "自己的文件覆盖模块",
                    detail = "文件名不要写成 random.py、math.py 等，否则会覆盖标准模块。",
                    code = "# random.py 会干扰 import random",
                ),
            ),
            projectCode = "import json\n\ndata = {\"name\": \"小林\", \"score\": 88}\nprint(json.dumps(data, ensure_ascii=False))",
            legalRisk = "🟢 较低风险",
            legalNote = "模块是通用知识。第三方模块应来自可信来源，并关注其授权方式与维护情况。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("oop", "类与对象", 25, LessonState.TODO),
                LessonSummary("errors", "异常处理", 19, LessonState.LOCKED),
            ),
        ),
        "oop" to LessonDetail(
            id = "oop",
            title = "类与对象",
            stage = "函数与文件",
            level = "基础",
            minutes = 25,
            knowledge = listOf(
                "类是一套设计图，对象是根据设计图创建出的具体实例。",
                "__init__ 是创建对象时自动执行的方法，self 指“当前对象”。",
            ),
            why = listOf(
                "当多个数据和方法属于同一个事物时，例如学生有名字、成绩和自我介绍方法，类能让结构更清楚。",
                "真实项目里 GUI、ORM、请求封装都大量使用类。",
            ),
            purpose = "封装用户、订单、网络客户端等实体和它对应的行为。",
            example = "class Student:\n    def __init__(self, name):\n        self.name = name\n    def intro(self):\n        return \"我是\" + self.name\n\ns = Student(\"小林\")\nprint(s.intro())",
            exampleNotes = listOf(
                "class Student:" to "定义类",
                "__init__" to "创建对象时设置初始属性",
                "self.name" to "把参数保存到当前对象上",
                "s.intro()" to "调用对象的方法",
            ),
            quiz = Quiz(
                question = "运行下面代码会输出什么？",
                code = "class Student:\n    def __init__(self, name):\n        self.name = name\n\ns = Student(\"小林\")\nprint(s.name)",
                options = listOf("小林", "name", "Student", "会报错"),
                answerIndex = 0,
                explanation = "创建 s 时把 小林 存到 s.name，所以输出小林。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "方法定义漏掉 self",
                    detail = "实例方法的第一个参数必须写 self，否则调用时参数数量不匹配。",
                    code = "def intro():  # 应写 def intro(self):\n    ...",
                ),
                ErrorExample(
                    title = "创建对象漏括号",
                    detail = "Student 是类，Student() 才会创建对象。",
                    code = "s = Student  # 类本身，不是对象\ns = Student(\"小林\")  # 对象",
                ),
            ),
            projectCode = "class Task:\n    def __init__(self, title):\n        self.title = title\n        self.done = False\n    def finish(self):\n        self.done = True\n\nt = Task(\"复习函数\")\nt.finish()\nprint(t.title, t.done)",
            legalRisk = "🟢 较低风险",
            legalNote = "类与对象是通用编程概念。用它建模真实用户信息时，仍应遵循最小必要和授权访问。",
            legalBasis = "参考原则：个人信息保护法、网络安全法、数据安全法",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("errors", "异常处理", 19, LessonState.TODO),
                LessonSummary("http", "HTTP 请求与响应", 18, LessonState.LOCKED),
            ),
        ),
        "errors" to LessonDetail(
            id = "errors",
            title = "异常处理",
            stage = "函数与文件",
            level = "基础",
            minutes = 19,
            knowledge = listOf(
                "程序遇到错误会抛出异常。try 里放可能出错的代码，except 负责处理某种异常。",
                "异常处理让程序在遇到输入错误或网络失败时继续运行，而不是直接崩溃。",
            ),
            why = listOf(
                "用户可能输入 abc，文件可能不存在，网络可能断掉。真实程序必须为这些情况做准备。",
                "只把 print 包起来而不处理，不能称为异常处理。",
            ),
            purpose = "转换用户输入、处理缺失文件、重试网络请求、返回友好提示。",
            example = "try:\n    number = int(\"abc\")\nexcept ValueError:\n    print(\"不是数字\")\nprint(\"程序继续\")",
            exampleNotes = listOf(
                "try:" to "尝试执行可能出错的代码",
                "except ValueError:" to "只捕获数字转换错误",
                "程序继续" to "捕获后不会崩溃",
            ),
            quiz = Quiz(
                question = "下面代码会输出什么？",
                code = "try:\n    number = int(\"abc\")\nexcept ValueError:\n    print(\"不是数字\")\nprint(\"完成\")",
                options = listOf("不是数字 完成", "abc", "只输出完成", "会崩溃"),
                answerIndex = 0,
                explanation = "int(\"abc\") 抛 ValueError，被 except 捕获后输出不是数字，最后输出完成。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "捕获范围太宽",
                    detail = "bare except: 会吞掉所有错误，让人看不出真正问题。至少写明异常类型。",
                    code = "try:\n    ...\nexcept:  # 太宽\n    pass",
                ),
                ErrorExample(
                    title = "except 后继续用无效变量",
                    detail = "转换失败时 number 可能不存在，后续使用前要处理默认值。",
                    code = "try:\n    number = int(input())\nexcept ValueError:\n    number = 0  # 给默认值",
                ),
            ),
            projectCode = "def to_int(text):\n    try:\n        return int(text)\n    except ValueError:\n        return 0\n\nprint(to_int(\"abc\"), to_int(\"42\"))",
            legalRisk = "🟢 较低风险",
            legalNote = "异常处理是通用编程知识。捕获异常不应用来绕过访问限制或隐藏不合规行为。",
            legalBasis = "参考原则：本模块不构成法律意见",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("http", "HTTP 请求与响应", 18, LessonState.TODO),
                LessonSummary("requests", "requests 基础", 21, LessonState.LOCKED),
            ),
        ),
        "http" to LessonDetail(
            id = "http",
            title = "HTTP 请求与响应",
            stage = "网络与爬虫",
            level = "基础",
            minutes = 18,
            knowledge = listOf(
                "HTTP 是浏览器和网站之间通信的规则：客户端发请求，服务器返回状态码和内容。",
                "常见状态码包括 200 成功、404 找不到、403 无权限、500 服务器错误。",
            ),
            why = listOf(
                "爬虫不是凭空“读取网页”，而是模拟一次受允许的请求并处理返回内容。",
                "看懂请求和状态码，才能判断是网络问题、地址问题还是权限问题。",
            ),
            purpose = "读取公开接口、检查目标是否可访问、理解服务器返回结果。",
            example = "import urllib.request\n\ntry:\n    response = urllib.request.urlopen(\"https://www.python.org\", timeout=8)\n    print(\"状态码\", response.status)\nexcept Exception as e:\n    print(\"请求失败\", e)",
            exampleNotes = listOf(
                "urlopen(...)" to "发起一次 HTTP GET 请求",
                "response.status" to "服务器返回的状态码",
                "timeout=8" to "8 秒内没响应就放弃",
            ),
            quiz = Quiz(
                question = "服务器返回 404，通常表示什么？",
                code = "# 状态码 404",
                options = listOf("找不到页面或资源", "请求成功", "没有权限", "服务器崩溃"),
                answerIndex = 0,
                explanation = "404 表示服务器找不到请求的 URL 对应资源。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "网址拼错",
                    detail = "缺少 https://、多了空格，都会让请求失败。",
                    code = "urlopen(\"www.python.org\")  # 建议写完整 https:// 地址",
                ),
                ErrorExample(
                    title = "把状态码当成内容",
                    detail = "response.status 只是状态码，正文还需要调用读取内容的方法。",
                    code = "html = response.read()  # 读取响应正文",
                ),
            ),
            projectCode = "import urllib.request\n\ntry:\n    with urllib.request.urlopen(\"https://www.python.org\", timeout=8) as r:\n        print(\"状态码\", r.status)\nexcept Exception as e:\n    print(\"请求失败\", e)",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "发起网络请求本身是中性的，但应遵守网站服务条款、robots 规则和访问频率要求。不要绕过登录、验证码或访问控制。",
            legalBasis = "参考原则：民法典、网络安全法、数据安全法、个人信息保护法；不同地区可能另有规则",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("requests", "requests 基础", 21, LessonState.TODO),
                LessonSummary("api", "API 的正确用法", 17, LessonState.LOCKED),
            ),
        ),
        "requests" to LessonDetail(
            id = "requests",
            title = "requests 基础",
            stage = "网络与爬虫",
            level = "基础",
            minutes = 21,
            knowledge = listOf(
                "requests 是 Python 常用的 HTTP 请求库，代码比 urllib 更简洁。",
                "requests.get(url) 发 GET 请求，response.status_code 看状态码，response.text 看正文。",
            ),
            why = listOf(
                "把请求代码写得简短清晰，才能把精力放在真正要处理的数据上。",
                "requests 是很多爬虫与 API 项目的基础。",
            ),
            purpose = "请求公开网页、调用 API、携带参数或 Headers、处理响应文本。",
            example = "import requests\n\ntry:\n    r = requests.get(\"https://www.python.org\", timeout=8)\n    print(\"状态码\", r.status_code)\n    print(\"前 40 个字符\", r.text[:40])\nexcept requests.RequestException as e:\n    print(\"请求失败\", e)",
            exampleNotes = listOf(
                "requests.get(url)" to "发起 GET 请求",
                "r.status_code" to "状态码",
                "r.text" to "响应文本",
            ),
            quiz = Quiz(
                question = "requests.get 成功返回后，怎么看状态码？",
                code = "r = requests.get(url)\nprint(?)",
                options = listOf("r.status_code", "r.code", "r.response", "status(r)"),
                answerIndex = 0,
                explanation = "requests 响应对象的 status_code 属性保存 HTTP 状态码。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "未安装 requests",
                    detail = "requests 不是标准库，需要先安装到项目依赖中。",
                    code = "import requests  # ModuleNotFoundError 表示未安装",
                ),
                ErrorExample(
                    title = "不看状态码就解析",
                    detail = "请求失败时响应内容可能是错误页，先检查 status_code 再处理。",
                    code = "if r.status_code == 200:\n    html = r.text",
                ),
            ),
            projectCode = "import requests\n\ntry:\n    r = requests.get(\"https://www.python.org\", timeout=8)\n    if r.status_code == 200:\n        print(\"页面长度\", len(r.text))\n    else:\n        print(\"状态码\", r.status_code)\nexcept requests.RequestException as e:\n    print(\"请求失败\", e)",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "requests 只是工具。使用前应确认访问对象是否允许程序化访问，控制频率并尊重数据所有者权利。",
            legalBasis = "参考原则：民法典、网络安全法、数据安全法、个人信息保护法；不同地区可能另有规则",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("html", "HTML 与 BeautifulSoup", 22, LessonState.TODO),
                LessonSummary("session", "Cookie 与 Session", 19, LessonState.LOCKED),
            ),
        ),
        "html" to LessonDetail(
            id = "html",
            title = "HTML 与 BeautifulSoup",
            stage = "网络与爬虫",
            level = "基础",
            minutes = 22,
            knowledge = listOf(
                "HTML 是网页的结构文本，标签通常成对出现，例如 <div>...</div>。",
                "BeautifulSoup 可以把 HTML 字符串解析成对象，再用选择器取出内容。",
            ),
            why = listOf(
                "直接对整段 HTML 做字符串截取很容易出错。解析库能按标签结构稳定提取。",
                "BeautifulSoup 适合处理不严格规范的 HTML。",
            ),
            purpose = "从页面中提取标题、链接、列表内容，作为后续结构化数据。",
            example = "from bs4 import BeautifulSoup\n\nhtml = \"<div class='news'>Python 课程</div>\"\nsoup = BeautifulSoup(html, \"html.parser\")\nprint(soup.select_one(\".news\").get_text())",
            exampleNotes = listOf(
                "BeautifulSoup(html, \"html.parser\")" to "解析 HTML 字符串",
                "select_one(\".news\")" to "按 CSS class 找到第一个元素",
                "get_text()" to "取出元素里的文字",
            ),
            quiz = Quiz(
                question = "拿到一个 BeautifulSoup 对象后，怎么取出标签文字？",
                code = "soup = BeautifulSoup(html, \"html.parser\")\nelement = soup.select_one(\".title\")",
                options = listOf("element.get_text()", "element.text()", "element.content", "get(element)"),
                answerIndex = 0,
                explanation = "BeautifulSoup 元素用 get_text() 获取其中文字。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "选择器写错",
                    detail = "类名选择器要写 .类名，标签直接写标签名，id 写 #id。",
                    code = "soup.select_one(\"news\")  # 少了 .\nsoup.select_one(\".news\")  # 对",
                ),
                ErrorExample(
                    title = "对空结果调用 get_text",
                    detail = "没有找到元素时返回 None，先判断再取文字。",
                    code = "element = soup.select_one(\".missing\")\nif element:\n    print(element.get_text())",
                ),
            ),
            projectCode = "from bs4 import BeautifulSoup\n\nhtml = \"<ul><li>标题一</li><li>标题二</li></ul>\"\nsoup = BeautifulSoup(html, \"html.parser\")\nfor li in soup.find_all(\"li\"):\n    print(li.get_text())",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "解析公开页面结构本身不违法，但只应解析你有权访问的页面，并尊重网站规则与著作权。",
            legalBasis = "参考原则：民法典、著作权法、网络安全法、数据安全法；不同地区可能另有规则",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("session", "Cookie 与 Session", 19, LessonState.TODO),
                LessonSummary("api", "API 的正确用法", 17, LessonState.LOCKED),
            ),
        ),
        "session" to LessonDetail(
            id = "session",
            title = "Cookie 与 Session",
            stage = "网络与爬虫",
            level = "基础",
            minutes = 19,
            knowledge = listOf(
                "Session 常用来保持同一客户端的一系列状态，比如登录后连续访问多个页面。",
                "requests.Session() 会自动保存服务器下发的 Cookie，供后续请求使用。",
            ),
            why = listOf(
                "很多需要登录的页面不能每发一次请求都重新登录。Session 让状态可以延续。",
                "但 Session 也意味着权限边界，绝不能擅自绕过登录或访问控制。",
            ),
            purpose = "保持 Cookie、模拟带登录状态的多步骤访问、管理会话请求头。",
            example = "import requests\n\nsession = requests.Session()\nsession.headers.update({\"User-Agent\": \"PythonLearner/1.0\"})\nprint(\"Session 已创建\")",
            exampleNotes = listOf(
                "requests.Session()" to "创建可复用会话",
                "headers.update(...)" to "为后续请求统一设置请求头",
                "作用" to "会话会保存返回的 Cookie",
            ),
            quiz = Quiz(
                question = "requests.Session() 主要帮助解决什么问题？",
                code = "session = requests.Session()",
                options = listOf("保持 Cookie 等会话状态", "自动破解验证码", "隐藏来源地址", "绕过访问权限"),
                answerIndex = 0,
                explanation = "Session 会保存 Cookie 并保持会话状态，但不能也不应用于绕过访问控制。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "把 Session 当匿名工具",
                    detail = "登录状态只代表服务端已经授权当前会话，不代表可以随意复制或抓取数据。",
                    code = "# 有权限后仍要遵守用途限制",
                ),
                ErrorExample(
                    title = "每个请求都新建 Session",
                    detail = "新建 Session 会丢失上一个请求保存的 Cookie。",
                    code = "session = requests.Session()  # 复用同一个 session",
                ),
            ),
            projectCode = "import requests\n\nsession = requests.Session()\nsession.headers.update({\"User-Agent\": \"PythonLearner/1.0\"})\n# 只在服务端允许的范围和使用目的内使用会话",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "管理自己的登录会话属于常见技术。禁止利用他人凭据、绕过访问控制或超出授权范围处理数据。",
            legalBasis = "参考原则：网络安全法、数据安全法、个人信息保护法、计算机信息系统相关法律；不同地区可能另有规则",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("api", "API 的正确用法", 17, LessonState.TODO),
                LessonSummary("legal", "爬虫安全与法律", 24, LessonState.LOCKED),
            ),
        ),
        "api" to LessonDetail(
            id = "api",
            title = "API 的正确用法",
            stage = "网络与爬虫",
            level = "基础",
            minutes = 17,
            knowledge = listOf(
                "API 是服务方公开的“接口”，返回通常是 JSON。调用前应阅读文档、注册授权并遵守限额。",
                "调用者身份通常通过 Key、Token 或 OAuth 验证；Key 属于账号凭证，不能公开。",
            ),
            why = listOf(
                "比起解析 HTML，使用官方 API 更稳定、更合规，也更尊重数据所有者。",
                "很多网站明确鼓励开发者通过 API 获取数据。",
            ),
            purpose = "获取天气、地图、翻译等公开服务数据，完成项目与自动化。",
            example = "import requests\n\ntry:\n    r = requests.get(\"https://jsonplaceholder.typicode.com/todos/1\", timeout=8)\n    print(\"状态码\", r.status_code)\n    print(r.json().get(\"title\", \"\"))\nexcept requests.RequestException as e:\n    print(\"请求失败\", e)",
            exampleNotes = listOf(
                "requests.get(url)" to "调用示例接口",
                "r.json()" to "把 JSON 转成字典/列表",
                "timeout=8" to "设置超时",
            ),
            quiz = Quiz(
                question = "调用需要密钥的 API 时，正确做法是什么？",
                code = "# 请求头",
                options = listOf("密钥保存在服务端配置中", "把密钥发给别人", "密钥写进公开教程", "不设权限"),
                answerIndex = 0,
                explanation = "API 密钥是账号凭证，应保存在服务端或安全的本地配置中，不能公开。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "不阅读限额就高频请求",
                    detail = "API 通常会限制频率，超限会被限流或封禁。应遵守文档速率限制并加延时。",
                    code = "# 按文档控制请求频率",
                ),
                ErrorExample(
                    title = "把 Key 写进代码仓库",
                    detail = "Key 一旦泄露可能被滥用。应从环境变量或安全配置读取。",
                    code = "api_key = os.environ[\"API_KEY\"]  # 不写死",
                ),
            ),
            projectCode = "import os\nimport requests\n\n# 在真实项目里从安全配置读取 Key，不写进代码\nendpoint = \"https://example.com/api\"\ntry:\n    r = requests.get(endpoint, timeout=8)\n    if r.status_code == 200:\n        print(r.json())\n    else:\n        print(\"状态码\", r.status_code)\nexcept requests.RequestException as e:\n    print(\"请求失败\", e)",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "使用 API 必须遵守服务条款与授权范围。密钥泄漏、绕过限额、抓取非授权数据都可能带来合规风险。",
            legalBasis = "参考原则：民法典、网络安全法、数据安全法、个人信息保护法；不同地区可能另有规则",
            legalUpdated = "2026-09-05",
            next = listOf(
                LessonSummary("legal", "爬虫安全与法律", 24, LessonState.TODO),
            ),
        ),
        "legal" to LessonDetail(
            id = "legal",
            title = "爬虫安全与法律",
            stage = "网络与爬虫",
            level = "安全与合规",
            minutes = 24,
            knowledge = listOf(
                "判断一次数据采集是否合适，要看访问对象、数据类型、用途和方式，而不是把爬虫工具本身当违法工具。",
                "公开可见不等于可以任意复制；登录状态、个人数据、商业数据库需要更谨慎评估。",
            ),
            why = listOf(
                "爬虫课程的价值不只是“能抓到”，而是知道什么能访问、如何访问、抓到的数据能做什么。",
                "法律内容会随地区和案例变化，本课程只给检查清单，不构成法律意见。",
            ),
            purpose = "在真实项目开始前做访问目的、权限、频率、数据用途和保存期限的自查。",
            example = "# 项目开始前先回答这些问题：\n# 1. 我是否获得授权或使用公开 API？\n# 2. 请求频率是否合理？\n# 3. 数据是否含个人信息或受著作权保护？\n# 4. 采集后的用途和保存期限是什么？",
            exampleNotes = listOf(
                "授权" to "优先使用 API 和服务条款允许的方式",
                "频率" to "低频率、按需请求，避免影响对方服务",
                "数据" to "区分公开信息、个人数据与受版权保护内容",
            ),
            quiz = Quiz(
                question = "下面哪种情况最需要先做合规评估？",
                code = "# 选择更谨慎的场景",
                options = listOf(
                    "采集含姓名、电话的个人信息",
                    "读取自己项目中的配置文件",
                    "在本地练习 for 循环",
                    "打印一行问候文字",
                ),
                answerIndex = 0,
                explanation = "处理个人信息会涉及隐私和数据保护规则，应优先评估合法性依据与用途限制。",
            ),
            errors = listOf(
                ErrorExample(
                    title = "把“公开可见”等同于任意使用",
                    detail = "公开可见不等于数据不受著作权、隐私或网站规则保护。",
                    code = "# 公开页面也要看授权和使用目的",
                ),
                ErrorExample(
                    title = "只改请求头就认为合规",
                    detail = "合规主要看访问对象、数据性质和用途，伪造请求头不能解决访问授权问题。",
                    code = "# User-Agent 不决定是否合规",
                ),
            ),
            projectCode = "# 我的合规自查清单\n# 访问对象：\n# 使用目的：\n# 授权方式：\n# 请求频率：\n# 数据类型：\n# 保存期限：",
            legalRisk = "⚠️ 需要结合场景判断",
            legalNote = "本模块只提供学习性检查清单，不构成法律意见。不同国家/地区对网页抓取、个人数据与商业数据的规定不同，应结合具体项目咨询专业意见。",
            legalBasis = "参考原则：网络安全法、数据安全法、个人信息保护法、著作权法、民法典；日本/美国/欧盟另有相应规则",
            legalUpdated = "2026-09-05",
            next = listOf(
            ),
        ),
    )
}

object ProjectCatalog {
    val guess = ProjectInfo(
        id = "guess",
        title = "猜数字",
        level = "Lv.1 入门项目",
        goal = "编写一个 1~100 的猜数字游戏。程序随机生成答案，用户每次输入一个数字，程序提示偏大或偏小，猜对后结束并显示猜测次数。",
        requirements = listOf(
            "程序随机生成 1 到 100 之间的整数",
            "用户输入数字并转换为整数",
            "比较猜的数字和答案，并提示大小",
            "猜错时继续，猜对后结束",
            "记录并显示猜测次数",
        ),
        knowledge = listOf("random", "input", "if", "while", "变量"),
        hints = listOf(
            "先写“生成答案 → 接收输入 → 比较 → 结束”的骨架，再考虑重复。",
            "需要重复的是接收输入和比较。想想哪一种循环适合“猜对了才停”。",
            "每猜一次用一个变量 +1，最后打印出来。先跑通再优化。",
        ),
        starter = "print(\"我已经想好一个 1~100 的数字\")\n\n# 1. 生成答案\n# 2. 用变量记录次数\n# 3. 接收用户输入并比较\n# 4. 猜对后结束",
    )

    val calculator = ProjectInfo(
        id = "calculator",
        title = "计算器",
        level = "Lv.1 入门项目",
        goal = "做一个支持加减乘除的文本计算器。程序接收两个数字和运算符号，输出正确结果，并处理除数为 0 的情况。",
        requirements = listOf(
            "接收第一个数字、运算符号和第二个数字",
            "把输入内容转换为数字",
            "根据运算符号完成加减乘除",
            "除数为 0 时给出友好提示，不让程序崩溃",
            "输出完整计算式与结果",
        ),
        knowledge = listOf("input", "变量", "if", "float", "异常处理"),
        hints = listOf(
            "先只处理两个数字和一种运算，跑通后再补其他运算。",
            "运算符号可以存到变量里，再用 if / elif 判断。",
            "输入 abc 时 int() 会报错，可先做异常处理。",
        ),
        starter = "# 1. 接收两个数字和运算符号\n# 2. 转换为数字\n# 3. 用 if 判断运算并计算结果\n# 4. 输出结果",
    )

    val bmi = ProjectInfo(
        id = "bmi",
        title = "BMI 计算器",
        level = "Lv.1 入门项目",
        goal = "接收身高和体重，计算 BMI，并根据结果给出偏瘦、正常、偏胖等提示。",
        requirements = listOf(
            "接收身高（米）和体重（千克）",
            "BMI = 体重 ÷ 身高 ÷ 身高",
            "用条件判断输出对应的文字结果",
            "身高或体重输入不合法时给提示",
        ),
        knowledge = listOf("float", "input", "变量", "if", "异常处理"),
        hints = listOf(
            "先算 BMI，再把它放进多个条件判断里。",
            "身体结果只是学习示例，不代表医学建议。",
            "可以先给数值范围，再判断是否合理。",
        ),
        starter = "# 1. 接收身高\n# 2. 接收体重\n# 3. 计算 BMI\n# 4. 用 if 输出分类",
    )

    val contacts = ProjectInfo(
        id = "contacts",
        title = "通讯录",
        level = "Lv.2 基础项目",
        goal = "做一个临时通讯录，能新增联系人、列出所有联系人，并按姓名查询电话号码。",
        requirements = listOf(
            "用字典保存联系人姓名和电话",
            "提供新增联系人功能",
            "提供列出全部联系人功能",
            "提供按姓名查询电话功能",
            "程序结束时给出退出提示",
        ),
        knowledge = listOf("dict", "list", "while", "input", "函数"),
        hints = listOf(
            "先用字典 contacts = {}，再用 name = input() 作为键。",
            "重复操作可以用 while True，退出时用 break。",
            "先实现新增和列出，再补查询。",
        ),
        starter = "contacts = {}\nprint(\"欢迎使用通讯录\")\n# 用 while True 提供菜单\n# 输入 1 新增，2 列出，3 查询，0 退出",
    )

    val all = listOf(guess, calculator, bmi, contacts)

    fun byId(id: String): ProjectInfo? = all.firstOrNull { it.id == id }
}

object DemoStats {
    val pythonLevel = "Python Lv.1"
    val learningDays = 0
    val finishedCourses = 0
    val finishedPractice = 0
    val streakDays = 0
    val dailyMinutes = 0
    val todayTasks = listOf("学习 15 分钟", "完成 4 道练习", "完成今日挑战")
    val projects = listOf(
        "计算器" to "已完成",
        "猜数字" to "进行中",
        "BMI 计算器" to "未开始",
        "通讯录" to "未解锁",
    )
}
