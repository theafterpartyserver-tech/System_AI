# core/reliability.py

from typing import Callable, Any, Dict


def validate_or_retry(
    llm_call_fn: Callable[[str], str],
    parse_fn: Callable[[str], Dict[str, Any]],
    prompt: str,
) -> Dict[str, Any]:
    """
    Call llm_call_fn(prompt), then parse_fn on the raw text.
    Retry up to 2 times; if still invalid, return a safe fallback.
    """
    bad_payloads = 0

    for _ in range(2):
        raw = llm_call_fn(prompt)
        result = parse_fn(raw)

        # Treat any object with a valid "tool" as acceptable.
        if isinstance(result, dict) and "tool" in result:
            return result

        bad_payloads += 1

    # After 2 failed attempts, return safe fallback:
    # - if tool was parsed but something else failed, keep it
    # - otherwise: no tool, but still valid JSON.
    if isinstance(result, dict) and "tool" in result:
        return result
    else:
        return {
            "mode": "chat",
            "intent": "",
            "tool": None,
            "args": {},
            "raw_response": raw,
        }
