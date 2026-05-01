from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import time


@dataclass
class TimeoutResult:
    ok: bool
    message: str = ""
    value: Any = None
    elapsed_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class TimeoutManager:
    def __init__(self, timeout_seconds: float = 20.0):
        self.timeout_seconds = timeout_seconds

    def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> TimeoutResult:
        start = time.time()
        try:
            value = fn(*args, **kwargs)
            elapsed_ms = (time.time() - start) * 1000.0
            return TimeoutResult(
                ok=True,
                message="Completed within timeout.",
                value=value,
                elapsed_ms=elapsed_ms,
            )
        except TimeoutError:
            elapsed_ms = (time.time() - start) * 1000.0
            return TimeoutResult(
                ok=False,
                message="Timed out.",
                elapsed_ms=elapsed_ms,
            )
