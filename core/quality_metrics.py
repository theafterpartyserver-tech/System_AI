from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import time


@dataclass
class QualityMetric:
    name: str
    value: float
    unit: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class QualityMetrics:
    def __init__(self):
        self._metrics: List[QualityMetric] = []

    def record(self, name: str, value: float, unit: str = "", details: Dict[str, Any] | None = None) -> QualityMetric:
        metric = QualityMetric(
            name=name,
            value=value,
            unit=unit,
            details=details or {},
        )
        self._metrics.append(metric)
        return metric

    def all(self) -> List[QualityMetric]:
        return list(self._metrics)

    def as_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "details": m.details,
                "timestamp": m.timestamp,
            }
            for m in self._metrics
        ]
