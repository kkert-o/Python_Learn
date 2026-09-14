from __future__ import annotations

import builtins
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any


class _ControlWriter:
    def __init__(
        self,
        control_stream: "_EventStream",
        event_type: str,
        output_limit: int,
    ) -> None:
        self.control_stream = control_stream
        self.event_type = event_type
        self.output_limit = output_limit
        self.bytes_written = 0
        self.truncated = False
        self.encoding = "utf-8"

    def write(self, text: str) -> int:
        if not text:
            return 0
        encoded = text.encode(self.encoding, errors="replace")
        if self.bytes_written >= self.output_limit:
            self._emit_truncated()
            return len(text)
        remaining = self.output_limit - self.bytes_written
        accepted = encoded[:remaining]
        self.bytes_written += len(accepted)
        decoded = accepted.decode(self.encoding, errors="replace")
        if decoded:
            self._emit({"type": self.event_type, "text": decoded})
        if len(accepted) < len(encoded):
            self._emit_truncated()
        return len(text)

    def flush(self) -> None:
        return None

    def isatty(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def _emit_truncated(self) -> None:
        if not self.truncated:
            self.truncated = True
            self._emit({"type": "truncated", "stream": self.event_type})

    def _emit(self, event: dict[str, Any]) -> None:
        self.control_stream.emit(event)


class _EventStream:
    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.buffer = getattr(stream, "buffer", None)

    def emit(self, event: dict[str, Any]) -> None:
        line = (
            json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        if self.buffer is not None:
            self.buffer.write(line.encode("utf-8"))
            self.buffer.flush()
            return
        self.stream.write(line)
        self.stream.flush()


def _emit(control_stream: _EventStream, event: dict[str, Any]) -> None:
    control_stream.emit(event)


def _pump_remaining() -> None:
    return None


def _read_input(
    *,
    prompt: str,
    control_input: Any,
    control_stream: _EventStream,
    stdout: _ControlWriter,
) -> str:
    if prompt:
        stdout.write(str(prompt))
    _emit(control_stream, {"type": "input_request", "prompt": str(prompt)})
    line = control_input.readline()
    if line == "":
        raise EOFError("没有更多输入")
    try:
        event = json.loads(line)
    except json.JSONDecodeError as exc:
        raise EOFError("输入通道收到无效数据") from exc
    if event.get("type") == "eof":
        raise EOFError("用户结束了输入")
    if event.get("type") != "stdin":
        raise EOFError("输入通道状态错误")
    return str(event.get("data", "")).rstrip("\r\n")


def run_request(request: dict[str, Any]) -> int:
    control_stream = _EventStream(sys.stdout)
    control_input = sys.stdin
    output_limit = int(request.get("output_limit_bytes", 1_048_576))
    stdout = _ControlWriter(control_stream, "stdout", output_limit)
    stderr = _ControlWriter(control_stream, "stderr", output_limit)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_input = builtins.input
    started = time.perf_counter()
    exit_code = 0
    error_type: str | None = None

    def input_override(prompt: object = "") -> str:
        return _read_input(
            prompt=str(prompt),
            control_input=control_input,
            control_stream=control_stream,
            stdout=stdout,
        )

    try:
        sys.stdout = stdout
        sys.stderr = stderr
        builtins.input = input_override
        code = str(request.get("code", ""))
        script_path = str(request.get("script_path", "<string>"))
        compiled = compile(code, script_path, "exec")
        namespace = {
            "__name__": "__main__",
            "__file__": script_path,
            "__package__": None,
            "__builtins__": builtins,
        }
        exec(compiled, namespace, namespace)
    except SystemExit as exc:
        code_value = exc.code
        if code_value is None:
            exit_code = 0
        elif isinstance(code_value, int):
            exit_code = code_value
        else:
            stderr.write(str(code_value))
            exit_code = 1
    except BaseException as exc:
        error_type = type(exc).__name__
        exit_code = 130 if isinstance(exc, KeyboardInterrupt) else 1
        stderr.write("".join(traceback.format_exception(exc)))
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        builtins.input = original_input

    duration_ms = round((time.perf_counter() - started) * 1000)
    _emit(
        control_stream,
        {
            "type": "finished",
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "error_type": error_type,
        },
    )
    return 0


def run_worker_file(request_path: str | Path) -> int:
    path = Path(request_path)
    control_stream = _EventStream(sys.stdout)
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            request = json.load(handle)
        if not isinstance(request, dict):
            raise ValueError("运行请求必须是 JSON 对象")
        return run_request(request)
    except BaseException as exc:
        _emit(
            control_stream,
            {
                "type": "finished",
                "exit_code": 2,
                "duration_ms": 0,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        )
        return 2


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--pip-install":
        from pip._internal.cli.main import main as pip_main

        result = pip_main(args[1:])
        return int(result or 0)
    if len(args) != 1:
        return 2
    return run_worker_file(args[0])


if __name__ == "__main__":
    raise SystemExit(main())
