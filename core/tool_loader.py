import importlib
import json
from pathlib import Path
from typing import List

from core.contracts import RegisteredTool, ToolSpec


class ToolLoader:
    def __init__(self, manifest_path: Path):
        self.manifest_path = Path(manifest_path).resolve()

    def load(self) -> List[RegisteredTool]:
        if not self.manifest_path.exists():
            return []

        raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        tool_defs = raw.get("tools", [])
        registered: List[RegisteredTool] = []

        for item in tool_defs:
            spec = ToolSpec(**item)
            if not spec.enabled:
                continue

            module = importlib.import_module(spec.module)
            handler = getattr(module, spec.function)
            registered.append(RegisteredTool(spec=spec, handler=handler))

        return registered
