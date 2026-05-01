from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RecoveryPrompt:
    reason: str
    prompt_text: str
    details: Dict[str, Any]


class RecoveryPromptBuilder:
    def build_after_failure(
        self,
        reason: str,
        last_user_input: Optional[str] = None,
        last_action: Optional[Dict[str, Any]] = None,
    ) -> RecoveryPrompt:
        parts = [f"Recovery reason: {reason}"]
        if last_user_input:
            parts.append(f"Last user input: {last_user_input}")
        if last_action:
            parts.append(f"Last action: {last_action}")
        return RecoveryPrompt(
            reason=reason,
            prompt_text="\n".join(parts),
            details={
                "last_user_input": last_user_input,
                "last_action": last_action,
            },
        )
