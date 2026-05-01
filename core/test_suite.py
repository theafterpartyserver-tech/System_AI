from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import time


# ── Models (merged from core/test_models.py) ──────────────────────────────────

@dataclass
class TestCase:
    name: str
    prompt: str
    expected_mode: Optional[str] = None
    expected_tool: Optional[str] = None
    expected_contains: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ── Suite ─────────────────────────────────────────────────────────────────────

class TestSuite:
    def __init__(self):
        self._cases: List[TestCase] = []
        self._results: List[TestResult] = []

    def add_case(self, name: str, prompt: str, expected_mode: Optional[str] = None,
                 expected_tool: Optional[str] = None, expected_contains: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> TestCase:
        case = TestCase(name=name, prompt=prompt, expected_mode=expected_mode,
                        expected_tool=expected_tool, expected_contains=expected_contains,
                        metadata=metadata or {})
        self._cases.append(case)
        return case

    def run(self, runner: Any) -> List[TestResult]:
        self._results = []
        for case in self._cases:
            self._results.append(self._run_case(case, runner))
        return list(self._results)

    def _run_case(self, case: TestCase, runner: Any) -> TestResult:
        try:
            output = runner(case.prompt)
            passed, message, details = self._evaluate_case(case, output)
            return TestResult(name=case.name, passed=passed, message=message, details=details)
        except Exception as e:
            return TestResult(name=case.name, passed=False, message=str(e),
                              details={"exception": type(e).__name__})

    def _evaluate_case(self, case: TestCase,
                       output: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
        details: Dict[str, Any] = {"output": output}
        if case.expected_mode and output.get("mode") != case.expected_mode:
            return False, "Unexpected mode.", details
        if case.expected_tool is not None and output.get("tool") != case.expected_tool:
            return False, "Unexpected tool.", details
        if case.expected_contains and case.expected_contains not in str(output.get("raw_response", "")):
            return False, "Expected text not found.", details
        return True, "Passed.", details

    def results(self) -> List[TestResult]: return list(self._results)

    def as_dict(self) -> Dict[str, Any]:
        return {"cases": [asdict(c) for c in self._cases],
                "results": [asdict(r) for r in self._results]}
