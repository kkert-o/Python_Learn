package com.pythonlearn.app.data

enum class LibraryCategory(val label: String) {
    NETWORK("网络与 API"),
    DATA("数据处理"),
    DATABASE("数据库"),
    WEB("Web 开发"),
    TESTING("测试与质量"),
    AI("AI 应用"),
    TOOLS("工程工具"),
}

data class LibraryEntry(
    val id: String,
    val name: String,
    val category: LibraryCategory,
    val summary: String,
    val useCase: String,
    val install: String,
    val example: String,
    val lessonId: String?,
    val runtimeAvailable: Boolean = true,
)

object LibraryCatalog {
    val all: List<LibraryEntry> = listOf(
        LibraryEntry(
            id = "requests",
            name = "requests",
            category = LibraryCategory.NETWORK,
            summary = "易读的 HTTP 客户端，适合调用 API 和理解请求响应。",
            useCase = "访问自己拥有的服务、公开 API 或获得授权的数据接口。",
            install = "pip install requests",
            example = "import requests\nr = requests.get(url, timeout=8)\nprint(r.status_code)",
            lessonId = "requests",
        ),
        LibraryEntry(
            id = "httpx",
            name = "httpx",
            category = LibraryCategory.NETWORK,
            summary = "同时支持同步和异步的现代 HTTP 客户端。",
            useCase = "需要并发请求或同时使用标准 HTTP/2 能力的 Python 项目。",
            install = "pip install httpx",
            example = "import httpx\nr = httpx.get(url, timeout=8)",
            lessonId = "requests",
        ),
        LibraryEntry(
            id = "beautifulsoup4",
            name = "BeautifulSoup",
            category = LibraryCategory.NETWORK,
            summary = "用标签选择器从 HTML/XML 中提取结构化内容。",
            useCase = "解析获得授权的静态页面，优先选择官方 API，并遵守网站规则。",
            install = "pip install beautifulsoup4",
            example = "from bs4 import BeautifulSoup\nsoup = BeautifulSoup(html, \"html.parser\")",
            lessonId = "html",
        ),
        LibraryEntry(
            id = "pandas",
            name = "pandas",
            category = LibraryCategory.DATA,
            summary = "处理表格数据、清洗缺失值和做聚合分析的核心库。",
            useCase = "读取 CSV/Excel，筛选、合并、统计并输出分析结果。",
            install = "pip install pandas",
            example = "import pandas as pd\ndf = pd.read_csv(\"scores.csv\")\nprint(df.groupby(\"class\")[\"score\"].mean())",
            lessonId = "pandas",
        ),
        LibraryEntry(
            id = "numpy",
            name = "NumPy",
            category = LibraryCategory.DATA,
            summary = "面向数组和数值计算的 Python 基础工具。",
            useCase = "批量数值运算、矩阵计算和机器学习数据准备。",
            install = "pip install numpy",
            example = "import numpy as np\nvalues = np.array([1, 2, 3])\nprint(values.mean())",
            lessonId = "numpy",
        ),
        LibraryEntry(
            id = "matplotlib",
            name = "Matplotlib",
            category = LibraryCategory.DATA,
            summary = "把数据绘制成折线图、柱状图、散点图等静态图表。",
            useCase = "学习数据可视化，或把分析结果输出为图片用于报告。",
            install = "pip install matplotlib",
            example = "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])\nplt.savefig(\"chart.png\")",
            lessonId = "visualization",
        ),
        LibraryEntry(
            id = "sqlalchemy",
            name = "SQLAlchemy",
            category = LibraryCategory.DATABASE,
            summary = "成熟 ORM 与 SQL 工具集，减少重复数据库代码。",
            useCase = "中型应用的数据建模、事务和多数据库适配。",
            install = "pip install sqlalchemy",
            example = "from sqlalchemy import create_engine\nengine = create_engine(\"sqlite:///study.db\")",
            lessonId = "sqlite",
        ),
        LibraryEntry(
            id = "fastapi",
            name = "FastAPI",
            category = LibraryCategory.WEB,
            summary = "基于类型提示的现代 Web API 框架，自动生成接口文档。",
            useCase = "把自己的 Python 能力封装成可被网页或移动端调用的服务。",
            install = "pip install fastapi uvicorn",
            example = "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get(\"/health\")\ndef health():\n    return {\"ok\": True}",
            lessonId = "fastapi",
        ),
        LibraryEntry(
            id = "pytest",
            name = "pytest",
            category = LibraryCategory.TESTING,
            summary = "用简洁的断言组织自动化测试。",
            useCase = "验证函数、接口和数据流程，防止修改代码后引入回归。",
            install = "pip install pytest",
            example = "def test_add():\n    assert 1 + 2 == 3",
            lessonId = "testing",
        ),
        LibraryEntry(
            id = "ruff",
            name = "Ruff",
            category = LibraryCategory.TESTING,
            summary = "快速检查常见代码问题并统一代码风格。",
            useCase = "在提交前发现未使用变量、导入顺序和常见缺陷。",
            install = "pip install ruff",
            example = "ruff check .\nruff format .",
            lessonId = "quality",
            runtimeAvailable = false,
        ),
        LibraryEntry(
            id = "click",
            name = "Click",
            category = LibraryCategory.TOOLS,
            summary = "快速构建结构清晰的命令行工具。",
            useCase = "为自动化脚本、数据处理任务和开发工具提供命令参数。",
            install = "pip install click",
            example = "import click\n\n@click.command()\n@click.option(\"--name\", prompt=True)\ndef hello(name):\n    click.echo(f\"Hello {name}\")",
            lessonId = "module",
        ),
        LibraryEntry(
            id = "rich",
            name = "Rich",
            category = LibraryCategory.TOOLS,
            summary = "在终端输出彩色文本、表格、进度条和结构化信息。",
            useCase = "改善命令行工具的可读性和长时间任务的进度反馈。",
            install = "pip install rich",
            example = "from rich.console import Console\nconsole = Console()\nconsole.print(\"Python\", style=\"bold green\")",
            lessonId = "quality",
        ),
        LibraryEntry(
            id = "openai",
            name = "OpenAI Python SDK",
            category = LibraryCategory.AI,
            summary = "在 Python 项目中调用大模型接口。",
            useCase = "把总结、分类、问答等 AI 能力接入自己的应用。",
            install = "pip install openai",
            example = "import os\nimport openai\n\nopenai.api_key = os.environ[\"OPENAI_API_KEY\"]\nreply = openai.ChatCompletion.create(\n    model=\"gpt-4.1-mini\",\n    messages=[{\"role\": \"user\", \"content\": \"解释变量\"}],\n)",
            lessonId = "ai-api",
        ),
        LibraryEntry(
            id = "scikit-learn",
            name = "scikit-learn",
            category = LibraryCategory.AI,
            summary = "经典机器学习算法和数据处理流程工具。",
            useCase = "分类、回归、聚类和模型评估入门。",
            install = "pip install scikit-learn",
            example = "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()",
            lessonId = "machine-learning",
            runtimeAvailable = false,
        ),
    )

