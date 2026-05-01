import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def _is_blocked_command(parts: List[str]) -> tuple[bool, str]:
    blocked = {
        "del",
        "erase",
        "format",
        "shutdown",
        "reboot",
        "poweroff",
    }

    if not parts:
        return True, "empty_command"

    cmd = parts[0].lower()
    if cmd in blocked:
        return True, f"blocked_command: {cmd}"

    return False, "ok"


def shell_exec(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    parts = shlex.split(command)

    is_blocked, reason = _is_blocked_command(parts)
    if is_blocked:
        return {
            "status": "error",
            "command": command,
            "error": reason,
        }

    try:
        completed = subprocess.run(
            parts,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=False,
            timeout=10,
        )
        return {
            "status": "ok" if completed.returncode == 0 else "error",
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "command": command,
            "error": "timeout",
        }
    except Exception as e:
        return {
            "status": "error",
            "command": command,
            "error": str(e),
        }