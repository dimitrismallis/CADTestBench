"""Metrics package: dynamic discovery + factory for ``EvaluationMetric`` subclasses."""
from __future__ import annotations

import inspect
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules
from typing import Dict, List, Type

from .interface import EvaluationMetric, MetricResult, SampleData

__all__ = [
    "EvaluationMetric",
    "MetricResult",
    "SampleData",
    "available_metrics",
    "create_metric",
]

# Global registry: metric_name -> metric_class
METRIC_REGISTRY: Dict[str, Type[EvaluationMetric]] = {}


def _discover_metrics() -> None:
    """Import every public module in this package and register metric classes."""
    package_dir = Path(__file__).resolve().parent

    for module_info in iter_modules([str(package_dir)]):
        if module_info.name.startswith("_"):
            continue
        if module_info.name == "interface":
            continue

        module_name = f"{__name__}.{module_info.name}"
        module = import_module(module_name)

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not (issubclass(obj, EvaluationMetric) and obj is not EvaluationMetric):
                continue
            try:
                instance = obj()
            except TypeError:
                # Metric requires non-default args; skip auto-registration.
                continue

            metric_name = instance.name
            if metric_name in METRIC_REGISTRY and METRIC_REGISTRY[metric_name] is not obj:
                raise ValueError(
                    f"Duplicate metric name '{metric_name}' for "
                    f"{METRIC_REGISTRY[metric_name]} and {obj}"
                )
            METRIC_REGISTRY[metric_name] = obj


_discover_metrics()


def available_metrics() -> List[str]:
    """Return the list of all discovered metric names."""
    return sorted(METRIC_REGISTRY.keys())


def create_metric(name: str, **kwargs) -> EvaluationMetric:
    """Instantiate a metric by its registered name."""
    try:
        cls = METRIC_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown metric '{name}'. Available metrics: {available_metrics()}"
        ) from exc
    return cls(**kwargs)