    fun byId(id: String): LibraryEntry? = all.firstOrNull { it.id == id }

    fun search(query: String): List<LibraryEntry> {
        val needle = query.trim()
        if (needle.isEmpty()) return all
        return all.filter { entry ->
            entry.name.contains(needle, ignoreCase = true) ||
                entry.summary.contains(needle, ignoreCase = true) ||
                entry.useCase.contains(needle, ignoreCase = true) ||
                entry.category.label.contains(needle, ignoreCase = true)
        }
    }
}

data class ErrorMuseumEntry(
    val id: String,
    val title: String,
    val errorType: String,
    val symptom: String,
    val cause: String,
    val brokenCode: String,
    val fixedCode: String,
    val prevention: String,
    val lessonId: String?,
)

object ErrorMuseumCatalog {
    val all: List<ErrorMuseumEntry> = listOf(
        ErrorMuseumEntry(
            id = "name-error",
            title = "变量名拼写不一致",
            errorType = "NameError",
            symptom = "Python 提示 name 'socre' is not defined。",
            cause = "定义变量时写的是 score，使用时却写成了 socre。",
            brokenCode = "score = 85\nprint(socre)",
            fixedCode = "score = 85\nprint(score)",
            prevention = "使用有意义的变量名，并借助编辑器补全检查拼写。",
            lessonId = "errors",
        ),
        ErrorMuseumEntry(
            id = "syntax-error",
            title = "if 条件用了赋值号",
            errorType = "SyntaxError",
            symptom = "Python 在运行前就指出条件表达式无效。",
            cause = "= 是赋值，== 才是判断两个值是否相等。",
            brokenCode = "score = 85\nif score = 85:\n    print(\"正确\")",
            fixedCode = "score = 85\nif score == 85:\n    print(\"正确\")",
            prevention = "写条件判断时先读一遍：这里是在赋值，还是在比较？",
            lessonId = "if",
        ),
        ErrorMuseumEntry(
            id = "type-error",
            title = "文字和数字直接相加",
            errorType = "TypeError",
            symptom = "报错提到 can only concatenate str，不能把 str 和 int 相加。",
            cause = "input() 返回字符串，直接和数字计算前必须转换类型。",
            brokenCode = "age = input(\"年龄：\")\nprint(age + 1)",
            fixedCode = "age = int(input(\"年龄：\"))\nprint(age + 1)",
            prevention = "看到 input() 时先问：后面把它当文字还是当数字？",
            lessonId = "types",
        ),
        ErrorMuseumEntry(
            id = "value-error",
            title = "转换了非数字内容",
            errorType = "ValueError",
            symptom = "int(\"abc\") 报 ValueError，提示字符串不是合法整数。",
            cause = "转换函数只能处理格式正确的内容，用户可能没有按预期输入。",
            brokenCode = "count = int(\"很多\")\nprint(count)",
            fixedCode = "text = \"很多\"\nif text.isdigit():\n    count = int(text)\nelse:\n    print(\"请输入数字\")",
            prevention = "处理真实输入时使用校验或 try / except，不要默认输入永远正确。",
            lessonId = "errors",
        ),
        ErrorMuseumEntry(
            id = "index-error",
            title = "访问了列表不存在的位置",
            errorType = "IndexError",
            symptom = "list index out of range，说明索引超出了列表范围。",
            cause = "列表长度是 3，有效索引只到 2，却访问了索引 3。",
            brokenCode = "names = [\"小林\", \"小王\", \"小陈\"]\nprint(names[3])",
            fixedCode = "names = [\"小林\", \"小王\", \"小陈\"]\nprint(names[-1])  # 最后一个元素",
            prevention = "访问索引前确认列表长度，或用循环和成员判断避免硬编码位置。",
            lessonId = "list",
        ),
        ErrorMuseumEntry(
            id = "key-error",
            title = "读取字典里不存在的键",
            errorType = "KeyError",
            symptom = "字典方括号读取内容时提示某个 key 不存在。",
            cause = "方括号读取要求键一定存在，否则会报错。",
            brokenCode = "person = {\"name\": \"小林\"}\nprint(person[\"phone\"])",
            fixedCode = "person = {\"name\": \"小林\"}\nprint(person.get(\"phone\", \"未记录\"))",
            prevention = "不确定键是否存在时使用 get()，并给出清晰的默认值。",
            lessonId = "dict",
        ),
        ErrorMuseumEntry(
            id = "attribute-error",
            title = "调用了不存在的列表方法",
            errorType = "AttributeError",
            symptom = "列表对象没有 add 方法，但代码却调用了 scores.add()。",
            cause = "把集合的 add() 记忆成了列表方法；列表添加末尾元素应使用 append()。",
            brokenCode = "scores = [80, 90]\nscores.add(100)",
            fixedCode = "scores = [80, 90]\nscores.append(100)",
            prevention = "先确认数据类型，再选择它真正支持的方法。",
            lessonId = "list",
        ),
        ErrorMuseumEntry(
            id = "file-error",
            title = "读取不存在的文件",
            errorType = "FileNotFoundError",
            symptom = "程序找不到指定路径的文件。",
            cause = "文件名、目录或工作目录与预期不一致。",
            brokenCode = "with open(\"score.txt\", \"r\", encoding=\"utf-8\") as file:\n    print(file.read())",
            fixedCode = "from pathlib import Path\npath = Path(\"score.txt\")\nif path.exists():\n    print(path.read_text(encoding=\"utf-8\"))\nelse:\n    print(\"请先创建 score.txt\")",
            prevention = "使用明确的路径，并在读取前判断文件是否存在。",
            lessonId = "file",
        ),
    )

