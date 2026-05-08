"""
Loader for the CADTestBench benchmark.

Loads samples from the published Parquet dataset (local ``data/hf/`` layout
or a HF Hub repo id), resolved through :class:`HFDatasetSource`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional

from ..data_source import HFDatasetSource


@dataclass
class CADTestBenchSample:
    """One CADTestBench sample (id + prompt). The cadtest bundle lives in the
    dataset and is fetched by :class:`CADTestMetric` directly."""

    sample_id: str
    prompt_text: str


class CADTestBenchLoader:
    """Iterate samples in a CADTestBench partition (HF Parquet-backed)."""

    def __init__(self, source: str, partition: str):
        self.source: str = str(source)
        self.partition: str = partition
        self._hf = HFDatasetSource(self.source, self.partition)
        self._samples_cache: Dict[str, CADTestBenchSample] = {}

    @property
    def dataset(self) -> str:
        """Dataset source string (local path or HF Hub repo id)."""
        return self.source

    def get_sample_ids(self) -> List[str]:
        return self._hf.sample_ids()

    def load_sample(self, sample_id: str) -> CADTestBenchSample:
        if sample_id in self._samples_cache:
            return self._samples_cache[sample_id]

        sample = CADTestBenchSample(
            sample_id=sample_id,
            prompt_text=self._hf.prompt_for(sample_id),
        )
        self._samples_cache[sample_id] = sample
        return sample

    def load_samples(
        self,
        sample_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[CADTestBenchSample]:
        ids = list(sample_ids) if sample_ids is not None else self.get_sample_ids()
        if limit is not None:
            ids = ids[:limit]

        out: List[CADTestBenchSample] = []
        for sid in ids:
            try:
                out.append(self.load_sample(sid))
            except (KeyError, ValueError) as e:
                print(f"Warning: Failed to load sample {sid}: {e}")
        return out

    def __iter__(self) -> Iterator[CADTestBenchSample]:
        for sid in self.get_sample_ids():
            try:
                yield self.load_sample(sid)
            except (KeyError, ValueError) as e:
                print(f"Warning: Failed to load sample {sid}: {e}")

    def __len__(self) -> int:
        return len(self.get_sample_ids())
