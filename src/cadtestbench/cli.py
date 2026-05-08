"""Command-line entry point for CADTestBench evaluations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from .loaders import CADTestBenchLoader
from .runner import EvaluationRunner

_CADTEST_TOPLEVEL_KWARGS = (
    "code_filename_prefix",
    "legacy_code_filename",
    "generated_code_subdir",
    "strict_generated_code",
)

_DEFAULT_HUB_DATASET = "dimitrismallis/CADTestBench"


def _finalize_evaluate_paths(args: argparse.Namespace) -> argparse.Namespace:
    """Resolve positional baseline, ``eval_root``, and normalize ``generation_dir`` type."""
    merged = vars(args).copy()
    baseline = merged.get("baseline")
    if baseline is not None:
        merged["generation_dir"] = _resolve_local_path(baseline)

    er = merged.get("eval_root")
    if er is not None:
        merged["eval_root"] = _resolve_local_path(er)

    gen = merged.get("generation_dir")
    if gen is not None and not isinstance(gen, Path):
        merged["generation_dir"] = Path(gen)

    return argparse.Namespace(**merged)


def _resolve_local_path(raw: Any) -> Path:
    """Resolve a CLI path relative to the current working directory."""
    p = raw if isinstance(raw, Path) else Path(raw)
    if p.is_absolute():
        return p.expanduser().resolve()
    return (Path.cwd() / p).resolve()


def _resolve_dataset_source(raw: Any) -> str:
    """Resolve a dataset source string; relative local paths use ``cwd``; Hub ids pass through."""
    if isinstance(raw, Path):
        return str(raw.expanduser().resolve())
    s = str(raw)
    p = Path(s).expanduser()
    if p.is_absolute():
        return str(p.resolve())
    candidate = (Path.cwd() / p).resolve()
    if candidate.is_dir():
        return str(candidate)
    return s


def _normalize_evaluate_config(args: argparse.Namespace) -> argparse.Namespace:
    """Expand shorthand: ``dataset`` + ``partition`` -> default cadtest metric."""
    metrics = getattr(args, "metrics", None)
    dataset_raw = getattr(args, "dataset", None) or _DEFAULT_HUB_DATASET
    dataset = _resolve_dataset_source(dataset_raw)
    partition = getattr(args, "partition", None)

    if not metrics and dataset and partition:
        kwargs: Dict[str, Any] = {"dataset": dataset, "partition": partition}
        for k in _CADTEST_TOPLEVEL_KWARGS:
            if not hasattr(args, k):
                continue
            v = getattr(args, k)
            if k == "strict_generated_code":
                kwargs[k] = bool(v)
            elif v is not None:
                kwargs[k] = v
        args.metrics = [{"name": "cadtest", "kwargs": kwargs}]

    args.partition = partition
    args.dataset = dataset
    return args


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cadtestbench",
        description="CADTestBench: cadtest-based evaluation for CAD generations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cadtestbench evaluate baselines/.../Abstract --partition abstract
  cadtestbench evaluate /path/to/run/Detailed --partition detailed --dataset data/hf
  cadtestbench evaluate baselines/React/GPT-5.2/Detailed --partition detailed --limit 10
        """,
    )

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate pre-generated CAD models")
    eval_parser.add_argument(
        "baseline",
        nargs="?",
        type=Path,
        metavar="BASELINE_DIR",
        help=(
            "Run root containing generated_models/ (often …/Abstract or …/Detailed). "
        ),
    )
    eval_parser.add_argument(
        "--dataset",
        type=str,
        default=argparse.SUPPRESS,
        help=(
            "CADTestBench dataset source: local Parquet root (e.g. data/hf) "
            "or Hugging Face Hub repo id. Default when omitted: "
            f"{_DEFAULT_HUB_DATASET}."
        ),
    )
    eval_parser.add_argument(
        "--eval-root",
        type=Path,
        help="Top-level folder under which evaluation runs are logged.",
    )
    eval_parser.add_argument(
        "--partition",
        choices=("abstract", "detailed"),
        default=None,
        metavar="{abstract,detailed}",
        help="Benchmark partition: abstract or detailed (required).",
    )
    eval_parser.add_argument(
        "--run-label",
        dest="run_label",
        default=None,
        metavar="TEXT",
        help=(
            "Optional label for the eval run folder name . "
            "When set, folder names use this instead of inferring from baseline."
        ),
    )
    eval_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of samples to evaluate.",
    )
    eval_parser.add_argument(
        "--sample-ids",
        nargs="+",
        help="Specific sample IDs to evaluate.",
    )

    return parser


def _sanitize_stringify_config(cfg: argparse.Namespace) -> Dict[str, Any]:
    def convert(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: convert(v) for k, v in o.items()}
        if isinstance(o, list):
            return [convert(v) for v in o]
        if isinstance(o, Path):
            return str(o)
        return o

    d = vars(cfg).copy()
    d.pop("baseline", None)
    d.pop("config", None)
    d.pop("additional_eval_info", None)
    return convert(d)


