from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ReleaseGateResult:
    ok: bool
    message: str = ""
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ReleaseGate:
    def __init__(self, min_pass_rate: float = 1.0):
        self.min_pass_rate = min_pass_rate

    def evaluate(self, results: List[Any]) -> ReleaseGateResult:
        total = len(results)
        passed = sum(1 for r in results if getattr(r, "passed", False))
        pass_rate = passed / total if total else 0.0
        blockers = []
        warnings = []

        if pass_rate < self.min_pass_rate:
            blockers.append(f"pass_rate_below_threshold:{pass_rate:.2f}")

        return ReleaseGateResult(
            ok=len(blockers) == 0,
            message="Release allowed." if not blockers else "Release blocked.",
            blockers=blockers,
            warnings=warnings,
            details={"pass_rate": pass_rate, "total": total, "passed": passed},
        )
