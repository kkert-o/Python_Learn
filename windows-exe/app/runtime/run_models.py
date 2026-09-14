from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class RunState(StrEnum):
    IDLE = "IDLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    WAITING_INPUT = "WAITING_INPUT"
    CANCELLING = "CANCELLING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


@dataclass(frozen=True, slots=True)
class RunRequest:
    run_id: str
    script_path: str
    working_directory: str
    interpreter_path: str
    code: str
    timeout_seconds: float = 5.0
    output_limit_bytes: int = 1_048_576
    environment: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool
    cancelled: bool
    error_type: str | None
    started_at: int

