from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Callable

from core.tool_loader import ToolLoader
from core.skill_loader import SkillLoader


PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class ToolSpec:
    name: str
    description: str
    risk: str
    function: Callable
    schema: dict

    def __init__(self, name: str, description: str, risk: str, function: Callable, schema: dict):
        self.name = name
        self.description = description
        self.risk = risk
        self.function = function
        self.schema = schema


class HybridRegistry:
    """Registry that combines tools and skills in one injectable context."""

    def __init__(
        self,
        project_root: Path = PROJECT_ROOT,
        extra_skill_dirs: Optional[List[Path]] = None,
        tools_manifest_path: Optional[Path] = None,
    ):
        self.project_root = project_root
        self.extra_skill_dirs = extra_skill_dirs or []
        self.tools_manifest_path = tools_manifest_path or (project_root / "tools" / "tools_manifest.json")

        self._tools: Dict[str, ToolSpec] = {}
        self._skills: Dict[str, Any] = {}
        
        # Lazy load on first access
        self._tools_loaded = False
        self._skills_loaded = False

    def register_tool(
        self, name: str, description: str, risk: str, schema: dict, function: Callable
    ) -> None:
        self._tools[name] = ToolSpec(name=name, description=description, risk=risk, schema=schema, function=function)

    def get_tool(self, name: str) -> Optional[ToolSpec]:
        self._ensure_tools_loaded()
        return self._tools.get(name)

    def get_injectable_context(self) -> List[Dict[str, Any]]:
        """Return tools as a list of dicts for prompt injection."""
        self._ensure_tools_loaded()
        return [
            {
                "name": t.name,
                "description": t.description,
                "risk": t.risk,
                "schema": t.schema,
            }
            for t in self._tools.values()
        ]

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        tool = self.get_tool(tool_name)
        if tool is None:
            raise ValueError(f"Unknown tool: {tool_name}")
        return tool.function(**kwargs)

    def list_tool_names(self) -> List[str]:
        self._ensure_tools_loaded()
        return list(self._tools.keys())

    def list_skill_names(self) -> List[str]:
        self._ensure_skills_loaded()
        return list(self._skills.keys())

    def get_skill(self, name: str) -> Optional[Any]:
        self._ensure_skills_loaded()
        return self._skills.get(name)

    def refresh(self) -> None:
        """Reload tools and skills from disk."""
        self._tools_loaded = False
        self._skills_loaded = False
        self._load_tools()
        self._load_skills()

    def _ensure_tools_loaded(self) -> None:
        if not self._tools_loaded:
            self._load_tools()

    def _ensure_skills_loaded(self) -> None:
        if not self._skills_loaded:
            self._load_skills()

    def _load_tools(self) -> None:
        """Load tools from manifest file dynamically."""
        try:
            if not self._tools.keys():  # Only load if not already loaded
                loader = ToolLoader(self.tools_manifest_path)
                registered_tools = loader.load()
                
                for registered in registered_tools:
                    spec = registered.spec
                    self.register_tool(
                        name=spec.name,
                        description=spec.description,
                        risk=spec.risk,
                        schema=spec.args_schema,
                        function=registered.handler,
                    )
            self._tools_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load tools: {e}")
            self._tools_loaded = True

    def _load_skills(self) -> None:
        """Load skills from skill directories dynamically."""
        try:
            skill_dirs = [self.project_root / "skills"] + self.extra_skill_dirs
            skill_dirs = [d for d in skill_dirs if d.exists()]
            
            if skill_dirs:
                loader = SkillLoader(skill_dirs)
                skills = loader.discover()
                
                for skill in skills:
                    self._skills[skill.name] = skill
            
            self._skills_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load skills: {e}")
            self._skills_loaded = True
