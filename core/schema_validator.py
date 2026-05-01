from typing import Dict, Any


def validate_tool_call(
    tool_name: str, payload: Dict[str, Any], tool_registry: Dict[str, Any]
) -> tuple[bool, str]:
    tool_entry = tool_registry.get(tool_name)
    if tool_entry is None:
        return False, "tool_not_found"

    spec = getattr(tool_entry, "spec", None)
    args_schema = getattr(spec, "args_schema", {}) if spec is not None else {}

    required_fields = set(args_schema.keys())
    missing = [field for field in required_fields if field not in payload]

    if missing:
        return False, f"missing_fields: {', '.join(missing)}"

    return True, "valid"
