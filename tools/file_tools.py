from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow project root and arbitrary user files outside it
ALLOWED_ROOTS = [
    PROJECT_ROOT,
]

# Block system-critical paths
_MAIN_SYSTEM_ROOTS = {
    Path("C:/Windows").resolve(),
}


def _is_protected_system_root(path: Path) -> bool:
    resolved = path.resolve()
    for sys_root in _MAIN_SYSTEM_ROOTS:
        if resolved == sys_root or sys_root in resolved.parents:
            return True
    return False


def _resolve_user_path(user_path: str) -> Path:
    raw = Path(user_path)

    if raw.is_absolute():
        candidate = raw.resolve()
    else:
        candidate = (PROJECT_ROOT / raw).resolve()

    # Allow if candidate is inside any allowed root (including project root)
    allowed = False
    for root in ALLOWED_ROOTS:
        resolved_root = root.resolve()
        if candidate == resolved_root or resolved_root in candidate.parents:
            allowed = True
            break

    # Only block if we are *inside* a system root, even if otherwise allowed
    if _is_protected_system_root(candidate):
        raise ValueError(
            f"Path is inside a protected system root: {user_path}"
        )

    return candidate


def file_read(path: str) -> Dict[str, Any]:
    try:
        resolved = _resolve_user_path(path)

        if not resolved.exists():
            return {"status": "error", "error": f"File not found: {path}"}

        if not resolved.is_file():
            return {"status": "error", "error": f"Not a file: {path}"}

        content = resolved.read_text(encoding="utf-8")
        return {
            "status": "ok",
            "path": str(resolved),
            "content": content,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def file_write(path: str, content: str) -> Dict[str, Any]:
    try:
        resolved = _resolve_user_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")

        return {
            "status": "ok",
            "path": str(resolved),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
