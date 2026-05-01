from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from core.test_suite import TestResult
from core.test_suite import TestSuite


class RegressionRunner:
    def __init__(self, suite: Optional[TestSuite] = None):
        self.suite = suite or TestSuite()

    def run(self, runner: Callable[[str], Dict[str, Any]]) -> List[TestResult]:
        return self.suite.run(runner)

    def add_default_cases(self) -> None:
        self.suite.add_case(
            name="chat_math",
            prompt="what is 3 + 5?",
            expected_mode="chat",
            expected_contains="8",
        )
        self.suite.add_case(
            name="chat_greeting",
            prompt="say hello in one word",
            expected_mode="chat",
            expected_contains="Hello",
        )
        self.suite.add_case(
            name="file_read",
            prompt="read memory/index.json",
            expected_mode="tool",
            expected_tool="file_read",
        )
        self.suite.add_case(
            name="lint_code",
            prompt='lint code: print("hello")',
            expected_mode="tool",
            expected_tool="lint_code",
        )

    def summary(self) -> Dict[str, Any]:
        results = self.suite.results()
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        return {
            "passed": passed,
            "failed": failed,
            "total": len(results),
        }
