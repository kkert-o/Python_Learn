from __future__ import annotations

import textwrap

from app.training.models import TrainingExercise, TrainingType


def _code(value: str) -> str:
    return textwrap.dedent(value).strip()


class TrainingCatalog:
    def __init__(self, exercises: tuple[TrainingExercise, ...]) -> None:
        self.all = exercises
        self._by_id = {exercise.exercise_id: exercise for exercise in exercises}

    def by_id(self, exercise_id: str) -> TrainingExercise | None:
        return self._by_id.get(exercise_id)

    def by_type(self, training_type: TrainingType) -> list[TrainingExercise]:
        return [exercise for exercise in self.all if exercise.type is training_type]

    def by_ids(self, exercise_ids: set[str]) -> list[TrainingExercise]:
        return [
            exercise for exercise in self.all if exercise.exercise_id in exercise_ids
        ]


training_catalog = TrainingCatalog(
    (
        TrainingExercise(
            "read-variable",
            "variable",
            TrainingType.READ_CODE,
            "变量保存了什么",
            "先阅读代码，不要急着运行。",
            _code(
                """
                name = "小林"
                age = 18
                print(name, age)
                """
            ),
            "关于这段代码，哪项说法正确？",
            "引号中的内容是字符串，18 没有引号，是整数。print 会把两者依次显示。",
            (
                "name 保存字符串，age 保存整数",
                "name 和 age 都保存字符串",
                "age 会被自动打印成字符串 18 岁",
                "代码会报 NameError",
            ),
            0,
            (
                "先看等号右边的值有没有引号。",
                "再确认 print 使用的是已经定义过的变量。",
            ),
        ),
        TrainingExercise(
            "read-if",
            "if",
            TrainingType.READ_CODE,
            "条件分支会走哪里",
            "阅读条件判断，判断哪个分支会执行。",
            _code(
                """
                score = 60
                if score >= 60:
                    print("通过")
                else:
                    print("继续加油")
                """
            ),
            "score 正好等于 60 时，程序会输出什么？",
            ">= 表示大于或等于，60 >= 60 成立，所以执行 if 分支。",
            ("通过", "继续加油", "两个都输出", "什么也不输出"),
            0,
            (
                "注意 >= 和 > 的区别。",
                "条件为 True 时执行缩进在 if 下面的代码。",
            ),
        ),
        TrainingExercise(
            "read-loop",
            "for",
            TrainingType.READ_CODE,
            "循环执行几次",
            "观察 range 的起止值。",
            _code(
                """
                for number in range(1, 4):
                    print(number)
                """
            ),
            "循环体会执行几次？",
            "range(1, 4) 产生 1、2、3，不包含结束值 4，所以执行 3 次。",
            ("2 次", "3 次", "4 次", "无限次"),
            1,
            (
                "range 的第二个参数不包含在结果中。",
                "列出 range 实际产生的数字。",
            ),
        ),
        TrainingExercise(
            "read-function",
            "function",
            TrainingType.READ_CODE,
            "函数返回了什么",
            "先找函数定义，再找函数调用。",
            _code(
                """
                def add(a, b):
                    return a + b

                result = add(1, 2)
                print(result)
                """
            ),
            "最终输出的结果是什么？",
            "调用 add(1, 2) 时，a 是 1、b 是 2，return 返回 3。",
            ("a + b", "3", "12", "None"),
            1,
            (
                "把实参依次代入形参。",
                "return 会把计算结果交给调用处。",
            ),
        ),
        TrainingExercise(
            "predict-add",
            "variable",
            TrainingType.PREDICT_OUTPUT,
            "增量赋值",
            "先选择你预测的输出，再运行代码验证。",
            _code(
                """
                x = 10
                x += 5
                print(x)
                """
            ),
            "这段代码会输出什么？",
            "x += 5 等价于 x = x + 5，所以 10 加 5 后得到 15。",
            ("10", "15", "5", "报错"),
            1,
            ("把 += 展开成普通赋值语句。",),
        ),
        TrainingExercise(
            "predict-else",
            "if",
            TrainingType.PREDICT_OUTPUT,
            "判断奇偶",
            "先判断条件结果，再运行验证。",
            _code(
                """
                number = 7
                if number % 2 == 0:
                    print("偶数")
                else:
                    print("奇数")
                """
            ),
            "这段代码会输出什么？",
            "7 除以 2 的余数是 1，条件为 False，因此执行 else 分支。",
            ("偶数", "奇数", "7", "报错"),
            1,
            (
                "% 表示取余数。",
                "偶数除以 2 的余数才是 0。",
            ),
        ),
        TrainingExercise(
            "predict-list",
            "list",
            TrainingType.PREDICT_OUTPUT,
            "列表追加",
            "注意列表在什么位置被修改。",
            _code(
                """
                numbers = [1, 2]
                numbers.append(3)
                print(numbers)
                """
            ),
            "这段代码会输出什么？",
            "append(3) 会把 3 加到列表末尾，原来的列表变成 [1, 2, 3]。",
            ("[1, 2]", "[1, 2, 3]", "3", "报错"),
            1,
            (
                "append 修改的是原列表。",
                "print 输出的是修改后的完整列表。",
            ),
        ),
        TrainingExercise(
            "predict-dict",
            "dict",
            TrainingType.PREDICT_OUTPUT,
            "字典读取",
            "找到键对应的值。",
            _code(
                """
                person = {"name": "小林", "city": "上海"}
                print(person["name"])
                """
            ),
            "这段代码会输出什么？",
            '字典通过键 "name" 找到对应的值 "小林"。',
            ("name", "小林", "上海", "报错"),
            1,
            ("方括号里的是键，不是位置编号。",),
        ),
        TrainingExercise(
            "complete-range",
            "for",
            TrainingType.COMPLETE_CODE,
            "输出 1 到 100",
            "补全 range，让程序输出 1、2、3 一直到 100。",
            "for number in range(____):\n    print(number)",
            "在编辑器中补全代码后点击检查。",
            "range(1, 101) 会产生 1 到 100。结束值 101 本身不会出现。",
            hints=(
                "range 的起点是 1。",
                "想要包含 100，结束值要写 101。",
            ),
            starter_code="for number in range(____):\n    print(number)",
            required_snippets=("for", "range(1,101)", "print"),
            reference_solution="for number in range(1, 101):\n    print(number)",
        ),
        TrainingExercise(
            "complete-function",
            "function",
            TrainingType.COMPLETE_CODE,
            "补全求和函数",
            "让 add 函数返回两个参数的和。",
            "def add(a, b):\n    ____",
            "在编辑器中补全函数体后点击检查。",
            "函数体使用 return a + b，把计算结果返回给调用处。",
            hints=(
                "函数需要把结果交回调用处。",
                "使用关键字 return。",
            ),
            starter_code="def add(a, b):\n    ____",
            required_snippets=("defadd(a,b)", "returna+b"),
            reference_solution="def add(a, b):\n    return a + b",
        ),
        TrainingExercise(
            "complete-dict-get",
            "dict",
            TrainingType.COMPLETE_CODE,
            "安全读取联系人",
            "键不存在时不要报错，而是返回“未找到”。",
            _code(
                """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.____
                print(phone)
                """
            ),
            "补全字典读取代码后点击检查。",
            '使用 contacts.get(name, "未找到")，不存在键时会返回默认值。',
            hints=(
                "字典的 get 方法可以设置默认值。",
                "要把变量 name 当作键传进去。",
            ),
            starter_code=_code(
                """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.____
                print(phone)
                """
            ),
            required_snippets=('contacts.get(name,"未找到")', "print"),
            reference_solution=_code(
                """
                contacts = {"小林": "13800000000"}
                name = "小王"
                phone = contacts.get(name, "未找到")
                print(phone)
                """
            ),
        ),
        TrainingExercise(
            "complete-file-write",
            "file",
            TrainingType.COMPLETE_CODE,
            "写入文本文件",
            "以写入模式打开文件，并写入一行内容。",
            _code(
                """
                with open("notes.txt", ____) as file:
                    file.____("今天学习了 Python")
                """
            ),
            "补全打开模式和写入方法后点击检查。",
            '写入模式是 "w"，file.write(...) 会把字符串写入文件。',
            hints=(
                "只写内容应使用 write 模式。",
                '打开模式的参数是字符串 "w"。',
            ),
            starter_code=_code(
                """
                with open("notes.txt", ____) as file:
                    file.____("今天学习了 Python")
                """
            ),
            required_snippets=('open("notes.txt","w")', "file.write"),
            reference_solution=_code(
                """
                with open("notes.txt", "w") as file:
                    file.write("今天学习了 Python")
                """
            ),
        ),
        TrainingExercise(
            "debug-name",
            "errors",
            TrainingType.DEBUG_LAB,
            "变量名拼写错误",
            "先判断哪一行有问题，再修改代码让它正常运行。",
            _code(
                """
                name = "Tom"
                print(nam)
                """
            ),
            "请在编辑器中修复错误。",
            "定义的是 name，打印时却写成了 nam，Python 找不到这个名称。",
            hints=(
                "错误类型通常是 NameError。",
                "比较 print 里的名字和第一行变量名。",
            ),
            starter_code=_code(
                """
                name = "Tom"
                print(nam)
                """
            ),
            required_snippets=('name="Tom"', "print(name)"),
            forbidden_snippets=("print(nam)",),
            reference_solution='name = "Tom"\nprint(name)',
        ),
        TrainingExercise(
            "debug-compare",
            "if",
            TrainingType.DEBUG_LAB,
            "比较运算符写错",
            "修复条件判断，让程序能够正常运行。",
            _code(
                """
                score = 85
                if score = 85:
                    print("正确")
                """
            ),
            "请在编辑器中修复错误。",
            "= 是赋值，== 才是比较是否相等。if 条件中应使用 ==。",
            hints=(
                "错误会在运行代码之前被 Python 发现。",
                "检查 if 条件中的等号数量。",
            ),
            starter_code=_code(
                """
                score = 85
                if score = 85:
                    print("正确")
                """
            ),
            required_snippets=("ifscore==85:", "print"),
            forbidden_snippets=("ifscore=85:",),
            reference_solution='score = 85\nif score == 85:\n    print("正确")',
        ),
        TrainingExercise(
            "debug-range",
            "for",
            TrainingType.DEBUG_LAB,
            "少输出了一个数字",
            "程序应该输出 1 到 5，但现在只输出到 4。",
            _code(
                """
                for number in range(1, 5):
                    print(number)
                """
            ),
            "请在编辑器中修复范围。",
            "range 不包含结束值，要输出 5，结束值需要写成 6。",
            hints=(
                "先列出 range(1, 5) 实际产生的数字。",
                "把结束值增加 1。",
            ),
            starter_code=_code(
                """
                for number in range(1, 5):
                    print(number)
                """
            ),
            required_snippets=("range(1,6)", "print"),
            forbidden_snippets=("range(1,5)",),
            reference_solution="for number in range(1, 6):\n    print(number)",
        ),
        TrainingExercise(
            "debug-list-method",
            "list",
            TrainingType.DEBUG_LAB,
            "列表方法不存在",
            "把数字加入列表，但当前方法名不正确。",
            _code(
                """
                scores = [80, 90]
                scores.add(100)
                print(scores)
                """
            ),
            "请在编辑器中修复方法名。",
            "列表在末尾添加元素使用 append，add 不是列表方法。",
            hints=(
                "错误类型通常是 AttributeError。",
                "回忆列表添加元素使用哪个方法。",
            ),
            starter_code=_code(
                """
                scores = [80, 90]
                scores.add(100)
                print(scores)
                """
            ),
            required_snippets=("scores.append(100)", "print"),
            forbidden_snippets=("scores.add(100)",),
            reference_solution="scores = [80, 90]\nscores.append(100)\nprint(scores)",
        ),
        TrainingExercise(
            "debug-type-conversion",
            "types",
            TrainingType.DEBUG_LAB,
            "输入数字不能直接相加",
            "程序需要读取年龄并与 1 相加，现在会报 TypeError。",
            _code(
                """
                age = input("年龄：")
                print(age + 1)
                """
            ),
            "请修复类型转换。",
            "input() 返回字符串，计算结果前应使用 int() 转换为整数。",
            hints=(
                "先判断 input 返回值是什么类型。",
                "需要整数计算时使用 int()。",
            ),
            starter_code=_code(
                """
                age = input("年龄：")
                print(age + 1)
                """
            ),
            required_snippets=("int(input(", "print"),
            forbidden_snippets=("age=input(",),
            reference_solution='age = int(input("年龄："))\nprint(age + 1)',
        ),
        TrainingExercise(
            "debug-dict-get",
            "dict",
            TrainingType.DEBUG_LAB,
            "字典键不存在",
            "查询一个可能不存在的电话字段，不要因为 KeyError 崩溃。",
            _code(
                """
                person = {"name": "小林"}
                print(person["phone"])
                """
            ),
            "请使用安全的字典读取方式。",
            "get() 在键不存在时返回指定默认值，不会抛出 KeyError。",
            hints=(
                "字典方括号要求键一定存在。",
                "使用 get 并为未知号码设置默认值。",
            ),
            starter_code=_code(
                """
                person = {"name": "小林"}
                print(person["phone"])
                """
            ),
            required_snippets=('person.get("phone","未记录")', "print"),
            forbidden_snippets=('person["phone"]',),
            reference_solution='person = {"name": "小林"}\nprint(person.get("phone", "未记录"))',
        ),
        TrainingExercise(
            "debug-indentation",
            "if",
            TrainingType.DEBUG_LAB,
            "缩进层级错误",
            "让“通过”只在成绩达标时输出。",
            _code(
                """
                score = 80
                if score >= 60:
                print("通过")
                """
            ),
            "请修复代码块的缩进。",
            "if 下面的代码必须统一缩进，Python 通过缩进判断代码属于哪个代码块。",
            hints=(
                "报错通常是 IndentationError。",
                "print 需要缩进到 if 代码块内部。",
            ),
            starter_code=_code(
                """
                score = 80
                if score >= 60:
                print("通过")
                """
            ),
            required_snippets=('if score >= 60:\n    print("通过")',),
            reference_solution='score = 80\nif score >= 60:\n    print("通过")',
            preserve_indentation=True,
        ),
        TrainingExercise(
            "debug-file-exists",
            "file",
            TrainingType.DEBUG_LAB,
            "读取前检查文件",
            "文件不存在时给出提示，不要直接抛出 FileNotFoundError。",
            _code(
                """
                from pathlib import Path
                path = Path("note.txt")
                print(path.read_text(encoding="utf-8"))
                """
            ),
            "请增加文件存在检查。",
            "读取前使用 path.exists() 判断，并给用户明确提示。",
            hints=(
                "Path 对象提供 exists()。",
                "else 分支告诉用户需要先创建文件。",
            ),
            starter_code=_code(
                """
                from pathlib import Path
                path = Path("note.txt")
                print(path.read_text(encoding="utf-8"))
                """
            ),
            required_snippets=("ifpath.exists():", "read_text", "else:"),
            reference_solution=_code(
                """
                from pathlib import Path
                path = Path("note.txt")
                if path.exists():
                    print(path.read_text(encoding="utf-8"))
                else:
                    print("请先创建 note.txt")
                """
            ),
        ),
    )
)

