from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

from app.runtime import PythonErrorExplainer, PythonRunner


def _qt_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _run(
    paths,
    code: str,
    *,
    inputs: list[str] | None = None,
    timeout: float = 2.0,
    output_limit: int = 1_048_576,
):
    _qt_app()
    runner = PythonRunner(paths)
    results = []
    inputs_to_send = list(inputs or [])
    loop = QEventLoop()

    def on_input(_prompt: str) -> None:
        if inputs_to_send:
            runner.submit_input(inputs_to_send.pop(0))
        else:
            runner.end_input()

    runner.input_requested.connect(on_input)
    runner.result_ready.connect(lambda result: (results.append(result), loop.quit()))
    QTimer.singleShot(5000, loop.quit)
    script = paths.projects_dir / "main.py"
    script.write_text(code, encoding="utf-8")
    runner.start(
        code=code,
        script_path=script,
        working_directory=paths.projects_dir,
        timeout_seconds=timeout,
        output_limit_bytes=output_limit,
    )
    loop.exec()
    assert results, "运行没有在测试时限内结束"
    return runner, results[0]


def test_worker_runs_normal_code(app_paths) -> None:
    _runner, result = _run(app_paths, 'print("hello")')
    assert result.exit_code == 0
    assert result.stdout == "hello\n"
    assert result.stderr == ""


def test_runner_decodes_chinese_split_across_stdout_chunks(app_paths) -> None:
    _qt_app()
    runner = PythonRunner(app_paths)
    received: list[str] = []
    runner.stdout_ready.connect(received.append)
    payload = (
        json.dumps(
            {"type": "stdout", "text": "欢迎学习 Python\n"},
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )
    split = payload.index("欢".encode("utf-8")) + 1
    runner._consume_stdout_bytes(payload[:split])
    runner._consume_stdout_bytes(payload[split:])
    assert "".join(received) == "欢迎学习 Python\n"


def test_worker_preserves_chinese_output(app_paths) -> None:
    _runner, result = _run(app_paths, 'print("欢迎学习 Python")')
    assert result.stdout == "欢迎学习 Python\n"


def test_worker_supports_input(app_paths) -> None:
    _runner, result = _run(
        app_paths,
        'name = input("名字：")\nprint(f"你好，{name}")',
        inputs=["小明"],
    )
    assert result.exit_code == 0
    assert "名字：" in result.stdout
    assert "你好，小明" in result.stdout


def test_worker_reports_syntax_error(app_paths) -> None:
    _runner, result = _run(app_paths, "print(")
    assert result.exit_code != 0
    assert result.error_type == "SyntaxError"
    assert "SyntaxError" in result.stderr


def test_worker_enforces_timeout(app_paths) -> None:
    _runner, result = _run(app_paths, "while True:\n    pass", timeout=0.2)
    assert result.timed_out is True
    assert result.duration_ms >= 0


def test_worker_limits_large_output(app_paths) -> None:
    _runner, result = _run(
        app_paths,
        "print('x' * 2000)",
        output_limit=128,
    )
    assert result.exit_code == 0
    assert len(result.stdout.encode("utf-8")) <= 128


def test_runner_exposes_persistent_package_directory(app_paths) -> None:
    _qt_app()
    runner = PythonRunner(app_paths)
    environment = runner._environment(app_paths.runs_dir / "test")
    assert str(app_paths.packages_dir) in (
        environment.value("PYTHONPATH") or ""
    )


def test_worker_can_be_cancelled(app_paths) -> None:
    _qt_app()
    runner = PythonRunner(app_paths)
    results = []
    loop = QEventLoop()
    runner.result_ready.connect(lambda result: (results.append(result), loop.quit()))
    script = app_paths.projects_dir / "loop.py"
    code = "while True:\n    pass"
    script.write_text(code, encoding="utf-8")
    runner.start(
        code=code,
        script_path=script,
        working_directory=app_paths.projects_dir,
        timeout_seconds=5,
    )
    QTimer.singleShot(150, runner.stop)
    QTimer.singleShot(5000, loop.quit)
    loop.exec()
    assert results
    assert results[0].cancelled is True


def test_error_explainer_identifies_name_error() -> None:
    explanation = PythonErrorExplainer().explain(
        'Traceback (most recent call last):\n'
        '  File "main.py", line 2, in <module>\n'
        "    print(name)\n"
        "NameError: name 'name' is not defined\n"
    )
    assert explanation is not None
    assert explanation.error_type == "NameError"
    assert explanation.line_number == 2
