from __future__ import annotations

import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QProcess,
    QProcessEnvironment,
    QTimer,
    Signal,
)

from app.config import AppPaths
from app.runtime.run_models import RunRequest, RunResult, RunState


class PythonRunner(QObject):
    started = Signal(str)
    state_changed = Signal(object)
    stdout_ready = Signal(str)
    stderr_ready = Signal(str)
    input_requested = Signal(str)
    result_ready = Signal(object)
    failed = Signal(str)
    truncated = Signal(str)

    def __init__(self, paths: AppPaths, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.paths = paths
        self._process: QProcess | None = None
        self._state = RunState.IDLE
        self._request: RunRequest | None = None
        self._request_dir: Path | None = None
        self._stdout_parts: list[str] = []
        self._stderr_parts: list[str] = []
        self._stdout_buffer = bytearray()
        self._stderr_buffer = ""
        self._result_event: dict[str, object] | None = None
        self._timed_out = False
        self._cancelled = False
        self._started_at_ms = 0
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._force_kill)

    @property
    def state(self) -> RunState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state in {
            RunState.STARTING,
            RunState.RUNNING,
            RunState.WAITING_INPUT,
            RunState.CANCELLING,
        }

    def start(
        self,
        *,
        code: str,
        script_path: str | Path,
        working_directory: str | Path,
        timeout_seconds: float = 5.0,
        output_limit_bytes: int = 1_048_576,
    ) -> str:
        if self.is_running:
            raise RuntimeError("已有 Python 程序正在运行")

        run_id = uuid.uuid4().hex
        request = RunRequest(
            run_id=run_id,
            script_path=str(Path(script_path).resolve()),
            working_directory=str(Path(working_directory).resolve()),
            interpreter_path=sys.executable,
            code=code,
            timeout_seconds=timeout_seconds,
            output_limit_bytes=output_limit_bytes,
        )
        self._request = request
        self._reset_run_buffers()
        request_dir = self.paths.runs_dir / run_id
        request_dir.mkdir(parents=True, exist_ok=True)
        request_path = request_dir / "request.json"
        with request_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "run_id": run_id,
                    "script_path": request.script_path,
                    "working_directory": request.working_directory,
                    "interpreter_path": request.interpreter_path,
                    "code": request.code,
                    "timeout_seconds": request.timeout_seconds,
                    "output_limit_bytes": request.output_limit_bytes,
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
        self._request_dir = request_dir
        self._started_at_ms = int(time.time() * 1000)

        process = QProcess(self)
        process.setProgram(self._worker_program())
        process.setArguments(self._worker_arguments(request_path))
        process.setWorkingDirectory(request.working_directory)
        process.setProcessEnvironment(self._environment(request_dir))
        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.finished.connect(self._process_finished)
        process.errorOccurred.connect(self._process_error)
        self._process = process
        self._set_state(RunState.STARTING)
        self.started.emit(run_id)
        process.start()
        self._timeout_timer.start(max(1, round(request.timeout_seconds * 1000)))
        return run_id

    def submit_input(self, text: str) -> None:
        if self._state not in {RunState.WAITING_INPUT, RunState.RUNNING}:
            raise RuntimeError("当前程序没有等待输入")
        self._write_control({"type": "stdin", "data": text + "\n"})
        self._set_state(RunState.RUNNING)

    def end_input(self) -> None:
        if self._state is not RunState.WAITING_INPUT:
            return
        self._write_control({"type": "eof"})
        self._set_state(RunState.RUNNING)

    def stop(self) -> None:
        if not self.is_running or self._process is None:
            return
        self._cancelled = True
        self._timeout_timer.stop()
        self._set_state(RunState.CANCELLING)
        self._process.terminate()
        self._kill_timer.start(500)

    def _worker_arguments(self, request_path: Path) -> list[str]:
        if getattr(sys, "frozen", False):
            worker_executable = Path(sys.executable).with_name("PythonWorker.exe")
            if worker_executable.exists():
                return [str(request_path)]
            return ["--run-worker", str(request_path)]
        return ["-u", "-m", "app.runtime.worker", str(request_path)]

    def _worker_program(self) -> str:
        if getattr(sys, "frozen", False):
            worker_executable = Path(sys.executable).with_name("PythonWorker.exe")
            if worker_executable.exists():
                return str(worker_executable)
        return sys.executable

    def _environment(self, request_dir: Path) -> QProcessEnvironment:
        environment = QProcessEnvironment()
        allowed = {
            "ALLUSERSPROFILE",
            "APPDATA",
            "COMSPEC",
            "COMMONPROGRAMFILES",
            "COMMONPROGRAMFILES(X86)",
            "HOME",
            "HOMEDRIVE",
            "HOMEPATH",
            "LOCALAPPDATA",
            "NUMBER_OF_PROCESSORS",
            "OS",
            "PATH",
            "PATHEXT",
            "PROCESSOR_ARCHITECTURE",
            "PROCESSOR_IDENTIFIER",
            "PROGRAMDATA",
            "PROGRAMFILES",
            "PROGRAMFILES(X86)",
            "SYSTEMDRIVE",
            "SYSTEMROOT",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "WINDIR",
        }
        for key, value in os.environ.items():
            if key.upper() in allowed:
                environment.insert(key, value)
        environment.insert("PYTHONIOENCODING", "utf-8")
        environment.insert("PYTHONUTF8", "1")
        environment.insert("PYTHONUNBUFFERED", "1")
        environment.insert("PYTHONNOUSERSITE", "1")
        environment.insert("PYTHONLEGACYWINDOWSSTDIO", "0")
        environment.insert("PYTHONLEARN_RUN_DIR", str(request_dir))
        python_path = str(self.paths.packages_dir)
        existing_path = environment.value("PYTHONPATH")
        if existing_path:
            python_path += os.pathsep + existing_path
        environment.insert("PYTHONPATH", python_path)
        if not getattr(sys, "frozen", False):
            environment.insert(
                "PYTHONPATH",
                python_path + os.pathsep + str(self.paths.project_root),
            )
        return environment

    def _read_stdout(self) -> None:
        if self._process is None:
            return
        self._consume_stdout_bytes(bytes(self._process.readAllStandardOutput()))

    def _consume_stdout_bytes(self, data: bytes) -> None:
        if not data:
            return
        self._stdout_buffer.extend(data)
        while b"\n" in self._stdout_buffer:
            line, _, remainder = self._stdout_buffer.partition(b"\n")
            self._stdout_buffer = bytearray(remainder)
            self._handle_event_line(line.decode("utf-8", errors="replace"))

    def _read_stderr(self) -> None:
        if self._process is None:
            return
        text = bytes(self._process.readAllStandardError()).decode(
            "utf-8", errors="replace"
        )
        if text:
            self.stderr_ready.emit(text)
            self._stderr_parts.append(text)

    def _handle_event_line(self, line: str) -> None:
        if not line.strip():
            return
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            self.stdout_ready.emit(line + "\n")
            self._stdout_parts.append(line + "\n")
            return
        event_type = event.get("type")
        if event_type == "stdout":
            text = str(event.get("text", ""))
            self.stdout_ready.emit(text)
            self._stdout_parts.append(text)
        elif event_type == "stderr":
            text = str(event.get("text", ""))
            self.stderr_ready.emit(text)
            self._stderr_parts.append(text)
        elif event_type == "input_request":
            self._set_state(RunState.WAITING_INPUT)
            self.input_requested.emit(str(event.get("prompt", "")))
        elif event_type == "truncated":
            self.truncated.emit(str(event.get("stream", "output")))
        elif event_type == "finished":
            self._result_event = event
        else:
            self.stderr_ready.emit(f"未知 Worker 事件：{line}\n")

    def _write_control(self, payload: dict[str, object]) -> None:
        if self._process is None:
            raise RuntimeError("Worker 未启动")
        data = (
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        self._process.write(data)

    def _process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus,
    ) -> None:
        self._read_stdout()
        self._read_stderr()
        if self._stdout_buffer.strip():
            self._handle_event_line(
                self._stdout_buffer.decode("utf-8", errors="replace")
            )
        self._stdout_buffer = bytearray()
        self._stderr_buffer = ""
        self._timeout_timer.stop()
        self._kill_timer.stop()

        if self._timed_out:
            state = RunState.TIMEOUT
        elif self._cancelled:
            state = RunState.CANCELLED
        elif self._result_event is not None:
            state = RunState.FINISHED
        elif exit_code == 0:
            state = RunState.FINISHED
        else:
            state = RunState.FAILED

        event = self._result_event or {}
        result_exit_code = event.get("exit_code")
        if not isinstance(result_exit_code, int):
            result_exit_code = exit_code
        result = RunResult(
            run_id=self._request.run_id if self._request else "",
            exit_code=result_exit_code,
            stdout="".join(self._stdout_parts),
            stderr="".join(self._stderr_parts),
            duration_ms=int(event.get("duration_ms", 0)),
            timed_out=self._timed_out,
            cancelled=self._cancelled,
            error_type=(
                str(event["error_type"]) if event.get("error_type") is not None else None
            ),
            started_at=self._started_at_ms,
        )
        self._set_state(state)
        self.result_ready.emit(result)
        self._cleanup()

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.FailedToStart:
            message = "无法启动 Python Worker。"
            if self._process is not None:
                message += f" {self._process.errorString()}"
            self._timeout_timer.stop()
            self._kill_timer.stop()
            self._set_state(RunState.FAILED)
            self.failed.emit(message)
            self._cleanup()

    def _on_timeout(self) -> None:
        if not self.is_running or self._process is None:
            return
        self._timed_out = True
        self._set_state(RunState.CANCELLING)
        self._process.terminate()
        self._kill_timer.start(500)

    def _force_kill(self) -> None:
        if self._process is not None and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()

    def _set_state(self, state: RunState) -> None:
        if self._state == state:
            return
        self._state = state
        self.state_changed.emit(state)

    def _reset_run_buffers(self) -> None:
        self._stdout_parts = []
        self._stderr_parts = []
        self._stdout_buffer = bytearray()
        self._stderr_buffer = ""
        self._result_event = None
        self._timed_out = False
        self._cancelled = False

    def _cleanup(self) -> None:
        process = self._process
        self._process = None
        if process is not None:
            process.deleteLater()
        request_dir = self._request_dir
        self._request_dir = None
        self._request = None
        self._set_state(RunState.IDLE)
        if request_dir is not None:
            QTimer.singleShot(
                0,
                lambda path=request_dir: shutil.rmtree(path, ignore_errors=True),
            )
