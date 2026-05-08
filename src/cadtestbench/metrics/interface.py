"""
Base classes for CADTestBench evaluation metrics.

Each metric computes a numerical score (per sample) and an aggregation
(across samples) comparing a generated CAD model against a ground-truth
reference.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np


@dataclass
class MetricResult:
    """Result of a single metric computation on one sample."""

    metric_name: str
    sample_id: str
    value: float
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class SampleData:
    """All data a metric needs to score a single sample."""

    sample_id: str
    sample_folder_path: Path
    generated_stl_path: Optional[Path] = None
    prompt_text: str = ""
    sample_metadata: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    # When set, metrics may write per-sample artefacts (e.g. exported STL, replay scripts).
    eval_sample_dir: Optional[Path] = None


class EvaluationMetric(ABC):
    """Abstract base class for evaluation metrics."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def compute_sample_metric(self, sample_data: SampleData) -> MetricResult:
        """Compute the metric for a single sample."""

    @abstractmethod
    def aggregate_results(self, results: List[MetricResult]) -> Dict[str, Any]:
        """Aggregate per-sample results into summary statistics."""

    def get_aggregation_functions(
        self,
    ) -> Dict[str, Callable[[List[float]], float]]:
        """Default aggregation helpers metrics can reuse."""
        return {
            "mean": lambda values: float(np.mean(values)),
            "median": lambda values: float(np.median(values)),
            "std": lambda values: float(np.std(values)),
            "min": lambda values: float(np.min(values)),
            "max": lambda values: float(np.max(values)),
            "count": lambda values: len(values),
        }
