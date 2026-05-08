"""
CADTest metric: functional evaluation of CAD generations via executable cadtests.

The metric pulls the per-sample bundle from a CADTestBench Parquet dataset
(local ``data/hf/`` layout or a HF Hub repo id), reconstructed by
:class:`HFDatasetSource` into the shape::

    {
        "sample_id": "...",
        "requirement_groups": [...],
        "cadtests": [
            {
                "cadtest_id": <int|str>,
                "cadtest_description": "...",
                "prompt_justification": "...",
                "cadtest_code": "...",
                "cadtest_type": "...",
                "classification_reasoning": "...",
                "requirement_id": "..." | null,
                "requirement_type": "..." | null,
                "requirement_description": "..." | null
            },
            ...
        ]
    }

Older bundles may still use ``dof_*`` keys; readers fall back to those.
"""
from __future__ import annotations

import ast
import contextlib
import io
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import cadquery as cq

from ..constants import eval_sample_stl_filename
from ..data_source import HFDatasetSource
from .interface import EvaluationMetric, MetricResult, SampleData


def _row_id(row: Dict[str, Any]) -> Any:
    return row.get("cadtest_id")


def _row_code(row: Dict[str, Any]) -> str:
    v = row.get("cadtest_code")
    return "" if v is None else str(v)


def _group_cadtest_ids(group: Dict[str, Any]) -> List[Any]:
    return list(group.get("cadtest_ids") or [])


ASSERTION_EXEC_PREAMBLE = """import math
_check_pass_msg = None
def check(condition, pass_msg, fail_msg):
    global _check_pass_msg
    if not condition:
        raise AssertionError(fail_msg)
    _check_pass_msg = pass_msg
"""


def _indent_block(text: str, spaces: int = 4) -> str:
    pad = " " * spaces
    return "\n".join(f"{pad}{line}" for line in text.splitlines())


def _extract_model_var_name(code: str, code_path: str) -> str:
    """Return the variable name passed to ``cq.exporters.export(...)``."""
    tree = ast.parse(code, code_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "export"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "exporters"
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id == "cq"
            ):
                if node.args and isinstance(node.args[0], ast.Name):
                    return node.args[0].id
    return "final_result"


def _get_cadtest_category(row: Dict) -> str:
    return str(row.get("cadtest_type") or "uncategorized")


def _normalize_cadtest_id(raw_id: Any) -> Any:
    if isinstance(raw_id, int):
        return raw_id
    if isinstance(raw_id, str):
        stripped = raw_id.strip()
        if stripped.isdigit():
            return int(stripped)
        return stripped
    return raw_id


def _bundle_requirement_groups(
    bundle_doc: Dict[str, Any],
) -> Optional[List[Dict[str, Any]]]:
    raw = bundle_doc.get("requirement_groups")
    if raw is None:
        raw = bundle_doc.get("dof_groups")
    if isinstance(raw, list):
        return list(raw)
    return None


def _row_requirement_id(row: Dict[str, Any]) -> Any:
    return row.get("requirement_id", row.get("dof_id"))


def _row_requirement_type(row: Dict[str, Any]) -> Any:
    return row.get("requirement_type", row.get("dof_type"))


def _row_requirement_description(row: Dict[str, Any]) -> Any:
    return row.get("requirement_description", row.get("dof_description"))


def _group_requirement_id(g: Dict[str, Any]) -> Any:
    return g.get("requirement_id", g.get("dof_id"))


def _group_requirement_type(g: Dict[str, Any]) -> Any:
    return g.get("requirement_type", g.get("dof_type"))


def _group_requirement_description(g: Dict[str, Any]) -> Any:
    return g.get("requirement_description", g.get("dof_description"))


def _build_cadtest_entry(
    row: Dict[str, Any],
    status: str,
    message: Optional[str] = None,
    exception: Optional[str] = None,
) -> Dict[str, Any]:
    """Per-cadtest record written to the per-sample eval JSON."""
    entry: Dict[str, Any] = {
        "id": _normalize_cadtest_id(_row_id(row)),
        "category": _get_cadtest_category(row),
        "requirement_id": _row_requirement_id(row),
        "description": row.get("cadtest_description"),
        "cadtest_code": _row_code(row),
        "status": status,
        "message": message,
    }
    if exception is not None:
        entry["exception"] = exception
    return entry


