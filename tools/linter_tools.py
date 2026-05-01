from typing import Any, Dict, List


def lint_code(code: str) -> Dict[str, Any]:
    issues: List[str] = []
    lines = code.splitlines()

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.endswith(";"):
            issues.append(f"Line {lineno}: unnecessary semicolon")

        if "print(" in stripped and "debug" not in stripped.lower():
            issues.append(f"Line {lineno}: print statement found")

        if "\t" in line:
            issues.append(f"Line {lineno}: tab indentation found; use spaces")

    if issues:
        return {
            "status": "issues",
            "issues": issues,
            "message": "Lint issues detected."
        }

    return {
        "status": "ok",
        "issues": [],
        "message": "No lint issues found."
    }