    fun byId(id: String): ErrorMuseumEntry? = all.firstOrNull { it.id == id }

    fun search(query: String): List<ErrorMuseumEntry> {
        val needle = query.trim()
        if (needle.isEmpty()) return all
        return all.filter { entry ->
            entry.title.contains(needle, ignoreCase = true) ||
                entry.errorType.contains(needle, ignoreCase = true) ||
                entry.cause.contains(needle, ignoreCase = true) ||
                entry.symptom.contains(needle, ignoreCase = true)
        }
    }
}

enum class EngineeringCategory(val label: String) {
    GIT("Git 版本管理"),
    QUALITY("代码质量"),
    TESTING("测试"),
}

data class EngineeringModule(
    val id: String,
    val title: String,
    val category: EngineeringCategory,
    val summary: String,
    val checklist: List<String>,
    val commands: List<String>,
    val lessonId: String?,
)

object EngineeringCatalog {
    val all: List<EngineeringModule> = listOf(
        EngineeringModule(
            id = "git-basics",
            title = "Git 基础工作流",
            category = EngineeringCategory.GIT,
            summary = "用版本历史保护每次可运行的修改。",
            checklist = listOf("提交前查看变更", "一次提交只做一类修改", "提交信息说明原因和结果"),
            commands = listOf("git status", "git diff", "git add .", "git commit -m \"说明\""),
            lessonId = "git",
        ),
        EngineeringModule(
            id = "git-branches",
            title = "分支与合并",
            category = EngineeringCategory.GIT,
            summary = "在独立分支开发功能，验证后再合并。",
            checklist = listOf("功能分支从稳定版本开始", "合并前运行测试", "冲突时保留正确逻辑而不是机械选一边"),
            commands = listOf("git switch -c feature/task", "git switch main", "git merge feature/task"),
            lessonId = "git",
        ),
        EngineeringModule(
            id = "quality-review",
            title = "代码质量检查",
            category = EngineeringCategory.QUALITY,
            summary = "让代码更容易读、修改和测试。",
            checklist = listOf("函数只做一件事", "变量名表达真实含义", "错误有处理路径", "重复逻辑及时提取"),
            commands = listOf("ruff check .", "ruff format .", "python -m compileall ."),
            lessonId = "quality",
        ),
        EngineeringModule(
            id = "pytest-basics",
            title = "最小测试闭环",
            category = EngineeringCategory.TESTING,
            summary = "每次修改后自动确认关键行为没有倒退。",
            checklist = listOf("测试正常路径", "测试边界值", "测试错误输入", "失败时先复现再修复"),
            commands = listOf("pytest -q", "pytest --cov=.", "python -m unittest"),
            lessonId = "testing",
        ),
    )

