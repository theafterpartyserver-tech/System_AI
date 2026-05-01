import json
from typing import Dict, Any, Callable, List

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._load_builtin_tools()

    def _load_builtin_tools(self) -> None:
        # This is the list the LLM will see
        builtin_tool_data = [
            {
                "name": "file_read",
                "description": "Read the contents of a file.",
                "permission_tier": "safe",
                "args": {"path": "string"},
            },
            {
                "name": "file_write",
                "description": "Write content to a file.",
                "permission_tier": "elevated",
                "args": {"path": "string", "content": "string"},
            },
            {
                "name": "shell_exec",
                "description": "Run a shell command.",
                "permission_tier": "dangerous",
                "args": {"command": "string"},
            },
        ]
        for tool in builtin_tool_data:
            self._tools[tool["name"]] = {
                "metadata": tool,
                "function": None  # filled by set_tool later
            }

    def get_injectable_context(self) -> List[Dict[str, Any]]:
        return [self._tools[name]["metadata"] for name in sorted(self._tools.keys())]

    def set_tool(self, name: str, function: Callable) -> None:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not defined in registry.")
        self._tools[name]["function"] = function

    def get_tool(self, name: str) -> Dict[str, Any] | None:
        return self._tools.get(name)

    def list_tool_names(self) -> List[str]:
        return list(self._tools.keys())
