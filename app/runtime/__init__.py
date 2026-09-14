from __future__ import annotations

import importlib
from typing import Any

from app.runtime.error_explainer import PythonErrorExplanation, PythonErrorExplainer
from app.runtime.run_models import RunRequest, RunResult, RunState

__all__ = [
    "PythonErrorExplanation",
    "PythonErrorExplainer",
    "PythonRunner",
    "RunRequest",
    "RunResult",
    "RunState",
]


def __getattr__(name: str) -> Any:
    if name == "PythonRunner":
        module = importlib.import_module("app.runtime.python_runner")
        return module.PythonRunner
    raise AttributeError(name)
