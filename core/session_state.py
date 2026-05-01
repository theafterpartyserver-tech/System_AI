import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class SessionStateStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "status": "new",
                "started_at": None,
                "updated_at": None,
                "pending_action": None,
                "last_shutdown_reason": None,
            }

        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "status": "corrupt",
                "started_at": None,
                "updated_at": None,
                "pending_action": None,
                "last_shutdown_reason": "state_file_corrupt",
            }

    def save(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def mark_running(self, pending_action: Optional[Dict[str, Any]] = None) -> None:
        state = self.load()
        if not state.get("started_at"):
            state["started_at"] = datetime.now(timezone.utc).isoformat()
        state["status"] = "running"
        state["pending_action"] = pending_action
        state["last_shutdown_reason"] = None
        self.save(state)

    def set_pending_action(self, pending_action: Optional[Dict[str, Any]]) -> None:
        state = self.load()
        state["status"] = "running"
        state["pending_action"] = pending_action
        self.save(state)

    def mark_clean_exit(self) -> None:
        state = self.load()
        state["status"] = "clean_exit"
        state["pending_action"] = None
        state["last_shutdown_reason"] = "clean_exit"
        self.save(state)

    def mark_interrupted(self) -> None:
        state = self.load()
        state["status"] = "interrupted"
        state["last_shutdown_reason"] = "keyboard_interrupt"
        self.save(state)

    def mark_crash(self, reason: str) -> None:
        state = self.load()
        state["status"] = "crashed"
        state["last_shutdown_reason"] = reason
        self.save(state)
