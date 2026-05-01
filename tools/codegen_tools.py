from typing import Any, Dict

from tools.linter_tools import lint_code


def codegen(prompt: str, skill_name: str | None = None) -> Dict[str, Any]:
    prompt_lower = prompt.lower()

    if "add" in prompt_lower and "two number" in prompt_lower:
        code = "def add_two_numbers(a, b):\n    return a + b\n"
    elif "hello world" in prompt_lower:
        code = "def hello_world():\n    print('hello world')\n"
    else:
        code = "def generated_function():\n    return 'generated'\n"

    lint = lint_code(code)

    return {
        "status": "ok" if lint["status"] == "ok" else "lint_issues",
        "skill_name": skill_name,
        "code": code,
        "lint": lint,
    }
