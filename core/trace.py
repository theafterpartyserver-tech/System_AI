import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


LOG_PATH = Path("logs") / "events.log"


def trace_event(phase: str, metadata: Optional[Dict[str, Any]] = None, *,
                input_data: Any = None, output_data: Any = None) -> Dict[str, Any]:
    return {"timestamp": time.time(), "phase": phase,
            "input": input_data, "output": output_data, "metadata": metadata or {}}


def log_event(event: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def log_performance(phase: str, start_time: float,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
    duration = time.time() - start_time
    log_event({"timestamp": time.time(), "phase": phase,
               "duration_ms": round(duration * 1000, 2), "metadata": metadata or {}})


# ── LatencyLogger (merged from core/latency_logger.py) ───────────────────────

@dataclass
class LatencyEntry:
    name: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class LatencyLogger:
    def __init__(self):
        self._entries: List[LatencyEntry] = []

    def log(self, name: str, duration_ms: float,
            details: Optional[Dict[str, Any]] = None) -> LatencyEntry:
        entry = LatencyEntry(name=name, duration_ms=duration_ms, details=details or {})
        self._entries.append(entry)
        return entry

    def all(self) -> List[LatencyEntry]:
        return list(self._entries)
