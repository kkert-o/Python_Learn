import io
import json
import sys
import traceback


MAX_STEP_COUNT = 300000


class BoundedInput:
    def __init__(self, text):
        self.lines = iter(text.replace("\r\n", "\n").split("\n"))

    def __call__(self, prompt=""):
        if prompt:
            sys.stdout.write(prompt)
            sys.stdout.flush()
        try:
            return next(self.lines)
        except StopIteration:
            raise EOFError("运行台输入已经用完。请在输入区为每一行 input 准备内容。")


def run(code, stdin=""):
    output = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_trace = sys.gettrace()
    sys.stdout = output
    sys.stderr = output
    state = {"steps": 0}

    def trace(frame, event, arg):
        if event == "line":
            state["steps"] += 1
            if state["steps"] > MAX_STEP_COUNT:
                raise RuntimeError("程序运行次数过多，可能进入了无限循环。请补上循环停止条件后再运行。")
        return trace

    try:
        compiled = compile(code, "<user_code>", "exec")
        sys.settrace(trace)
        exec(compiled, {"__name__": "__main__", "input": BoundedInput(stdin)})
        return json.dumps({"ok": True, "output": output.getvalue()})
    except BaseException as error:
        return json.dumps(
            {
                "ok": False,
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
                "output": output.getvalue(),
            }
        )
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.settrace(old_trace)
