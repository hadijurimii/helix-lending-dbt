from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelinePaths:
    project_root: Path
    data_dir: Path
    output_dir: Path
    parquet_dir: Path
    metrics_dir: Path
    database_path: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "PipelinePaths":
        output_dir = project_root / "output"
        return cls(
            project_root=project_root,
            data_dir=project_root / "data",
            output_dir=output_dir,
            parquet_dir=output_dir / "parquet",
            metrics_dir=output_dir / "metrics",
            database_path=output_dir / "helix_lending.duckdb",
        )

    def create_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
