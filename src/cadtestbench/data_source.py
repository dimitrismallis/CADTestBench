"""
HF/Parquet data source for CADTestBench.

A single ``HFDatasetSource`` abstracts whether a dataset string points at:

- a **local** Parquet root produced by ``scripts/benchmark_to_parquet.py`` -- the
  expected layout is ``<root>/{samples,cadtests}/<partition>.parquet``;
- a **HF Hub repo id** such as ``your-org/CADTestBench`` -- in which case
  ``datasets.load_dataset`` is used to resolve the configs/splits declared in
  the dataset card.

The same instance can be (cheaply) constructed by both the dataset loader and the
``cadtest`` metric: ``datasets`` caches per (source, revision), so loading the
two small partition tables is paid at most once per process.

The tables are joined in-memory into a per-sample bundle dict that matches the
shape of the on-disk ``cadtests.json`` consumed by ``CADTestMetric``::

    {
        "sample_id": "...",
        "requirement_groups": [{"requirement_id": ..., "cadtest_ids": [...], ...}, ...],
        "cadtests":           [{"cadtest_id": ..., "cadtest_code": ..., ...}, ...]
    }

The ``requirement_groups`` are reconstructed by grouping the ``cadtests`` rows
by ``requirement_id`` (in first-seen order); rows with a ``null``
``requirement_id`` are not part of any group.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_PARTITIONS = ("abstract", "detailed")
_TABLE_NAMES = ("samples", "cadtests")


def _import_datasets():
    try:
        import datasets  # noqa: F401
    except ImportError as e:
        raise SystemExit(
            "The 'datasets' package is required to load CADTestBench data.\n"
            "Install with: pip install datasets"
        ) from e
    return datasets


class HFDatasetSource:
    """Lazy reader for the two CADTestBench Parquet tables of one partition."""

    def __init__(self, source: str, partition: str):
        if not source:
            raise ValueError("HFDatasetSource requires a non-empty 'source'.")
        if partition not in VALID_PARTITIONS:
            raise ValueError(
                f"partition must be one of {VALID_PARTITIONS}, got {partition!r}"
            )

        self.source: str = str(source)
        self.partition: str = partition
        self._is_local: bool = self._looks_local(self.source)

        self._tables: Dict[str, List[Dict[str, Any]]] = {}
        self._sample_index: Optional[Dict[str, Dict[str, Any]]] = None
        self._cadtests_index: Optional[Dict[str, List[Dict[str, Any]]]] = None

    @staticmethod
    def _looks_local(source: str) -> bool:
        """A source is treated as local if it resolves to an existing directory."""
        try:
            return Path(source).expanduser().is_dir()
        except OSError:
            return False

    @property
    def is_local(self) -> bool:
        return self._is_local

    def _load_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Load one Parquet table for ``self.partition`` and cache it."""
        if table_name in self._tables:
            return self._tables[table_name]
        if table_name not in _TABLE_NAMES:
            raise ValueError(
                f"unknown table {table_name!r}; expected one of {_TABLE_NAMES}"
            )

        datasets = _import_datasets()

        if self._is_local:
            local_path = (
                Path(self.source).expanduser() / table_name / f"{self.partition}.parquet"
            )
            if not local_path.is_file():
                raise FileNotFoundError(
                    f"Missing parquet file for table {table_name!r} / partition "
                    f"{self.partition!r}: {local_path}"
                )
            ds = datasets.Dataset.from_parquet(str(local_path))
        else:
            ds = datasets.load_dataset(
                self.source, name=table_name, split=self.partition
            )

        rows = ds.to_list()
        self._tables[table_name] = rows
        return rows

    def _build_sample_index(self) -> Dict[str, Dict[str, Any]]:
        if self._sample_index is None:
            self._sample_index = {
                row["sample_id"]: row for row in self._load_table("samples")
            }
        return self._sample_index

    def _build_cadtests_index(self) -> Dict[str, List[Dict[str, Any]]]:
        if self._cadtests_index is None:
            idx: Dict[str, List[Dict[str, Any]]] = {}
            for row in self._load_table("cadtests"):
                idx.setdefault(row["sample_id"], []).append(row)
            for sid, rows in idx.items():
                rows.sort(
                    key=lambda r: (r.get("cadtest_id") if r.get("cadtest_id") is not None else 0)
                )
            self._cadtests_index = idx
        return self._cadtests_index

    def sample_ids(self) -> List[str]:
        """All sample ids in this partition, lexicographically sorted."""
        return sorted(self._build_sample_index().keys())

    def __len__(self) -> int:
        return len(self._build_sample_index())

    def __contains__(self, sample_id: object) -> bool:
        return isinstance(sample_id, str) and sample_id in self._build_sample_index()

    def prompt_for(self, sample_id: str) -> str:
        index = self._build_sample_index()
        if sample_id not in index:
            raise KeyError(
                f"sample {sample_id!r} not found in dataset {self.source!r} "
                f"(partition {self.partition!r})"
            )
        return index[sample_id].get("prompt") or ""

    def bundle_for(self, sample_id: str) -> Dict[str, Any]:
        """Reconstruct the legacy ``cadtests.json``-shaped bundle for one sample.

        ``requirement_groups`` are derived by grouping the cadtests rows on
        ``requirement_id`` (in first-seen order); rows with a ``null``
        requirement are skipped.
        """
        if sample_id not in self._build_sample_index():
            raise KeyError(
                f"sample {sample_id!r} not found in dataset {self.source!r} "
                f"(partition {self.partition!r})"
            )

        cadtests_rows = self._build_cadtests_index().get(sample_id, [])

        cadtests: List[Dict[str, Any]] = []
        groups_by_rid: Dict[Any, Dict[str, Any]] = {}
        group_order: List[Any] = []

        for row in cadtests_rows:
            cid = row.get("cadtest_id")
            req_id = row.get("requirement_id")
            req_type = row.get("requirement_type")
            req_desc = row.get("requirement_description")

            cadtests.append(
                {
                    "cadtest_id": cid,
                    "cadtest_description": row.get("cadtest_description") or "",
                    "cadtest_code": row.get("cadtest_code") or "",
                    "cadtest_type": row.get("cadtest_type") or "uncategorized",
                    "classification_reasoning": row.get("classification_reasoning") or "",
                    "prompt_justification": row.get("prompt_justification") or "",
                    "requirement_id": req_id,
                    "requirement_type": req_type,
                    "requirement_description": req_desc,
                }
            )

            if req_id is None:
                continue
            group = groups_by_rid.get(req_id)
            if group is None:
                group = {
                    "requirement_id": req_id,
                    "requirement_type": req_type,
                    "requirement_description": req_desc,
                    "cadtest_ids": [],
                }
                groups_by_rid[req_id] = group
                group_order.append(req_id)
            group["cadtest_ids"].append(cid)

        requirement_groups = [groups_by_rid[rid] for rid in group_order]

        return {
            "sample_id": sample_id,
            "requirement_groups": requirement_groups,
            "cadtests": cadtests,
        }
