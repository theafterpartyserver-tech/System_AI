from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import time


class RecoveryStatus(str, Enum):
    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    CRASHED = "crashed"
    UNKNOWN = "unknown"


@dataclass
class RecoveryEvent:
    name: str
    status: RecoveryStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class SessionSnapshot:
    session_id: str
    last_user_input: Optional[str] = None
    last_router_result: Optional[Dict[str, Any]] = None
    last_tool_result: Optional[Dict[str, Any]] = None
    memory_state: Optional[Dict[str, Any]] = None
    health_state: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)


class RecoveryManager:
    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = Path(state_dir) if state_dir else None
        self._events: List[RecoveryEvent] = []
        self._last_snapshot: Optional[SessionSnapshot] = None
        self._watchdog_enabled: bool = True

    def record_event(
        self,
        name: str,
        status: RecoveryStatus,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> RecoveryEvent:
        event = RecoveryEvent(
            name=name,
            status=status,
            message=message,
            details=details or {},
        )
        self._events.append(event)
        return event

    def create_snapshot(
        self,
        session_id: str,
        last_user_input: Optional[str] = None,
        last_router_result: Optional[Dict[str, Any]] = None,
        last_tool_result: Optional[Dict[str, Any]] = None,
        memory_state: Optional[Dict[str, Any]] = None,
        health_state: Optional[Dict[str, Any]] = None,
    ) -> SessionSnapshot:
        snapshot = SessionSnapshot(
            session_id=session_id,
            last_user_input=last_user_input,
            last_router_result=last_router_result,
            last_tool_result=last_tool_result,
            memory_state=memory_state,
            health_state=health_state,
        )
        self._last_snapshot = snapshot
        return snapshot

    def load_last_snapshot(self) -> Optional[SessionSnapshot]:
        return self._last_snapshot

    def restore_session(self) -> Dict[str, Any]:
        if self._last_snapshot is None:
            return {
                "status": RecoveryStatus.UNKNOWN.value,
                "message": "No snapshot available for recovery.",
            }

        return {
            "status": RecoveryStatus.OK.value,
            "session_id": self._last_snapshot.session_id,
            "message": "Session restored from snapshot.",
        }

    def build_recovery_prompt(self, reason: str) -> str:
        snapshot = self._last_snapshot
        parts = [f"Recovery prompt reason: {reason}"]
        if snapshot:
            parts.append(f"Last user input: {snapshot.last_user_input}")
            parts.append(f"Last router result: {snapshot.last_router_result}")
        return "\n".join(parts)

    def log_resume(self, reason: str, details: Optional[Dict[str, Any]] = None) -> RecoveryEvent:
        return self.record_event(
            name="session_resume",
            status=RecoveryStatus.OK,
            message=reason,
            details=details or {},
        )

    def log_crash(self, reason: str, details: Optional[Dict[str, Any]] = None) -> RecoveryEvent:
        return self.record_event(
            name="session_crash",
            status=RecoveryStatus.CRASHED,
            message=reason,
            details=details or {},
        )

    def log_interrupt(self, reason: str, details: Optional[Dict[str, Any]] = None) -> RecoveryEvent:
        return self.record_event(
            name="session_interrupt",
            status=RecoveryStatus.INTERRUPTED,
            message=reason,
            details=details or {},
        )

    def enable_watchdog(self) -> None:
        self._watchdog_enabled = True

    def disable_watchdog(self) -> None:
        self._watchdog_enabled = False

    def watchdog_enabled(self) -> bool:
        return self._watchdog_enabled

    def get_events(self) -> List[RecoveryEvent]:
        return list(self._events)