def _validate_evaluate_args(args: argparse.Namespace) -> List[str]:
    missing = []
    if getattr(args, "partition", None) is None:
        missing.append("partition")
    if not getattr(args, "dataset", None):
        missing.append("dataset")
    if getattr(args, "generation_dir", None) is None:
        missing.append("generation_dir")
    if getattr(args, "partition", None) is not None and not getattr(args, "metrics", None):
        missing.append("metrics")
    return missing


def _run_evaluate(args: argparse.Namespace) -> int:
    """Run the evaluate subcommand. Returns 0 on success, non-zero only on
    operator/setup errors (missing config, missing generation dir, etc.).
    Per-sample metric failures are reported in the eval output, not via exit
    code."""
    missing = _validate_evaluate_args(args)
    if missing:
        labels = []
        for k in missing:
            if k == "generation_dir":
                labels.append("BASELINE_DIR")
            elif k == "partition":
                labels.append("--partition")
            else:
                labels.append(f"--{k.replace('_', '-')}")
        print(
            "Error: the following must be set (CLI or defaults): "
            + ", ".join(labels)
        )
        if "dataset" in missing:
            print(
                "       Pass --dataset with a local Parquet root (e.g. data/hf) "
                "or a HF Hub repo id (e.g. dimitrismallis/CADTestBench).",
                file=sys.stderr,
            )
        if "partition" in missing:
            print(
                "       Pass --partition abstract or --partition detailed.",
                file=sys.stderr,
            )
        return 1

    partition = args.partition

    dataset_loader = CADTestBenchLoader(args.dataset, partition)
    runner = EvaluationRunner(
        dataset_loader=dataset_loader,
        generation_dir=args.generation_dir,
        metrics=args.metrics,
        partition=partition,
        final_configs=_sanitize_stringify_config(args),
        eval_root=getattr(args, "eval_root", None),
        run_label=getattr(args, "run_label", None),
    )

    available = runner.get_available_samples()
    if not available:
        print(f"No generated models found in {args.generation_dir}/generated_models")
        return 1

    samples_to_evaluate = args.sample_ids
    if samples_to_evaluate:
        samples_to_evaluate = [sid for sid in samples_to_evaluate if sid in available]
        if not samples_to_evaluate:
            print("None of the requested sample_ids have generated models!")
            return 1

    _print_run_header(args, runner, available_count=len(available))

    summary = runner.evaluate_samples(
        sample_ids=samples_to_evaluate,
        limit=args.limit,
    )

    _print_run_summary(summary, runner)
    return 0


def _print_run_header(
    args: argparse.Namespace,
    runner: EvaluationRunner,
    available_count: int,
) -> None:
    print("=" * 72)
    print("CADTestBench Evaluation")
    print("-" * 72)
    print(f"  Generation dir : {args.generation_dir}")
    print(f"  Dataset        : {args.dataset}")
    print(f"  Partition      : {runner.partition}")
    print(f"  Run name       : {runner.run_name}")
    print(f"  Output dir     : {runner.output_dir}")
    print(f"  Models found   : {available_count}")
    metric_names = ", ".join(m.name for m in runner.metrics) or "(none)"
    print(f"  Metrics        : {metric_names}")
    print("=" * 72)


def _print_run_summary(summary: Dict[str, Any], runner: EvaluationRunner) -> None:
    stats = summary.get("statistics", {})
    aggregate = summary.get("aggregate_metrics", {}) or {}
    cadtest = aggregate.get("cadtest", {}) or {}

    total_samples = stats.get("total_samples", 0)
    invalid = cadtest.get("invalid_samples", 0)
    invalid_pct = cadtest.get("invalid_sample_percentage", 0.0)
    passed_all = cadtest.get("samples_passed_all_cadtests", 0)
    pr = cadtest.get("pr", 0.0)
    rs = cadtest.get("rs", 0.0)
    elapsed = stats.get("total_time_seconds", 0.0)

    print()
    print("=" * 72)
    print("Summary")
    print("-" * 72)
    print(f"  Samples evaluated      : {total_samples}")
    print(f"  Invalid (didn't run)   : {invalid} / {total_samples}  ({invalid_pct:.1f}%)")
    print(f"  PR (pass rate)         : {passed_all} / {total_samples}  ({pr:.1f}%)")
    print(f"  RS (avg)               : {rs:.2f}%")
    print(f"  Total time             : {elapsed:.2f}s")
    print(f"  Saved to               : {runner.output_dir}")
    print("=" * 72)


def main(argv: List[str] | None = None) -> int:
    parser = _create_argument_parser()
    args = parser.parse_args(argv)

    if not args.mode:
        parser.print_help()
        return 1

    if args.mode == "evaluate":
        try:
            args = _finalize_evaluate_paths(args)
            args = _normalize_evaluate_config(args)
            return _run_evaluate(args)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1

    print(f"Unknown mode: {args.mode}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