    fun search(query: String): List<EngineeringModule> {
        val needle = query.trim()
        if (needle.isEmpty()) return all
        return all.filter { module ->
            module.title.contains(needle, ignoreCase = true) ||
                module.summary.contains(needle, ignoreCase = true) ||
                module.category.label.contains(needle, ignoreCase = true)
        }
    }
}

data class AiFreeChallenge(
    val id: String,
    val title: String,
    val level: String,
    val brief: String,
    val acceptance: List<String>,
)

object AiIndependenceCatalog {
    val challenges: List<AiFreeChallenge> = listOf(
        AiFreeChallenge(
            id = "ai-free-debug",
            title = "独立定位一个报错",
            level = "Lv.1",
            brief = "遇到报错后先阅读类型、行号和最后一个变量名，不询问 AI。",
            acceptance = listOf("说出错误发生在哪一行", "用自己的话解释原因", "修复后再次运行验证"),
        ),
        AiFreeChallenge(
            id = "ai-free-function",
            title = "独立写出一个小函数",
            level = "Lv.2",
            brief = "只根据输入、输出和边界要求写函数，不看完整答案。",
            acceptance = listOf("函数职责清晰", "正常输入结果正确", "边界输入有明确行为"),
        ),
        AiFreeChallenge(
            id = "ai-free-file",
            title = "独立完成文件处理",
            level = "Lv.2",
            brief = "读取一段文本，统计目标内容并把结果写入新文件。",
            acceptance = listOf("文件正确关闭", "异常路径有提示", "结果可重复验证"),
        ),
        AiFreeChallenge(
            id = "ai-free-api",
            title = "独立调用公开 API",
            level = "Lv.3",
            brief = "阅读接口文档，使用超时、状态码判断和 JSON 解析完成调用。",
            acceptance = listOf("不改用未经授权的数据源", "不硬编码密钥", "处理网络失败"),
        ),
        AiFreeChallenge(
            id = "ai-free-database",
            title = "独立设计 SQLite 数据表",
            level = "Lv.4",
            brief = "为一个小型记录程序设计表结构并完成增删改查。",
            acceptance = listOf("主键与字段类型合理", "新增和查询可用", "删除前有确认或可恢复策略"),
        ),
        AiFreeChallenge(
            id = "ai-free-project",
            title = "从需求到可运行项目",
            level = "Lv.5",
            brief = "选择毕业项目，先写需求和验收标准，再独立完成第一版。",
            acceptance = listOf("功能按验收标准可操作", "关键流程有测试", "能在没有 AI 生成代码的情况下解释每段实现"),
        ),
    )
}

data class AiIndependenceProfile(
    val level: String,
    val experience: Int,
    val dependencyIndex: Int,
    val aiFreeCompleted: Int,
    val aiFreeTotal: Int,
)

