from __future__ import annotations

from app.toolbox.models import (
    EngineeringCategory,
    EngineeringModule,
    ErrorMuseumEntry,
    LibraryCategory,
    LibraryEntry,
)


class LibraryCatalog:
    all = (
        LibraryEntry(
            "requests",
            "requests",
            "requests",
            LibraryCategory.NETWORK,
            "易读的 HTTP 客户端，适合调用 API 和理解请求响应。",
            "访问自己拥有的服务、公开 API 或获得授权的数据接口。",
            "pip install requests",
            'import requests\nr = requests.get(url, timeout=8)\nprint(r.status_code)',
            "requests",
        ),
        LibraryEntry(
            "httpx",
            "httpx",
            "httpx",
            LibraryCategory.NETWORK,
            "同时支持同步和异步的现代 HTTP 客户端。",
            "需要并发请求或同时使用标准 HTTP/2 能力的 Python 项目。",
            "pip install httpx",
            'import httpx\nr = httpx.get(url, timeout=8)\nprint(r.status_code)',
            "requests",
        ),
        LibraryEntry(
            "beautifulsoup4",
            "BeautifulSoup",
            "bs4",
            LibraryCategory.NETWORK,
            "用标签选择器从 HTML/XML 中提取结构化内容。",
            "解析获得授权的静态页面，优先选择官方 API。",
            "pip install beautifulsoup4",
            'from bs4 import BeautifulSoup\nsoup = BeautifulSoup(html, "html.parser")',
            "html",
        ),
        LibraryEntry(
            "pandas",
            "pandas",
            "pandas",
            LibraryCategory.DATA,
            "处理表格数据、清洗缺失值和做聚合分析的核心库。",
            "读取 CSV/Excel，筛选、合并、统计并输出分析结果。",
            "pip install pandas",
            'import pandas as pd\ndf = pd.read_csv("scores.csv")\nprint(df.groupby("class")["score"].mean())',
            "pandas",
        ),
        LibraryEntry(
            "numpy",
            "NumPy",
            "numpy",
            LibraryCategory.DATA,
            "面向数组和数值计算的 Python 基础工具。",
            "批量数值运算、矩阵计算和机器学习数据准备。",
            "pip install numpy",
            "import numpy as np\nvalues = np.array([1, 2, 3])\nprint(values.mean())",
            "numpy",
        ),
        LibraryEntry(
            "matplotlib",
            "Matplotlib",
            "matplotlib",
            LibraryCategory.DATA,
            "把数据绘制成折线图、柱状图、散点图等静态图表。",
            "学习数据可视化，或把分析结果输出为图片用于报告。",
            "pip install matplotlib",
            'import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])\nplt.savefig("chart.png")',
            "visualization",
        ),
        LibraryEntry(
            "sqlalchemy",
            "SQLAlchemy",
            "sqlalchemy",
            LibraryCategory.DATABASE,
            "成熟 ORM 与 SQL 工具集，减少重复数据库代码。",
            "中型应用的数据建模、事务和多数据库适配。",
            "pip install sqlalchemy",
            'from sqlalchemy import create_engine\nengine = create_engine("sqlite:///study.db")',
            "sqlite",
        ),
        LibraryEntry(
            "flask",
            "Flask",
            "flask",
            LibraryCategory.WEB,
            "轻量 Web 框架，用路由把 URL 和 Python 函数连接起来。",
            "构建小型服务、内部工具、管理页面和 Web 原理学习项目。",
            "pip install flask",
            'from flask import Flask\napp = Flask(__name__)\n\n@app.get("/health")\ndef health():\n    return {"status": "ok"}',
            "flask",
        ),
        LibraryEntry(
            "fastapi",
            "FastAPI",
            "fastapi",
            LibraryCategory.WEB,
            "基于类型提示的现代 Web API 框架，自动生成接口文档。",
            "把自己的 Python 能力封装成网页或移动端可调用的服务。",
            "pip install fastapi uvicorn",
            'from fastapi import FastAPI\napp = FastAPI()\n\n@app.get("/health")\ndef health():\n    return {"ok": True}',
            "fastapi",
        ),
        LibraryEntry(
            "pytest",
            "pytest",
            "pytest",
            LibraryCategory.TESTING,
            "用简洁的断言组织自动化测试。",
            "验证函数、接口和数据流程，防止代码修改引入回归。",
            "pip install pytest",
            "def test_add():\n    assert 1 + 2 == 3",
            "testing",
        ),
        LibraryEntry(
            "ruff",
            "Ruff",
            "ruff",
            LibraryCategory.TESTING,
            "快速检查常见代码问题并统一代码风格。",
            "在提交前发现未使用变量、导入顺序和常见缺陷。",
            "pip install ruff",
            "ruff check .\nruff format .",
            "quality",
        ),
        LibraryEntry(
            "click",
            "Click",
            "click",
            LibraryCategory.TOOLS,
            "快速构建结构清晰的命令行工具。",
            "为自动化脚本、数据处理任务和开发工具提供命令参数。",
            "pip install click",
            'import click\n\n@click.command()\n@click.option("--name", prompt=True)\ndef hello(name):\n    click.echo(f"Hello {name}")',
            "module",
        ),
        LibraryEntry(
            "rich",
            "Rich",
            "rich",
            LibraryCategory.TOOLS,
            "在终端输出彩色文本、表格、进度条和结构化信息。",
            "改善命令行工具的可读性和长时间任务的进度反馈。",
            "pip install rich",
            'from rich.console import Console\nconsole = Console()\nconsole.print("Python", style="bold green")',
            "quality",
        ),
        LibraryEntry(
            "openai",
            "OpenAI Python SDK",
            "openai",
            LibraryCategory.AI,
            "在 Python 项目中调用大模型接口。",
            "把总结、分类、问答等 AI 能力接入自己的应用。",
            "pip install openai",
            'import os\nfrom openai import OpenAI\nclient = OpenAI(api_key=os.environ["OPENAI_API_KEY"])',
            "ai-api",
        ),
        LibraryEntry(
            "scikit-learn",
            "scikit-learn",
            "sklearn",
            LibraryCategory.AI,
            "经典机器学习算法和数据处理流程工具。",
            "分类、回归、聚类和模型评估入门。",
            "pip install scikit-learn",
            "from sklearn.linear_model import LinearRegression\nmodel = LinearRegression()",
            "machine-learning",
        ),
    )

    @classmethod
    def by_id(cls, library_id: str) -> LibraryEntry | None:
        return next(
            (entry for entry in cls.all if entry.library_id == library_id),
            None,
        )

    @classmethod
    def search(
        cls,
        query: str,
        category: LibraryCategory | None = None,
    ) -> list[LibraryEntry]:
        needle = query.strip().casefold()
        return [
            entry
            for entry in cls.all
            if (category is None or entry.category == category)
            and (
                not needle
                or needle in entry.name.casefold()
                or needle in entry.summary.casefold()
                or needle in entry.use_case.casefold()
                or needle in entry.category.value.casefold()
            )
        ]


