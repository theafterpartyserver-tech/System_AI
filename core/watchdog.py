from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
import time


@dataclass
class WatchdogResult:
    ok: bool
    message: str = ""
    details: Dict[str, Any] = None
    timestamp: float = 0.0


class Watchdog:
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self._last_beat = time.time()

    def beat(self) -> None:
        self._last_beat = time.time()

    def is_stale(self) -> bool:
        return (time.time() - self._last_beat) > self.timeout_seconds

    def check(self) -> WatchdogResult:
        if self.is_stale():
            return WatchdogResult(
                ok=False,
                message="Watchdog timeout exceeded.",
                details={"timeout_seconds": self.timeout_seconds},
                timestamp=time.time(),
            )
        return WatchdogResult(
            ok=True,
            message="Watchdog healthy.",
            details={"timeout_seconds": self.timeout_seconds},
            timestamp=time.time(),
        )

    def run_with_timeout(
        self,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self.beat()
        return fn(*args, **kwargs)
