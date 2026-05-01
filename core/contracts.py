from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class ToolSpec:
    name: str
    description: str
    module: str
    function: str
    risk: str = "safe"
    enabled: bool = True
    args_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillSpec:
    name: str
    description: str
    path: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegisteredTool:
    spec: ToolSpec
    handler: Callable[..., Any]
