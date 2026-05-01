"""
Advanced Discovery Engine
Auto-discovers tools and skills from files, reads metadata, and generates manifests.
Supports Python modules, external programs, and skill definitions.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class DiscoveryEngine:
    """Discovers and catalogs tools and skills from the filesystem."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.tools_dir = self.project_root / "tools"
        self.skills_dir = self.project_root / "skills"
        self.external_skills_dir = self.project_root / "external_skills"
        self.discoveries = {
            "tools": [],
            "skills": [],
            "programs": [],
            "metadata": {
                "discovered_at": datetime.now().isoformat(),
                "total_discovered": 0
            }
        }
    
    def discover_all(self) -> Dict[str, Any]:
        """Run complete discovery across all sources."""
        self.discover_python_tools()
        self.discover_python_skills()
        self.discover_external_programs()
        self.discover_skill_definitions()
        return self.discoveries
    
    def discover_python_tools(self) -> List[Dict[str, Any]]:
        """Discover tools from Python modules in tools/ directory."""
        tools = []
        
        if not self.tools_dir.exists():
            return tools
        
        for py_file in self.tools_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                tool_info = self._extract_python_metadata(py_file, "tool")
                tools.append(tool_info)
            except Exception as e:
                print(f"Error discovering {py_file.name}: {e}")
        
        self.discoveries["tools"] = tools
        return tools
    
    def discover_python_skills(self) -> List[Dict[str, Any]]:
        """Discover skills from Python modules in skills/ directory."""
        skills = []
        
        if not self.skills_dir.exists():
            return skills
        
        for py_file in self.skills_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                skill_info = self._extract_python_metadata(py_file, "skill")
                skills.append(skill_info)
            except Exception as e:
                print(f"Error discovering {py_file.name}: {e}")
        
        self.discoveries["skills"] = skills
        return skills
    
    def discover_external_programs(self) -> List[Dict[str, Any]]:
        """Discover external executable programs."""
        programs = []
        
        # Windows executables
        exe_extensions = [".exe", ".bat", ".cmd", ".ps1"]
        for ext in exe_extensions:
            for program in self.project_root.rglob(f"*{ext}"):
                if any(skip in program.parts for skip in [".venv", "__pycache__", ".git"]):
                    continue
                programs.append({
                    "name": program.stem,
                    "type": "executable",
                    "path": str(program),
                    "executable": True
                })
        
        self.discoveries["programs"] = programs
        return programs
    
    def discover_skill_definitions(self) -> List[Dict[str, Any]]:
        """Discover skill definitions from markdown/JSON files."""
        skill_defs = []
        
        if not self.external_skills_dir.exists():
            return skill_defs
        
        for md_file in self.external_skills_dir.glob("*.md"):
            try:
                skill_def = self._extract_markdown_skill(md_file)
                skill_defs.append(skill_def)
            except Exception as e:
                print(f"Error reading {md_file.name}: {e}")
        
        for json_file in self.external_skills_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    skill_def = json.load(f)
                    skill_def["source"] = str(json_file)
                    skill_defs.append(skill_def)
            except Exception as e:
                print(f"Error reading {json_file.name}: {e}")
        
        return skill_defs
    
    def _extract_python_metadata(self, py_file: Path, item_type: str) -> Dict[str, Any]:
        """Extract metadata from Python module."""
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract docstring
        docstring = ""
        doc_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if not doc_match:
            doc_match = re.search(r"'''(.+?)'''", content, re.DOTALL)
        if doc_match:
            docstring = doc_match.group(1).strip()
        
        # Extract function definitions
        functions = re.findall(r"def\s+(\w+)\s*\([^)]*\):", content)
        classes = re.findall(r"class\s+(\w+)[\(:]", content)
        
        return {
            "name": py_file.stem,
            "type": item_type,
            "file": str(py_file),
            "docstring": docstring[:200] if docstring else "No description",
            "functions": functions,
            "classes": classes,
            "source_type": "python"
        }
    
    def _extract_markdown_skill(self, md_file: Path) -> Dict[str, Any]:
        """Extract skill definition from markdown file."""
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract title (first H1)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # Extract description (first paragraph)
        desc_match = re.search(r"^[^#\n]+\n*(.+?)(?:\n##|\Z)", content, re.DOTALL)
        description = desc_match.group(1).strip()[:300] if desc_match else ""
        
        return {
            "name": md_file.stem,
            "type": "skill_definition",
            "file": str(md_file),
            "title": title,
            "description": description,
            "source_type": "markdown"
        }
    
    def export_manifest(self, output_path: Optional[Path] = None) -> str:
        """Export discovered items as manifest JSON."""
        manifest = {
            "version": "2.0.0",
            "generated": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "discovery": self.discoveries
        }
        
        if output_path:
            with open(output_path, "w") as f:
                json.dump(manifest, f, indent=2)
        
        return json.dumps(manifest, indent=2)
    
    def generate_summary(self) -> str:
        """Generate human-readable discovery summary."""
        summary = []
        summary.append("=" * 70)
        summary.append("DISCOVERY ENGINE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"Tools found: {len(self.discoveries.get('tools', []))}")
        summary.append(f"Skills found: {len(self.discoveries.get('skills', []))}")
        summary.append(f"Programs found: {len(self.discoveries.get('programs', []))}")
        summary.append("")
        
        if self.discoveries["tools"]:
            summary.append("TOOLS:")
            for tool in self.discoveries["tools"]:
                summary.append(f"  - {tool['name']}: {tool['docstring'][:50]}")
        
        if self.discoveries["skills"]:
            summary.append("\nSKILLS:")
            for skill in self.discoveries["skills"]:
                summary.append(f"  - {skill['name']}: {skill.get('docstring', 'No description')[:50]}")
        
        summary.append("=" * 70)
        return "\n".join(summary)
