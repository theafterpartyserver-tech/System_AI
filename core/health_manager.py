from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import time


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealthReport:
    status: HealthStatus
    checks: List[HealthCheckResult] = field(default_factory=list)
    summary: str = ""
    timestamp: float = field(default_factory=time.time)

    def add_check(self, result: HealthCheckResult) -> None:
        self.checks.append(result)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                    "timestamp": c.timestamp,
                }
                for c in self.checks
            ],
        }


class HealthManager:
    def __init__(self, project_root: Path, model_path: Optional[str | Path] = None):
        self.project_root = project_root
        self.model_path = Path(model_path) if model_path is not None else None
        self._last_report: Optional[HealthReport] = None
        self._session_logs: List[Dict[str, Any]] = []

    def run_all_checks(self) -> HealthReport:
        report = HealthReport(status=HealthStatus.UNKNOWN)

        report.add_check(self.check_startup())
        report.add_check(self.check_model())
        report.add_check(self.check_tools())
        report.add_check(self.check_registry())
        report.add_check(self.check_config())
        report.add_check(self.check_skills())
        report.add_check(self.check_disk_space())
        report.add_check(self.check_ram())
        report.add_check(self.check_gpu_vram())
        report.add_check(self.check_cpu_load())
        report.add_check(self.check_process_hang())
        report.add_check(self.check_timeout_recovery())
        report.add_check(self.check_restart_watchdog())
        report.add_check(self.check_session_crash_recovery())
        report.add_check(self.check_session_resume_logs())

        report.status = self._aggregate_status(report.checks)
        report.summary = self._build_summary(report)
        self._last_report = report
        return report

    def check_startup(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="startup",
            status=HealthStatus.HEALTHY,
            message="Startup check stub.",
        )

    def check_model(self) -> HealthCheckResult:
        if not self.model_path:
            return HealthCheckResult(
                name="model",
                status=HealthStatus.FAILED,
                message="No model path configured.",
            )

        if not self.model_path.exists():
            return HealthCheckResult(
                name="model",
                status=HealthStatus.FAILED,
                message="Model file not found.",
                details={"model_path": str(self.model_path)},
            )

        return HealthCheckResult(
            name="model",
            status=HealthStatus.HEALTHY,
            message="Model file exists.",
            details={"model_path": str(self.model_path)},
        )

    def check_tools(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="tools",
            status=HealthStatus.UNKNOWN,
            message="Tool health check stub.",
        )

    def check_registry(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="registry",
            status=HealthStatus.UNKNOWN,
            message="Registry health check stub.",
        )

    def check_config(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="config",
            status=HealthStatus.UNKNOWN,
            message="Config health check stub.",
        )

    def check_skills(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="skills",
            status=HealthStatus.UNKNOWN,
            message="Skill discovery health check stub.",
        )

    def check_disk_space(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="disk_space",
            status=HealthStatus.UNKNOWN,
            message="Disk-space health check stub.",
        )

    def check_ram(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="ram",
            status=HealthStatus.UNKNOWN,
            message="RAM health check stub.",
        )

    def check_gpu_vram(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="gpu_vram",
            status=HealthStatus.UNKNOWN,
            message="GPU VRAM health check stub.",
        )

    def check_cpu_load(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="cpu_load",
            status=HealthStatus.UNKNOWN,
            message="CPU load health check stub.",
        )

    def check_process_hang(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="process_hang",
            status=HealthStatus.UNKNOWN,
            message="Process hang detection stub.",
        )

    def check_timeout_recovery(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="timeout_recovery",
            status=HealthStatus.UNKNOWN,
            message="Timeout recovery health check stub.",
        )

    def check_restart_watchdog(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="restart_watchdog",
            status=HealthStatus.UNKNOWN,
            message="Restart watchdog health check stub.",
        )

    def check_session_crash_recovery(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="session_crash_recovery",
            status=HealthStatus.UNKNOWN,
            message="Session crash recovery health check stub.",
        )

    def check_session_resume_logs(self) -> HealthCheckResult:
        return HealthCheckResult(
            name="session_resume_logs",
            status=HealthStatus.UNKNOWN,
            message="Session resume logs health check stub.",
        )

    def log_session_event(self, event_name: str, details: Dict[str, Any]) -> None:
        self._session_logs.append(
            {
                "event": event_name,
                "details": details,
                "timestamp": time.time(),
            }
        )

    def get_last_report(self) -> Optional[HealthReport]:
        return self._last_report

    def get_session_logs(self) -> List[Dict[str, Any]]:
        return list(self._session_logs)

    def _aggregate_status(self, checks: List[HealthCheckResult]) -> HealthStatus:
        if any(c.status == HealthStatus.FAILED for c in checks):
            return HealthStatus.FAILED
        if any(c.status == HealthStatus.DEGRADED for c in checks):
            return HealthStatus.DEGRADED
        if all(c.status == HealthStatus.HEALTHY for c in checks):
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN

    def _build_summary(self, report: HealthReport) -> str:
        counts = {s.value: 0 for s in HealthStatus}
        for check in report.checks:
            counts[check.status.value] += 1
        return (
            f"{counts[HealthStatus.HEALTHY.value]} healthy, "
            f"{counts[HealthStatus.DEGRADED.value]} degraded, "
            f"{counts[HealthStatus.FAILED.value]} failed, "
            f"{counts[HealthStatus.UNKNOWN.value]} unknown"
        )


def get_routing_bias() -> str:
    """Stub retained for gateway.py compatibility."""
    return "chat"
