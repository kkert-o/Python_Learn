from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PythonErrorExplanation:
    error_type: str
    title: str
    message: str
    suggestions: tuple[str, ...]
    line_number: int | None = None


class PythonErrorExplainer:
    _exception_pattern = re.compile(
        r"(?m)^([A-Za-z_][A-Za-z0-9_.]*):\s*(.*)$"
    )
    _line_pattern = re.compile(r'File ".*?", line (\d+)')

    def explain(self, stderr: str) -> PythonErrorExplanation | None:
        if not stderr.strip():
            return None
        matches = self._exception_pattern.findall(stderr)
        if not matches:
            return PythonErrorExplanation(
                error_type="RuntimeError",
                title="程序运行失败",
                message="程序没有正常结束。请查看错误输出中的最后几行。",
                suggestions=("从最底部的异常信息开始检查。", "确认错误发生前修改了哪些代码。"),
            )
        error_type, message = matches[-1]
        line_match = self._line_pattern.search(stderr)
        line_number = int(line_match.group(1)) if line_match else None
        title, explanation, suggestions = self._details(error_type, message)
        return PythonErrorExplanation(
            error_type=error_type,
            title=title,
            message=explanation,
            suggestions=tuple(suggestions),
            line_number=line_number,
        )

    @staticmethod
    def _details(
        error_type: str,
        message: str,
    ) -> tuple[str, str, tuple[str, ...]]:
        short_type = error_type.rsplit(".", 1)[-1]
        details: dict[str, tuple[str, tuple[str, ...]]] = {
            "NameError": (
                "使用了尚未定义的名称。",
                (
                    "检查变量名是否拼写正确，并确认它在使用前已经赋值。",
                    "检查变量是否只在另一个函数或缩进块里定义。",
                ),
            ),
            "SyntaxError": (
                "Python 无法解析这行代码。",
                (
                    "检查括号、引号、冒号和逗号是否完整配对。",
                    "查看提示行号的前一行，语法错误经常由上一行引起。",
                ),
            ),
            "IndentationError": (
                "代码缩进不符合 Python 规则。",
                (
                    "同级代码应保持相同的缩进宽度。",
                    "函数、条件和循环后面的代码需要正确缩进。",
                ),
            ),
            "TabError": (
                "同一个代码块混用了 Tab 和空格。",
                ("将缩进统一为 4 个空格。",),
            ),
            "TypeError": (
                "操作中的数据类型不兼容。",
                (
                    "检查参与运算或函数调用的值分别是什么类型。",
                    "需要时先使用 int()、float() 或 str() 转换类型。",
                ),
            ),
            "ValueError": (
                "值的类型可能正确，但内容无法用于当前操作。",
                (
                    "检查输入内容是否符合函数要求。",
                    "使用 try/except 处理无法转换的用户输入。",
                ),
            ),
            "ZeroDivisionError": (
                "程序尝试除以零。",
                (
                    "在除法前判断除数是否为 0。",
                    "检查分母是否来自输入或计算结果。",
                ),
            ),
            "IndexError": (
                "访问了列表或序列中不存在的下标。",
                (
                    "检查下标是否从 0 开始，并小于序列长度。",
                    "访问前可以先打印 len(sequence)。",
                ),
            ),
            "KeyError": (
                "字典中不存在正在访问的键。",
                (
                    "检查键名拼写和大小写。",
                    "不确定键是否存在时使用 dict.get()。",
                ),
            ),
            "AttributeError": (
                "对象没有正在访问的属性或方法。",
                (
                    "检查对象类型和属性名是否匹配。",
                    "可以先用 type(value) 查看对象类型。",
                ),
            ),
            "ModuleNotFoundError": (
                "Python 找不到需要导入的模块。",
                (
                    "确认模块名称拼写正确。",
                    "第三方库需要先在当前 Python 环境中安装。",
                ),
            ),
            "ImportError": (
                "模块存在，但导入的内容不可用。",
                (
                    "检查导入名称和模块版本。",
                    "确认当前项目没有同名文件覆盖标准模块。",
                ),
            ),
            "UnboundLocalError": (
                "局部变量在赋值前被使用。",
                (
                    "在函数内使用变量前先赋值。",
                    "需要修改外部变量时明确使用 global 或 nonlocal。",
                ),
            ),
            "RecursionError": (
                "递归调用层数过深。",
                (
                    "确认递归函数包含能够结束递归的条件。",
                    "每次递归应让问题规模逐步缩小。",
                ),
            ),
            "EOFError": (
                "程序等待输入，但没有更多输入可用。",
                (
                    "程序使用 input() 时，需要在输入区提供内容。",
                    "确认提供的输入行数足够完成所有 input() 调用。",
                ),
            ),
            "KeyboardInterrupt": (
                "程序被手动中断。",
                ("如果并非你主动停止，检查是否误触了停止操作。",),
            ),
        }
        title, suggestions = details.get(
            short_type,
            (
                f"程序触发了 {short_type}。",
                (
                    "查看完整错误输出，从最底部的异常类型和消息开始排查。",
                    "根据 traceback 标出的文件与行号检查对应代码。",
                ),
            ),
        )
        return short_type, f"{title}\n原始信息：{message}", suggestions