class ErrorMuseumCatalog:
    all = (
        ErrorMuseumEntry(
            "name-error",
            "变量名拼写不一致",
            "NameError",
            "Python 提示 name 'socre' is not defined。",
            "定义变量时写的是 score，使用时却写成了 socre。",
            "score = 85\nprint(socre)",
            "score = 85\nprint(score)",
            "使用有意义的变量名，并借助编辑器补全检查拼写。",
            "errors",
        ),
        ErrorMuseumEntry(
            "syntax-error",
            "if 条件用了赋值号",
            "SyntaxError",
            "Python 在运行前就指出条件表达式无效。",
            "= 是赋值，== 才是判断两个值是否相等。",
            'score = 85\nif score = 85:\n    print("正确")',
            'score = 85\nif score == 85:\n    print("正确")',
            "写条件判断时先确认这里是在赋值，还是在比较。",
            "if",
        ),
        ErrorMuseumEntry(
            "type-error",
            "文字和数字直接相加",
            "TypeError",
            "报错提到 str 和 int 不能直接相加。",
            "input() 返回字符串，直接和数字计算前必须转换类型。",
            'age = input("年龄：")\nprint(age + 1)',
            'age = int(input("年龄："))\nprint(age + 1)',
            "看到 input() 时先判断后面把它当文字还是当数字。",
            "types",
        ),
        ErrorMuseumEntry(
            "value-error",
            "转换了非数字内容",
            "ValueError",
            'int("abc") 会提示字符串不是合法整数。',
            "转换函数只能处理格式正确的内容。",
            'count = int("很多")\nprint(count)',
            'text = "很多"\nif text.isdigit():\n    count = int(text)\nelse:\n    print("请输入数字")',
            "处理真实输入时使用校验或 try / except。",
            "errors",
        ),
        ErrorMuseumEntry(
            "index-error",
            "访问了列表不存在的位置",
            "IndexError",
            "list index out of range，说明索引超出列表范围。",
            "长度为 3 的列表有效索引只到 2，却访问了索引 3。",
            'names = ["小林", "小王", "小陈"]\nprint(names[3])',
            'names = ["小林", "小王", "小陈"]\nprint(names[-1])',
            "访问索引前确认长度，或用循环避免硬编码位置。",
            "list",
        ),
        ErrorMuseumEntry(
            "key-error",
            "读取字典里不存在的键",
            "KeyError",
            "字典方括号读取内容时提示某个 key 不存在。",
            "方括号读取要求键一定存在。",
            'person = {"name": "小林"}\nprint(person["phone"])',
            'person = {"name": "小林"}\nprint(person.get("phone", "未记录"))',
            "不确定键是否存在时使用 get() 并给出默认值。",
            "dict",
        ),
        ErrorMuseumEntry(
            "attribute-error",
            "调用了不存在的列表方法",
            "AttributeError",
            "列表对象没有 add 方法。",
            "把集合的 add() 记忆成了列表方法。",
            "scores = [80, 90]\nscores.add(100)",
            "scores = [80, 90]\nscores.append(100)",
            "先确认数据类型，再选择它真正支持的方法。",
            "list",
        ),
        ErrorMuseumEntry(
            "file-error",
            "读取不存在的文件",
            "FileNotFoundError",
            "程序找不到指定路径的文件。",
            "文件名、目录或工作目录与预期不一致。",
            'with open("score.txt", "r", encoding="utf-8") as file:\n    print(file.read())',
            'from pathlib import Path\npath = Path("score.txt")\nif path.exists():\n    print(path.read_text(encoding="utf-8"))\nelse:\n    print("请先创建 score.txt")',
            "使用明确路径，并在读取前判断文件是否存在。",
            "file",
        ),
    )

    @classmethod
    def by_id(cls, error_id: str) -> ErrorMuseumEntry | None:
        return next(
            (entry for entry in cls.all if entry.error_id == error_id),
            None,
        )

    @classmethod
    def search(cls, query: str) -> list[ErrorMuseumEntry]:
        needle = query.strip().casefold()
        if not needle:
            return list(cls.all)
        return [
            entry
            for entry in cls.all
            if needle in entry.title.casefold()
            or needle in entry.error_type.casefold()
            or needle in entry.cause.casefold()
            or needle in entry.symptom.casefold()
        ]


