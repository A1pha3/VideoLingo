from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    runtime_root: Path
    locks_dir: Path
    logs_dir: Path
    tmp_dir: Path
    lock_file: Path


def ensure_runtime_paths(repo_root: Path) -> RuntimePaths:
    runtime_root = repo_root / ".videolingo_cli"
    locks_dir = runtime_root / "locks"
    logs_dir = runtime_root / "logs"
    tmp_dir = runtime_root / "tmp"

    locks_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    return RuntimePaths(
        runtime_root=runtime_root,
        locks_dir=locks_dir,
        logs_dir=logs_dir,
        tmp_dir=tmp_dir,
        lock_file=locks_dir / "batch_translate.lock",
    )
