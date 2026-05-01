from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


@dataclass
class ResumeLogEntry:
    event: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SessionResumeLog:
    def __init__(self):
        self._entries: List[ResumeLogEntry] = []

    def add(self, event: str, message: str, details: Optional[Dict[str, Any]] = None) -> ResumeLogEntry:
        entry = ResumeLogEntry(
            event=event,
            message=message,
            details=details or {},
        )
        self._entries.append(entry)
        return entry

    def all(self) -> List[ResumeLogEntry]:
        return list(self._entries)
