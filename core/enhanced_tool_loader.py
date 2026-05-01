"""
Enhanced Tool Loader - Dynamically loads and registers tools from tool modules
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Callable

class EnhancedToolLoader:
    """Load tools from Python modules and register them"""
    
    def __init__(self, tools_dir: Path = None):
        self.tools_dir = tools_dir or Path('./tools')
        self.tools = {}
    
    def load_all_tools(self) -> Dict[str, Callable]:
        """Dynamically load all tools from tools directory"""
        if not self.tools_dir.exists():
            return {}
        
        for tool_file in self.tools_dir.glob('*.py'):
            if tool_file.name.startswith('_'):
                continue
            
            try:
                self.load_tool_module(tool_file)
            except Exception as e:
                print(f"Error loading {tool_file.name}: {e}")
        
        return self.tools
    
    def load_tool_module(self, tool_file: Path):
        """Load a single tool module"""
        module_name = tool_file.stem
        spec = importlib.util.spec_from_file_location(module_name, tool_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Extract functions from module
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith('_'):
                self.tools[f"{module_name}_{name}"] = obj
    
    def get_tool(self, tool_name: str) -> Callable:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> list:
        """List all loaded tools"""
        return list(self.tools.keys())

    def load_skill_modules(self, skills_dir: Path = None) -> Dict[str, Any]:
        """Load skill modules and extract metadata"""
        skills_dir = skills_dir or Path('./skills')
        skills = {}
        
        if not skills_dir.exists():
            return skills
        
        for skill_file in skills_dir.glob('*.py'):
            if skill_file.name.startswith('_'):
                continue
            
            try:
                module_name = skill_file.stem
                spec = importlib.util.spec_from_file_location(module_name, skill_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get metadata if available
                metadata = getattr(module, 'SKILL_METADATA', {})
                functions = [name for name, obj in inspect.getmembers(module, inspect.isfunction)
                           if not name.startswith('_')]
                
                skills[module_name] = {
                    "metadata": metadata,
                    "functions": functions,
                    "module": module
                }
            except Exception as e:
                print(f"Error loading skill {skill_file.name}: {e}")
        
        return skills
