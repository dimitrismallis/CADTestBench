"""Evaluation runner for CADTestBench."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional

from .constants import (
    config_filename,
    eval_root_dir,
    eval_sample_stl_filename,
    eval_samples_subdir,
    generated_models_dir,
    project_root,
    eval_sample_summary_filename,
    summary_filename,
)
from .loaders import CADTestBenchLoader, CADTestBenchSample
from .metrics import (
    EvaluationMetric,
    MetricResult,
    SampleData,
    create_metric,
)


Partition = Literal["abstract", "detailed"]

_WIN_FORBIDDEN_NAME_CHARS = frozenset('<>:"/\\|?*')


def filesystem_run_label_slug(raw: str, max_len: int = 120) -> str:
    """Turn a human-readable experiment label into a single folder-name segment."""
    if not raw or not str(raw).strip():
        return "run"
    parts: List[str] = []
    for ch in str(raw).strip():
        if ch in _WIN_FORBIDDEN_NAME_CHARS or ord(ch) < 32:
            parts.append("_")
        elif ch.isspace():
            parts.append("_")
        else:
            parts.append(ch)
    slug = "".join(parts)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug[:max_len] if slug else "run"


_CATEGORY_ABBREV: Dict[str, str] = {
    "topology_checks": "topo",
    "solid_shell_validity": "solid",
    "dimensions_ratios": "dim",
    "volumetric_checks": "vol",
    "spatial_arrangement": "space",
    "geometry_types": "geom",
}


@dataclass
class EvaluationResult:
    """Per-sample container saved to disk after evaluation."""

    sample_id: str
    prompt_text: str
    generated_stl_path: Optional[Path] = None
    evaluation_time: Optional[float] = None
    timestamp: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        generated_stl = (
            Path(self.generated_stl_path).name if self.generated_stl_path else None
        )
        return {
            "sample_id": self.sample_id,
            "prompt_text": self.prompt_text,
            "generated_stl": generated_stl,
            "evaluation_time": self.evaluation_time,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
            "metrics": self.metrics,
        }


class EvaluationRunner:
    """Score pre-generated CAD models against the benchmark."""

    def __init__(
        self,
        dataset_loader: CADTestBenchLoader,
        generation_dir: Path,
        metrics: List[Dict[str, Any]],
        partition: Partition = "detailed",
        final_configs: Optional[Dict[str, Any]] = None,
        eval_root: Optional[Path] = None,
        run_label: Optional[str] = None,
        run_name_suffix: Optional[str] = None,
    ):
        """Initialize the runner.

        Args:
            dataset_loader: Loader for the benchmark dataset.
            generation_dir: Generation-output directory; models are expected
                under ``{generation_dir}/generated_models``.
            metrics: List of metric specs, each ``{"name": str, "kwargs": {...}}``.
            partition: Benchmark partition (``"abstract"`` or ``"detailed"``).
            final_configs: Resolved configuration to dump alongside results.
            eval_root: Override for the top-level eval folder. Defaults to
                ``{project_root}/eval``.
            run_label: If set, used as the human-readable part of the eval folder
                name instead of inferring from ``generation_dir`` (e.g.
                ``CADTests__GPT-5.2`` for paper tables).
            run_name_suffix: If set, appended to the run folder name so parallel
                batch jobs do not collide.
        """
        self.dataset_loader = dataset_loader

        self.generation_dir = Path(generation_dir)
        if not self.generation_dir.exists():
            raise FileNotFoundError(
                f"Generation directory does not exist: {self.generation_dir}"
            )

        if partition not in ("abstract", "detailed"):
            raise ValueError(
                f"partition must be 'abstract' or 'detailed', got {partition!r}"
            )
        self.partition: Partition = partition
        self.models_dir = self.generation_dir / generated_models_dir

        if not metrics:
            raise ValueError(
                "EvaluationRunner requires at least one metric spec; got empty list."
            )

        self.metrics: List[EvaluationMetric] = [
            create_metric(spec["name"], **spec.get("kwargs", {})) for spec in metrics
        ]

        if eval_root is None:
            eval_root = project_root() / eval_root_dir
        self.eval_root = Path(eval_root)

        self.run_name = self._build_run_name(
            self.generation_dir,
            self.partition,
            run_label=run_label,
        )
        if run_name_suffix:
            self.run_name = f"{self.run_name}_{run_name_suffix}"
        self.output_dir = self.eval_root / self.run_name

        self.eval_samples_root = self.output_dir / eval_samples_subdir
        self.eval_samples_root.mkdir(parents=True, exist_ok=True)

        with open(self.output_dir / config_filename, "w") as f:
            json.dump(final_configs or {}, f, indent=2)

    @staticmethod
    def _baseline_name(generation_dir: Path) -> str:
        """Combine parent dir + generation dir into a baseline label."""
        parent = generation_dir.parent.name or "baseline"
        return f"{parent}__{generation_dir.name}"

    @classmethod
    def _build_run_name(
        cls,
        generation_dir: Path,
        partition: str,
        *,
        run_label: Optional[str] = None,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if run_label:
            slug = filesystem_run_label_slug(run_label)
            return f"{timestamp}_{slug}_{partition}"
        baseline = cls._baseline_name(generation_dir)
        if generation_dir.name.lower() == partition:
            return f"{timestamp}_{baseline}"
        return f"{timestamp}_{baseline}_{partition}"

    def find_generated_model(self, sample_id: str) -> Optional[Path]:
        """Locate the STL produced for a sample, if any."""
        sample_dir = self.models_dir / sample_id
        if not sample_dir.exists():
            return None

        for stl_file in sample_dir.glob("*.stl"):
            if stl_file.stat().st_size > 0 and "generated" in stl_file.name.lower():
                return stl_file
        return None

    def get_available_samples(self) -> List[str]:
        if not self.models_dir.exists():
            return []
        return sorted(d.name for d in self.models_dir.iterdir() if d.is_dir())

    def evaluate_sample(
        self,
        sample: CADTestBenchSample,
        generated_stl_path: Optional[Path] = None,
        **evaluation_kwargs: Any,
    ) -> EvaluationResult:
        start_time = time.time()
        prompt_text = sample.prompt_text

        if generated_stl_path is None:
            generated_stl_path = self.find_generated_model(sample.sample_id)

        eval_result = EvaluationResult(
            sample_id=sample.sample_id,
            prompt_text=prompt_text,
            generated_stl_path=generated_stl_path,
        )

        try:
            eval_result.metrics = self._compute_metrics(
                generated_stl=generated_stl_path,
                sample_id=sample.sample_id,
                prompt_text=prompt_text,
                **evaluation_kwargs,
            )
            exported_stl = (
                self.eval_samples_root / sample.sample_id / eval_sample_stl_filename
            )
            if exported_stl.exists():
                eval_result.generated_stl_path = exported_stl
        except Exception as e:
            eval_result.error_message = str(e)
        finally:
            eval_result.evaluation_time = time.time() - start_time
            eval_result.timestamp = datetime.now().isoformat()

        return eval_result

    def _compute_metrics(
        self,
        generated_stl: Optional[Path],
        sample_id: str,
        prompt_text: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        sample_data = SampleData(
            sample_id=sample_id,
            generated_stl_path=generated_stl,
            prompt_text=prompt_text,
            sample_folder_path=self.models_dir / sample_id,
            additional_info=kwargs.get("sample_additional_info"),
            eval_sample_dir=self.eval_samples_root / sample_id,
        )

        metrics_dict: Dict[str, Any] = {}
        for metric in self.metrics:
            try:
                result = metric.compute_sample_metric(sample_data)
                metrics_dict[metric.name] = {
                    "value": result.value,
                    "success": result.success,
                    "metadata": result.metadata,
                }
                if not result.success and result.error_message:
                    metrics_dict[metric.name]["error"] = result.error_message
            except Exception as e:
                metrics_dict[metric.name] = {
                    "value": None,
                    "success": False,
                    "error": str(e),
                }
        return metrics_dict

    def evaluate_samples(
        self,
        sample_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **evaluation_kwargs: Any,
    ) -> Dict[str, Any]:
        all_samples = self.dataset_loader.load_samples(
            sample_ids=sample_ids, limit=limit
        )
        total_samples = len(all_samples)
        all_results: List[EvaluationResult] = []
        index_width = max(3, len(str(total_samples)))

        start_time = time.time()

        for i, sample in enumerate(all_samples, 1):
            try:
                if progress_callback:
                    progress_callback(i, total_samples, sample.sample_id)

                eval_result = self.evaluate_sample(sample, **evaluation_kwargs)
                all_results.append(eval_result)
                self._save_evaluation_result(eval_result)

                if not progress_callback:
                    print(
                        self._format_sample_line(
                            i, total_samples, eval_result, index_width
                        )
                    )
            except Exception as e:
                err_result = EvaluationResult(
                    sample_id=sample.sample_id,
                    prompt_text="",
                    error_message=str(e),
                    timestamp=datetime.now().isoformat(),
                    evaluation_time=0.0,
                )
                all_results.append(err_result)
                if not progress_callback:
                    print(
                        f"[{i:>{index_width}}/{total_samples}] {sample.sample_id}  "
                        f"ERROR  runner_exception: {type(e).__name__}: {e}"
                    )

        total_time = time.time() - start_time
        summary = self._create_evaluation_summary(all_results, total_time)
        self._save_evaluation_summary(summary)

        return summary

    @staticmethod
    def _format_sample_line(
        index: int,
        total: int,
        eval_result: EvaluationResult,
        index_width: int,
    ) -> str:
        """One-line console summary for a single evaluated sample.

        Format::

            [001/200] 00000007  PASS 12/12  0.19s   topo:6/6 dim:2/2 ...   RS 6/6
            [002/200] 00000042  FAIL  9/12  0.21s   topo:5/6 dim:1/2 ...   RS 4/6  (3 failed)
            [003/200] 00000099  ERROR  model_compile_error  0.05s
        """
        prefix = f"[{index:>{index_width}}/{total}] {eval_result.sample_id}"
        elapsed = eval_result.evaluation_time or 0.0

        if eval_result.error_message and not eval_result.metrics:
            return f"{prefix}  ERROR  runner_exception  {elapsed:.2f}s  {eval_result.error_message}"

        primary = (eval_result.metrics or {}).get("cadtest")
        if not primary:
            status = "OK" if not eval_result.error_message else "ERROR"
            return f"{prefix}  {status}  {elapsed:.2f}s"

        summary = (primary.get("metadata") or {}).get("summary") or {}
        eval_error = summary.get("evaluation_error")
        compile_error = summary.get("model_compile_error", False)

        if eval_error:
            return f"{prefix}  ERROR  {eval_error}  {elapsed:.2f}s"
        if compile_error:
            return f"{prefix}  ERROR  model_compile_error  {elapsed:.2f}s"

        passed = summary.get("passed", 0)
        total_a = summary.get("total_cadtests", 0)
        status = "PASS" if passed == total_a and total_a > 0 else "FAIL"
        counts = f"{passed:>3}/{total_a:<3}"

        cats = summary.get("category_breakdown", {}) or {}
        cat_parts = [
            f"{_CATEGORY_ABBREV.get(name, name[:5])}:{c.get('passed', 0)}/{c.get('total', 0)}"
            for name, c in cats.items()
        ]
        cat_str = " ".join(cat_parts)

        rs_groups = summary.get("rs_groups", {}) or {}
        rs_part = f"RS {rs_groups.get('passed', 0)}/{rs_groups.get('total', 0)}"

        line = f"{prefix}  {status}  {counts}  {elapsed:.2f}s   {cat_str}   {rs_part}"
        if status == "FAIL":
            line += f"  ({total_a - passed} failed)"
        return line

    def _save_evaluation_result(self, eval_result: EvaluationResult) -> None:
        sample_dir = self.eval_samples_root / eval_result.sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)
        result_file = sample_dir / eval_sample_summary_filename
        with open(result_file, "w") as f:
            json.dump(eval_result.to_dict(), f, indent=2)

    def _save_evaluation_summary(self, summary: Dict[str, Any]) -> None:
        summary_file = self.output_dir / summary_filename
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

    def _create_evaluation_summary(
        self,
        all_results: List[EvaluationResult],
        total_time: float,
    ) -> Dict[str, Any]:
        total_evaluated = len(all_results)
        aggregate_metrics: Dict[str, Any] = {}

        for metric in self.metrics:
            metric_results: List[MetricResult] = []

            for eval_result in all_results:
                has_metric = (
                    eval_result.metrics is not None
                    and metric.name in eval_result.metrics
                )

                if has_metric and eval_result.metrics:
                    metric_data = eval_result.metrics[metric.name]
                    success = bool(metric_data.get("success", False))
                    metric_results.append(
                        MetricResult(
                            metric_name=metric.name,
                            sample_id=eval_result.sample_id,
                            value=metric_data.get("value", 0.0),
                            success=success,
                            metadata=metric_data.get("metadata"),
                            error_message=metric_data.get("error"),
                        )
                    )
                else:
                    metric_results.append(
                        MetricResult(
                            metric_name=metric.name,
                            sample_id=eval_result.sample_id,
                            value=float("inf"),
                            success=False,
                            error_message="Metric missing from evaluation result",
                        )
                    )

            if metric_results:
                aggregate_metrics[metric.name] = metric.aggregate_results(metric_results)

        return {
            "evaluation_info": {
                "dataset": self.dataset_loader.dataset,
                "generation_dir": str(self.generation_dir),
                "output_dir": str(self.output_dir),
                "partition": self.partition,
                "timestamp": datetime.now().isoformat(),
            },
            "statistics": {
                "total_samples": total_evaluated,
                "total_time_seconds": total_time,
                "average_time_per_sample": (
                    total_time / total_evaluated if total_evaluated > 0 else 0.0
                ),
            },
            "aggregate_metrics": aggregate_metrics,
        }
