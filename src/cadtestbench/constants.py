"""Filesystem constants shared across CADTestBench."""
from __future__ import annotations

from pathlib import Path

generated_models_dir = "generated_models"

eval_samples_subdir = "samples"
eval_sample_summary_filename = "summary.json"
eval_sample_stl_filename = "generated.stl"

config_filename = "config.json"
summary_filename = "evaluation_summary.json"

eval_root_dir = "eval"


def project_root() -> Path:
    """Return the CADTestBench project root.

    Walks up from this file until a directory containing ``pyproject.toml`` is
    found. Falls back to the current working directory if no such marker is
    found (e.g. when the package is installed without source).
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()
