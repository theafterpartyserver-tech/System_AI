from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized: Dict[str, Any] = field(default_factory=dict)


class ToolOutputValidator:
    def validate(self, tool_name: str, result: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(result, dict):
            return ValidationResult(
                ok=False,
                message="Tool result must be a dict.",
                errors=["non_dict_result"],
            )

        status = result.get("status")
        if status is None:
            warnings.append("missing_status")

        if tool_name in {"file_read", "file_write", "lint_code", "codegen", "shell_exec"}:
            if "status" not in result:
                errors.append("status_missing")

        normalized = dict(result)
        if normalized.get("tool") == "null":
            normalized["tool"] = None

        ok = len(errors) == 0
        return ValidationResult(
            ok=ok,
            message="Validation passed." if ok else "Validation failed.",
            errors=errors,
            warnings=warnings,
            normalized=normalized,
        )
