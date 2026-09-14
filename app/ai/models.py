from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiReply:
    content: str
    source: str
    error: str | None = None

