from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _safe_json(path: Path) -> tuple[bool, Any | None, str | None]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return False, None, "missing"
    except json.JSONDecodeError as e:
        return False, None, f"invalid_json: {e.msg}"
    except Exception as e:
        return False, None, str(e)


def _tail_lines(path: Path, limit: int = 5) -> List[str]:
    if not path.exists() or not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-limit:]


def run_system_diagnostics(project_root: str | Path) -> Dict[str, Any]:
    root = Path(project_root).resolve()

    config_ok, config, config_err = _safe_json(root / "config" / "config.json")
    perms_ok, perms, perms_err = _safe_json(root / "config" / "permissions.json")
    sandbox_ok, sandbox, sandbox_err = _safe_json(root / "config" / "sandbox.json")
    manifest_ok, manifest, manifest_err = _safe_json(root / "tools" / "tools_manifest.json")
    session_ok, session, session_err = _safe_json(root / "runtime" / "session_state.json")
    state_ok, state, state_err = _safe_json(root / "memory" / "state.json")

    backend = config.get("model_backend") if isinstance(config, dict) else None
    model_rel = config.get("local_model_path") if isinstance(config, dict) else None
    model_path = (root / model_rel).resolve() if model_rel else None

    tools = manifest.get("tools", []) if isinstance(manifest, dict) else []
    skills = sorted([p.name for p in (root / "skills").glob("*.md")]) if (root / "skills").exists() else []
    external_skills = sorted([p.name for p in (root / "external_skills").glob("*.md")]) if (root / "external_skills").exists() else []

    log_path = root / "logs" / "events.log"
    log_tail = _tail_lines(log_path, 5)

    diag = {
        "project_root": str(root),
        "config": {
            "config_json_ok": config_ok,
            "config_error": config_err,
            "permissions_json_ok": perms_ok,
            "permissions_error": perms_err,
            "sandbox_json_ok": sandbox_ok,
            "sandbox_error": sandbox_err,
            "backend": backend,
            "debug_mode": config.get("debug_mode") if isinstance(config, dict) else None,
            "context_length": config.get("context_length") if isinstance(config, dict) else None,
            "max_tokens": config.get("max_tokens") if isinstance(config, dict) else None,
            "temperature": config.get("temperature") if isinstance(config, dict) else None,
        },
        "model": {
            "backend": backend,
            "configured_path": model_rel,
            "resolved_path": str(model_path) if model_path else None,
            "exists": bool(model_path and model_path.exists()),
        },
        "registry": {
            "manifest_ok": manifest_ok,
            "manifest_error": manifest_err,
            "tool_count": len(tools),
            "enabled_tool_count": sum(1 for t in tools if t.get("enabled")),
            "tool_names": [t.get("name") for t in tools],
            "skill_count": len(skills),
            "skill_names": skills,
            "external_skill_count": len(external_skills),
            "external_skill_names": external_skills,
        },
        "runtime": {
            "session_state_ok": session_ok,
            "session_state_error": session_err,
            "session_status": session.get("status") if isinstance(session, dict) else None,
            "pending_action": session.get("pending_action") if isinstance(session, dict) else None,
            "memory_state_ok": state_ok,
            "memory_state_error": state_err,
            "logs_exists": log_path.exists(),
            "logs_size_bytes": log_path.stat().st_size if log_path.exists() else 0,
            "logs_tail": log_tail,
        },
        "permissions": {
            "blocked_tools": perms.get("blocked_tools") if isinstance(perms, dict) else None,
            "tool_tiers": perms.get("tool_tiers") if isinstance(perms, dict) else None,
            "sandbox_restricted_paths": sandbox.get("restricted_paths") if isinstance(sandbox, dict) else None,
        },
    }

    return diag
