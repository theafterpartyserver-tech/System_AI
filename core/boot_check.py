from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> tuple[bool, Any | None, str | None]:
    try:
        return True, json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return False, None, "missing"
    except json.JSONDecodeError as e:
        return False, None, f"invalid_json: {e.msg}"
    except Exception as e:
        return False, None, str(e)


def run_boot_check(project_root: str | Path) -> Dict[str, Any]:
    root = Path(project_root).resolve()

    required_dirs = [
        root / "config",
        root / "core",
        root / "tools",
        root / "skills",
        root / "runtime",
        root / "logs",
        root / "memory",
        root / "models",
    ]
    optional_dirs = [root / "external_skills"]
    required_files = [
        root / "config" / "config.json",
        root / "config" / "permissions.json",
        root / "config" / "sandbox.json",
        root / "tools" / "tools_manifest.json",
    ]

    checks: List[Dict[str, Any]] = []
    ok = True

    for path in required_dirs:
        exists = path.exists() and path.is_dir()
        ok = ok and exists
        checks.append({"kind": "dir", "path": str(path), "required": True, "ok": exists})

    for path in optional_dirs:
        exists = path.exists() and path.is_dir()
        checks.append({"kind": "dir", "path": str(path), "required": False, "ok": exists})

    parsed_config = None
    for path in required_files:
        exists = path.exists() and path.is_file()
        item = {"kind": "file", "path": str(path), "required": True, "ok": exists}
        if exists and path.suffix == ".json":
            valid, payload, error = _load_json(path)
            item["json_ok"] = valid
            if not valid:
                item["error"] = error
                ok = False
            if path.name == "config.json" and valid:
                parsed_config = payload
        else:
            ok = ok and exists
        checks.append(item)

    model_check: Dict[str, Any] = {
        "kind": "model",
        "required": True,
        "ok": False,
        "configured_backend": None,
        "configured_path": None,
    }
    if isinstance(parsed_config, dict):
        backend = parsed_config.get("model_backend")
        model_check["configured_backend"] = backend
        if backend == "local":
            rel = parsed_config.get("local_model_path")
            model_check["configured_path"] = rel
            model_path = (root / rel).resolve() if rel else None
            exists = bool(model_path and model_path.exists() and model_path.is_file())
            model_check["ok"] = exists
            model_check["resolved_path"] = str(model_path) if model_path else None
            if not exists:
                model_check["error"] = "configured_local_model_missing"
                ok = False
        else:
            model_check["ok"] = True
    else:
        model_check["error"] = "config_unavailable"
        ok = False
    checks.append(model_check)

    import_check = {"kind": "python_import", "module": "llama_cpp", "required": False, "ok": False}
    try:
        __import__("llama_cpp")
        import_check["ok"] = True
    except Exception as e:
        import_check["error"] = str(e)
    checks.append(import_check)

    failures = [c for c in checks if c.get("required") and not c.get("ok")]
    warnings = [c for c in checks if (not c.get("required")) and not c.get("ok")]

    return {
        "status": "ok" if ok else "error",
        "project_root": str(root),
        "summary": {
            "required_failures": len(failures),
            "warnings": len(warnings),
            "total_checks": len(checks),
        },
        "checks": checks,
    }