class EngineeringCatalog:
    all = (
        EngineeringModule(
            "git-basics",
            "Git 基础工作流",
            EngineeringCategory.GIT,
            "用版本历史保护每次可运行的修改。",
            ("提交前查看变更", "一次提交只做一类修改", "提交信息说明原因和结果"),
            ('git status', 'git diff', 'git add .', 'git commit -m "说明"'),
            "git",
        ),
        EngineeringModule(
            "git-branches",
            "分支与合并",
            EngineeringCategory.GIT,
            "在独立分支开发功能，验证后再合并。",
            ("功能分支从稳定版本开始", "合并前运行测试", "冲突时保留正确逻辑"),
            ("git switch -c feature/task", "git switch main", "git merge feature/task"),
            "git",
        ),
        EngineeringModule(
            "quality-review",
            "代码质量检查",
            EngineeringCategory.QUALITY,
            "让代码更容易读、修改和测试。",
            ("函数只做一件事", "变量名表达真实含义", "错误有处理路径", "重复逻辑及时提取"),
            ("ruff check .", "ruff format .", "python -m compileall ."),
            "quality",
        ),
        EngineeringModule(
            "pytest-basics",
            "最小测试闭环",
            EngineeringCategory.TESTING,
            "每次修改后自动确认关键行为没有倒退。",
            ("测试正常路径", "测试边界值", "测试错误输入", "失败时先复现再修复"),
            ("pytest -q", "pytest --cov=.", "python -m unittest"),
            "testing",
        ),
    )

    @classmethod
    def by_id(cls, module_id: str) -> EngineeringModule | None:
        return next(
            (module for module in cls.all if module.module_id == module_id),
            None,
        )

    @classmethod
    def search(cls, query: str) -> list[EngineeringModule]:
        needle = query.strip().casefold()
        if not needle:
            return list(cls.all)
        return [
            module
            for module in cls.all
            if needle in module.title.casefold()
            or needle in module.summary.casefold()
            or needle in module.category.value.casefold()
        ]
