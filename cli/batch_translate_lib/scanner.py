from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cli.batch_translate_lib.args import CLIConfig
from cli.batch_translate_lib.state_store import StateStore
from core.utils import load_key


@dataclass(frozen=True)
class Task:
    name: str
    input_path: Path
    output_path: Path
    fingerprint: dict[str, int]


@dataclass(frozen=True)
class ScanResult:
    total_detected: int
    skipped_count: int
    planned_tasks: list[Task]


def _fingerprint(path: Path) -> dict[str, int]:
    stat = path.stat()
    return {"size": int(stat.st_size), "mtime": int(stat.st_mtime)}


def scan_tasks(config: CLIConfig, state_store: StateStore) -> ScanResult:
    allowed_formats = {ext.lower() for ext in load_key("allowed_video_formats")}
    pattern = "**/*" if config.recursive else "*"
    candidates = [
        path
        for path in sorted(config.input_dir.glob(pattern))
        if path.is_file() and path.suffix.lower().lstrip(".") in allowed_formats
    ]

    seen_names: set[str] = set()
    planned: list[Task] = []
    skipped_count = 0

    for path in candidates:
        if path.name in seen_names:
            raise RuntimeError(
                f"Duplicate input filename detected across directories: {path.name}. "
                "V1 requires unique basenames."
            )
        seen_names.add(path.name)

        fingerprint = _fingerprint(path)
        output_name = f"{path.stem}_dub.mp4"
        output_path = config.output_dir / output_name

        if state_store.should_skip(path.name, fingerprint, output_path, config.force):
            skipped_count += 1
            continue

        planned.append(
            Task(
                name=path.name,
                input_path=path,
                output_path=output_path,
                fingerprint=fingerprint,
            )
        )

    return ScanResult(
        total_detected=len(candidates),
        skipped_count=skipped_count,
        planned_tasks=planned,
    )
