import json
from pathlib import Path
from typing import Dict, Any

from core.health_manager import get_routing_bias


class Gateway:
    def __init__(self, permissions_path: Path):
        self.permissions_path = permissions_path
        self._permissions: Dict[str, Any] = {}
        self.load_permissions()

    def load_permissions(self) -> None:
        try:
            with open(self.permissions_path, "r", encoding="utf-8") as f:
                self._permissions = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Permissions config not found: {self.permissions_path}"
            )

    def check_tool(self, tool_name: str, user_mode: str = "user") -> Dict[str, Any]:
        blocked_tools = self._permissions.get("blocked_tools", [])
        if tool_name in blocked_tools:
            return {"decision": "DENY", "reason": "Tool is blocked"}

        tiers = self._permissions.get("tool_tiers", {})
        tier = tiers.get(tool_name, "safe")

        is_dangerous = tier == "dangerous"
        is_elevated = tier == "elevated"

        bias = get_routing_bias()

        if is_dangerous:
            return {"decision": "CONFIRM", "reason": "Dangerous tool"}

        if is_elevated and user_mode == "user":
            if bias == "conservative":
                return {
                    "decision": "CONFIRM",
                    "reason": "Elevated tool in user mode, conservative bias"
                }
            return {"decision": "CONFIRM", "reason": "Elevated tool in user mode"}

        return {"decision": "SAFE", "reason": "Allowed"}
