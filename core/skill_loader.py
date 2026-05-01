from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.contracts import SkillSpec


def _parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text

    metadata: Dict[str, str] = {}
    end_idx: Optional[int] = None

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
        if ":" in lines[i]:
            key, value = lines[i].split(":", 1)
            metadata[key.strip()] = value.strip()

    if end_idx is None:
        return {}, text

    body = "\n".join(lines[end_idx + 1:]).strip()
    return metadata, body


class SkillLoader:
    def __init__(self, skill_dirs: List[Path]):
        self.skill_dirs = [p.resolve() for p in skill_dirs]

    def _is_within_allowed_roots(self, path: Path) -> bool:
        resolved = path.resolve()
        for root in self.skill_dirs:
            if resolved == root or root in resolved.parents:
                return True
        return False

    def discover(self) -> List[SkillSpec]:
        skills: List[SkillSpec] = []
        seen_names: Dict[str, str] = {}

        for root in self.skill_dirs:
            if not root.exists() or not root.is_dir():
                continue

            for path in sorted(root.rglob("*.md")):
                if path.name.startswith("_"):
                    continue

                resolved = path.resolve()
                if not self._is_within_allowed_roots(resolved):
                    continue

                text = resolved.read_text(encoding="utf-8")
                metadata, body = _parse_frontmatter(text)

                name = metadata.get("name") or resolved.stem
                description = metadata.get("description") or f"Skill loaded from {resolved}"

                if name in seen_names:
                    raise ValueError(
                        f"Duplicate skill name '{name}' found in '{resolved}' and '{seen_names[name]}'"
                    )

                seen_names[name] = str(resolved)
                skills.append(
                    SkillSpec(
                        name=name,
                        description=description,
                        path=str(resolved),
                        body=body,
                        metadata=metadata,
                    )
                )

        return skills