object AiIndependenceEngine {
    fun build(
        completedLessons: Int,
        completedProjects: Int,
        completedTraining: Int,
        aiPromptCount: Int,
        aiFreeCompletedIds: Set<String>,
    ): AiIndependenceProfile {
        val experience = completedLessons * 12 + completedProjects * 45 + completedTraining * 8 +
            aiFreeCompletedIds.size * 30
        val level = when {
            experience >= 800 -> "独立开发者"
            experience >= 520 -> "Lv.5 综合实践"
            experience >= 320 -> "Lv.4 项目进阶"
            experience >= 170 -> "Lv.3 独立调试"
            experience >= 70 -> "Lv.2 基础实践"
            else -> "Lv.1 起步"
        }
        val manualActions = completedLessons + completedProjects + completedTraining +
            aiFreeCompletedIds.size * 2
        val dependencyIndex = if (manualActions + aiPromptCount == 0) {
            0
        } else {
            (aiPromptCount * 100 / (manualActions + aiPromptCount)).coerceIn(0, 100)
        }
        return AiIndependenceProfile(
            level = level,
            experience = experience,
            dependencyIndex = dependencyIndex,
            aiFreeCompleted = aiFreeCompletedIds.size,
            aiFreeTotal = AiIndependenceCatalog.challenges.size,
        )
    }
}

enum class SearchResultKind(val label: String) {
    LESSON("课程"),
    PROJECT("项目"),
    TRAINING("训练"),
    LIBRARY("第三方库"),
    ERROR("错误博物馆"),
    ENGINEERING("工程实践"),
}

data class GlobalSearchResult(
    val id: String,
    val title: String,
    val subtitle: String,
    val kind: SearchResultKind,
    val routeId: String,
    val favoriteKey: String,
)

object GlobalSearchEngine {
    fun search(query: String, limit: Int = 30): List<GlobalSearchResult> {
        val needle = query.trim()
        if (needle.isEmpty()) return emptyList()
        val matches = buildList {
            CourseCatalog.allLessons.forEach { lesson ->
                if (lesson.title.contains(needle, ignoreCase = true) ||
                    lesson.stage.contains(needle, ignoreCase = true) ||
                    lesson.knowledge.any { it.contains(needle, ignoreCase = true) }
                ) {
                    add(
                        GlobalSearchResult(
                            id = lesson.id,
                            title = lesson.title,
                            subtitle = lesson.stage,
                            kind = SearchResultKind.LESSON,
                            routeId = lesson.id,
                            favoriteKey = "lesson:${lesson.id}",
                        ),
                    )
                }
            }
            ProjectCatalog.all.forEach { project ->
                if (project.title.contains(needle, ignoreCase = true) ||
                    project.goal.contains(needle, ignoreCase = true) ||
                    project.knowledge.any { it.contains(needle, ignoreCase = true) }
                ) {
                    add(
                        GlobalSearchResult(
                            id = project.id,
                            title = project.title,
                            subtitle = project.level,
                            kind = SearchResultKind.PROJECT,
                            routeId = project.id,
                            favoriteKey = "project:${project.id}",
                        ),
                    )
                }
            }
            TrainingCatalog.all.forEach { exercise ->
                if (exercise.title.contains(needle, ignoreCase = true) ||
                    exercise.prompt.contains(needle, ignoreCase = true)
                ) {
                    add(
                        GlobalSearchResult(
                            id = exercise.id,
                            title = exercise.title,
                            subtitle = exercise.type.label,
                            kind = SearchResultKind.TRAINING,
                            routeId = exercise.id,
                            favoriteKey = "training:${exercise.id}",
                        ),
                    )
                }
            }
            LibraryCatalog.search(needle).forEach { library ->
                add(
                    GlobalSearchResult(
                        id = library.id,
                        title = library.name,
                        subtitle = library.summary,
                        kind = SearchResultKind.LIBRARY,
                        routeId = library.id,
                        favoriteKey = "library:${library.id}",
                    ),
                )
            }
            ErrorMuseumCatalog.search(needle).forEach { error ->
                add(
                    GlobalSearchResult(
                        id = error.id,
                        title = error.title,
                        subtitle = error.errorType,
                        kind = SearchResultKind.ERROR,
                        routeId = error.id,
                        favoriteKey = "error:${error.id}",
                    ),
                )
            }
            EngineeringCatalog.search(needle).forEach { module ->
                add(
                    GlobalSearchResult(
                        id = module.id,
                        title = module.title,
                        subtitle = module.category.label,
                        kind = SearchResultKind.ENGINEERING,
                        routeId = module.id,
                        favoriteKey = "engineering:${module.id}",
                    ),
                )
            }
        }
        return matches.distinctBy { it.favoriteKey }.take(limit)
    }
}