def _compute_rs_scoring(
    cadtests: List[Dict[str, Any]],
    passed_ids: Set[Any],
    filtered_cadtest_ids: Set[Any],
    requirement_groups: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Aggregate pass/fail counts per requirement group (RS breakdown).

    A group passes only if every filtered cadtest belonging to it passed.
    """
    normalized_filtered = {_normalize_cadtest_id(aid) for aid in filtered_cadtest_ids}
    normalized_passed = {_normalize_cadtest_id(aid) for aid in passed_ids}

    by_req: "Dict[Any, Dict[str, Any]]" = {}
    if requirement_groups:
        for g in requirement_groups:
            rid = _group_requirement_id(g)
            if rid is None or rid in by_req:
                continue
            kept_ids = [
                _normalize_cadtest_id(aid)
                for aid in _group_cadtest_ids(g)
                if _normalize_cadtest_id(aid) in normalized_filtered
            ]
            by_req[rid] = {
                "requirement_id": rid,
                "requirement_type": _group_requirement_type(g),
                "requirement_description": _group_requirement_description(g),
                "cadtest_ids": kept_ids,
            }
    else:
        for row in cadtests:
            rid = _row_requirement_id(row)
            if rid is None:
                continue
            aid = _normalize_cadtest_id(_row_id(row))
            if aid not in normalized_filtered:
                continue
            bucket = by_req.setdefault(
                rid,
                {
                    "requirement_id": rid,
                    "requirement_type": _row_requirement_type(row),
                    "requirement_description": _row_requirement_description(row),
                    "cadtest_ids": [],
                },
            )
            bucket["cadtest_ids"].append(aid)

    groups: List[Dict[str, Any]] = []
    groups_passed = 0
    for bucket in by_req.values():
        ids = bucket["cadtest_ids"]
        if not ids:
            continue
        n_passed = sum(1 for aid in ids if aid in normalized_passed)
        all_passed = n_passed == len(ids)
        if all_passed:
            groups_passed += 1
        groups.append(
            {
                "requirement_id": bucket["requirement_id"],
                "requirement_type": bucket["requirement_type"],
                "requirement_description": bucket["requirement_description"],
                "total": len(ids),
                "passed": n_passed,
                "all_passed": all_passed,
                "cadtest_ids": ids,
            }
        )

    if not groups:
        return {
            "available": False,
            "groups": [],
            "groups_total": 0,
            "groups_passed": 0,
            "rs": 0.0,
            "error": "No requirement groups were evaluated (no requirement_id on cadtests).",
        }

    return {
        "available": True,
        "groups": groups,
        "groups_total": len(groups),
        "groups_passed": groups_passed,
        "rs": groups_passed / len(groups) * 100.0,
    }


def _resolve_model_code_path(
    sample_data: SampleData,
    generated_code_subdir: str,
    code_filename_prefix: str,
    legacy_code_filename: str,
    strict_generated_code: bool = False,
) -> Path:
    sample_dir = sample_data.sample_folder_path
    code_dir = sample_dir / generated_code_subdir
    candidates: List[Path] = []

    stl_path = sample_data.generated_stl_path
    if stl_path:
        stl_name = Path(stl_path).name
        if stl_name.endswith(".stl"):
            stl_stem = Path(stl_name).stem
            if not strict_generated_code or stl_stem.startswith(code_filename_prefix):
                candidates.append(code_dir / f"{stl_stem}.py")
                candidates.append(sample_dir / f"{stl_stem}.py")

        suffix_match = re.match(rf"^{re.escape(code_filename_prefix)}_(\d+)\.stl$", stl_name)
        if suffix_match:
            idx = suffix_match.group(1)
            candidates.append(code_dir / f"{code_filename_prefix}_{idx}.py")
            candidates.append(sample_dir / f"{code_filename_prefix}_{idx}.py")

    candidates.append(sample_dir / legacy_code_filename)
    candidates.append(code_dir / legacy_code_filename)
    candidates.extend(sorted(code_dir.glob(f"{code_filename_prefix}_*.py")))
    candidates.extend(sorted(sample_dir.glob(f"{code_filename_prefix}_*.py")))

    if not strict_generated_code:
        candidates.extend(sorted(sample_dir.glob(f"**/{code_filename_prefix}*.py")))

    seen: Set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if path.exists() and path.is_file():
            return path

    raise FileNotFoundError(
        f"Could not find generated code for sample '{sample_data.sample_id}'. "
        f"Searched in '{sample_dir}' and '{code_dir}'."
    )


def _execute_one_cadtest(
    row: Dict[str, Any], env: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute one cadtest against ``env`` and return a structured entry."""
    code = _row_code(row)
    env["_check_pass_msg"] = None
    try:
        exec(ASSERTION_EXEC_PREAMBLE + code, env)
        return _build_cadtest_entry(
            row,
            status="pass",
            message=env.get("_check_pass_msg"),
        )
    except AssertionError as e:
        return _build_cadtest_entry(
            row,
            status="fail",
            message=str(e) or "cadtest failed",
            exception="AssertionError",
        )
    except Exception as e:
        return _build_cadtest_entry(
            row,
            status="fail",
            message=f"{type(e).__name__}: {e}",
            exception=type(e).__name__,
        )


def _run_cadtest_block(
    cadtests: List[Dict[str, Any]],
    model_source: str,
    execution_cwd: Optional[Path] = None,
    model_file_path: Optional[Path] = None,
    export_stl_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute the model's source then run each cadtest against it.

    Returns a dict with ``cadtests`` (per-cadtest entries),
    ``model_compile_error`` / ``model_error`` for the model exec failure path,
    ``execution_stdout`` (text captured from stdout, not echoed to terminal),
    and optionally ``stl_export_error``.
    """

    capture = io.StringIO()

    def _fail_all(reason: str) -> Dict[str, Any]:
        return {
            "cadtests": [
                _build_cadtest_entry(
                    row,
                    status="fail",
                    message=reason,
                    exception="ModelExecError",
                )
                for row in cadtests
            ],
            "model_compile_error": True,
            "model_error": reason,
            "execution_stdout": capture.getvalue(),
        }

    code_path_str = str(model_file_path) if model_file_path is not None else "<generated_model>"

    try:
        model_var_name = _extract_model_var_name(model_source, code_path_str)
    except Exception as e:
        return _fail_all(f"model parse error: {type(e).__name__}: {e}")

    env: Dict[str, Any] = {"__name__": "__main__", "cq": cq}
    if model_file_path is not None:
        env["__file__"] = str(model_file_path)

    cadtest_entries: List[Dict[str, Any]] = []
    stl_export_error: Optional[str] = None

    previous_cwd: Optional[str] = None
    try:
        if execution_cwd is not None:
            previous_cwd = os.getcwd()
            os.chdir(str(execution_cwd))

        with contextlib.redirect_stdout(capture):
            try:
                sanitized = "\n".join(
                    line for line in model_source.splitlines()
                    if "cq.exporters.export" not in line
                )
                compiled = compile(sanitized, code_path_str, "exec", optimize=2)
                exec(compiled, env)
            except Exception as e:
                return _fail_all(f"model exec error: {type(e).__name__}: {e}")

            if model_var_name not in env:
                return _fail_all(
                    f"model exec produced no variable named {model_var_name!r} "
                    "(was the export call removed?)"
                )

            env["final_result"] = env[model_var_name]

            cadtest_entries = [_execute_one_cadtest(row, env) for row in cadtests]

            if export_stl_path is not None:
                try:
                    export_stl_path = Path(export_stl_path)
                    export_stl_path.parent.mkdir(parents=True, exist_ok=True)
                    cq.exporters.export(env["final_result"], str(export_stl_path))
                except Exception as e:
                    stl_export_error = f"{type(e).__name__}: {e}"
    finally:
        if previous_cwd is not None:
            os.chdir(previous_cwd)

    out: Dict[str, Any] = {
        "cadtests": cadtest_entries,
        "model_compile_error": False,
        "model_error": None,
        "execution_stdout": capture.getvalue(),
    }
    if stl_export_error is not None:
        out["stl_export_error"] = stl_export_error
    return out


def create_code_cadtest_block(model_code: str, cadtests: List[Dict]) -> str:
    """Build a self-contained replay script (model + cadtests) for debugging."""
    model_code = "\n".join(
        line for line in model_code.splitlines() if "cq.exporters.export" not in line
    )
    model_code_indented = _indent_block(model_code)
    parts = [
        f"""
cadtest_results_tracker = {{"total_test": 0, "passed": [], "failed": [], "categories": {{}}, "model_compile_error": False}}
try:
{model_code_indented}
except Exception as e:"""
    ]

    for row in cadtests:
        aid = _row_id(row)
        cat = '"' + _get_cadtest_category(row) + '"'
        parts.append(
            f"""
    cadtest_results_tracker["total_test"] += 1
    cadtest_results_tracker["categories"].setdefault({cat}, {{"passed": [], "failed": []}})
    cadtest_results_tracker["failed"].append({aid})
    cadtest_results_tracker["categories"][{cat}]["failed"].append({aid})"""
        )

    parts.append(
        """
    cadtest_results_tracker["model_compile_error"] = True
else:
"""
    )

    for row in cadtests:
        aid = _row_id(row)
        code = _row_code(row)
        cat = '"' + _get_cadtest_category(row) + '"'
        indented_code = _indent_block(code, spaces=8)
        parts.append(
            f"""
    try:
        cadtest_results_tracker["total_test"] += 1
        cadtest_results_tracker["categories"].setdefault({cat}, {{"passed": [], "failed": []}})
{indented_code}
        cadtest_results_tracker["passed"].append({aid})
        cadtest_results_tracker["categories"][{cat}]["passed"].append({aid})
    except Exception:
        cadtest_results_tracker["failed"].append({aid})
        cadtest_results_tracker["categories"][{cat}]["failed"].append({aid})
"""
        )

    return "".join(parts)


class CADTestMetric(EvaluationMetric):
    """Run pre-classified cadtests against a generated CadQuery model."""

    def __init__(
        self,
        dataset: Optional[str] = None,
        partition: Optional[str] = None,
        generated_code_subdir: str = "generated_code",
        code_filename_prefix: str = "gpt_generated",
        legacy_code_filename: str = "gpt_generated.py",
        strict_generated_code: bool = False,
    ):
        super().__init__("cadtest")
        self.dataset = dataset
        self.partition = partition
        self.generated_code_subdir = generated_code_subdir
        self.code_filename_prefix = code_filename_prefix
        self.legacy_code_filename = legacy_code_filename
        self.strict_generated_code = strict_generated_code
        self._source: Optional[HFDatasetSource] = None

    def _get_source(self) -> HFDatasetSource:
        if self._source is None:
            if not self.dataset:
                raise ValueError(
                    "CADTestMetric requires 'dataset' (local Parquet root such as "
                    "'data/hf' or a HF Hub repo id like 'your-org/CADTestBench')."
                )
            if not self.partition:
                raise ValueError(
                    "CADTestMetric requires 'partition' ('abstract' or 'detailed')."
                )
            self._source = HFDatasetSource(self.dataset, self.partition)
        return self._source

    def compute_sample_metric(self, sample_data: SampleData) -> MetricResult:
        try:
            bundle_doc = self._get_source().bundle_for(sample_data.sample_id)
            cadtests: List[Dict[str, Any]] = list(bundle_doc.get("cadtests") or [])
            source_groups = _bundle_requirement_groups(bundle_doc)
        except Exception as e:
            return self._fail_sample(
                sample_data.sample_id,
                cadtests=[],
                error_reason=(
                    f"failed to load cadtest bundle for {sample_data.sample_id!r} "
                    f"from {self.dataset!r} / {self.partition!r}: "
                    f"{type(e).__name__}: {e}"
                ),
                error_kind="cadtests_load_error",
            )

        if not cadtests:
            return self._fail_sample(
                sample_data.sample_id,
                cadtests=[],
                error_reason=(
                    f"no cadtests found for sample {sample_data.sample_id!r} in "
                    f"{self.dataset!r} ({self.partition!r})"
                ),
                error_kind="cadtests_empty",
            )

        try:
            model_code_path = _resolve_model_code_path(
                sample_data=sample_data,
                generated_code_subdir=self.generated_code_subdir,
                code_filename_prefix=self.code_filename_prefix,
                legacy_code_filename=self.legacy_code_filename,
                strict_generated_code=self.strict_generated_code,
            )
            with open(model_code_path, "r") as f:
                model_code = f.read()
        except Exception as e:
            return self._fail_sample(
                sample_data.sample_id,
                cadtests=cadtests,
                error_reason=f"could not load model code: {type(e).__name__}: {e}",
                error_kind="model_load_error",
                benchmark_groups=source_groups,
            )

        export_stl: Optional[Path] = None
        if sample_data.eval_sample_dir is not None:
            export_stl = Path(sample_data.eval_sample_dir) / eval_sample_stl_filename

        run = _run_cadtest_block(
            cadtests,
            model_source=model_code,
            execution_cwd=model_code_path.parent,
            model_file_path=model_code_path,
            export_stl_path=export_stl,
        )

        replay_dir = sample_data.eval_sample_dir or sample_data.sample_folder_path
        replay_script = create_code_cadtest_block(model_code, cadtests)
        replay_dir.mkdir(parents=True, exist_ok=True)
        with open(replay_dir / "code_with_cadtests.py", "w") as f:
            f.write(replay_script)

        cadtest_entries: List[Dict[str, Any]] = run["cadtests"]
        passed_ids = {
            entry["id"] for entry in cadtest_entries if entry["status"] == "pass"
        }
        all_ids = {_normalize_cadtest_id(_row_id(row)) for row in cadtests}

        rs_result = _compute_rs_scoring(
            cadtests,
            passed_ids,
            all_ids,
            requirement_groups=source_groups,
        )

        summary = self._build_summary(
            cadtest_entries,
            model_compile_error=run["model_compile_error"],
            evaluation_error=None,
            rs_result=rs_result,
            execution_stdout=run.get("execution_stdout") or "",
        )

        meta: Dict[str, Any] = {
            "summary": summary,
            "cadtests": cadtest_entries,
            "rs_groups": rs_result.get("groups", []),
        }
        if run["model_compile_error"]:
            meta["model_error"] = run["model_error"]
        err = run.get("stl_export_error")
        if err:
            meta["stl_export_error"] = err

        value = summary["pass_rate"]
        return MetricResult(self.name, sample_data.sample_id, value, meta, True)

    def _fail_sample(
        self,
        sample_id: str,
        cadtests: List[Dict[str, Any]],
        error_reason: str,
        error_kind: str,
        benchmark_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> MetricResult:
        cadtest_entries = [
            _build_cadtest_entry(
                row,
                status="fail",
                message=error_reason,
                exception=error_kind,
            )
            for row in cadtests
        ]

        if cadtests:
            all_ids = {_normalize_cadtest_id(_row_id(row)) for row in cadtests}
            rs_result = _compute_rs_scoring(
                cadtests,
                passed_ids=set(),
                filtered_cadtest_ids=all_ids,
                requirement_groups=benchmark_groups,
            )
        else:
            rs_result = {
                "available": False,
                "groups": [],
                "groups_total": 0,
                "groups_passed": 0,
                "rs": 0.0,
            }

        summary = self._build_summary(
            cadtest_entries,
            model_compile_error=error_kind == "model_load_error",
            evaluation_error=error_kind,
            rs_result=rs_result,
        )

        meta: Dict[str, Any] = {
            "summary": summary,
            "cadtests": cadtest_entries,
            "rs_groups": rs_result.get("groups", []),
            "model_error": error_reason if error_kind == "model_load_error" else None,
            "evaluation_error_reason": error_reason,
        }

        return MetricResult(
            self.name,
            sample_id,
            0.0,
            meta,
            success=False,
            error_message=error_reason,
        )

    @staticmethod
    def _build_summary(
        cadtest_entries: List[Dict[str, Any]],
        model_compile_error: bool,
        evaluation_error: Optional[str],
        rs_result: Dict[str, Any],
        execution_stdout: str = "",
    ) -> Dict[str, Any]:
        total = len(cadtest_entries)
        passed = sum(1 for e in cadtest_entries if e["status"] == "pass")
        failed = total - passed

        category_breakdown: Dict[str, Dict[str, int]] = {}
        for entry in cadtest_entries:
            cat = entry.get("category") or "uncategorized"
            bucket = category_breakdown.setdefault(cat, {"passed": 0, "total": 0})
            bucket["total"] += 1
            if entry["status"] == "pass":
                bucket["passed"] += 1

        out: Dict[str, Any] = {
            "total_cadtests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100.0) if total > 0 else 0.0,
            "model_compile_error": model_compile_error,
            "evaluation_error": evaluation_error,
            "category_breakdown": category_breakdown,
            "rs": rs_result.get("rs", 0.0),
            "rs_groups": {
                "passed": rs_result.get("groups_passed", 0),
                "total": rs_result.get("groups_total", 0),
            },
        }
        if execution_stdout:
            out["execution_stdout"] = execution_stdout
        return out

    def aggregate_results(self, results: List[MetricResult]) -> Dict[str, Any]:
        total_samples = len(results)
        total_tests = 0
        total_passed = 0
        total_failed = 0
        invalid_samples = 0
        samples_passed_all = 0
        category_stats: Dict[str, Dict[str, int]] = {}
        per_sample_rs: List[float] = []

        for res in results:
            if res.metadata is None:
                raise RuntimeError(
                    f"Sample '{res.sample_id}' has no metadata -- metric was not computed."
                )
            summary = res.metadata.get("summary", {})

            n_total = summary.get("total_cadtests", 0)
            n_passed = summary.get("passed", 0)
            n_failed = summary.get("failed", 0)
            total_tests += n_total
            total_passed += n_passed
            total_failed += n_failed

            eval_error = summary.get("evaluation_error")
            if summary.get("model_compile_error") or eval_error:
                invalid_samples += 1
            elif n_total > 0 and n_passed == n_total:
                samples_passed_all += 1

            for cat, counts in summary.get("category_breakdown", {}).items():
                bucket = category_stats.setdefault(
                    cat, {"passed": 0, "failed": 0, "total": 0}
                )
                cat_passed = counts.get("passed", 0)
                cat_total = counts.get("total", 0)
                bucket["passed"] += cat_passed
                bucket["failed"] += cat_total - cat_passed
                bucket["total"] += cat_total

            rs_groups = summary.get("rs_groups", {})
            if rs_groups.get("total", 0) > 0:
                per_sample_rs.append(summary.get("rs", 0.0))

        category_accuracy: Dict[str, Dict[str, float]] = {
            cat: {
                "passed": stats["passed"],
                "failed": stats["failed"],
                "total": stats["total"],
                "accuracy": (
                    stats["passed"] / stats["total"] * 100.0 if stats["total"] > 0 else 0.0
                ),
            }
            for cat, stats in category_stats.items()
        }

        avg_rs = (
            sum(per_sample_rs) / len(per_sample_rs)
            if per_sample_rs
            else 0.0
        )

        pr_pct = (
            samples_passed_all / total_samples * 100.0 if total_samples > 0 else 0.0
        )

        return {
            "total_samples": total_samples,
            "invalid_samples": invalid_samples,
            "invalid_sample_percentage": (
                invalid_samples / total_samples * 100.0 if total_samples > 0 else 0.0
            ),
            "samples_passed_all_cadtests": samples_passed_all,
            "pr": pr_pct,
            "total_cadtests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "rs": avg_rs,
            "category_accuracy": category_accuracy,
        }
