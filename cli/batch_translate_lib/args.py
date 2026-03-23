from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CLIConfig:
    input_dir: Path
    output_dir: Path
    recursive: bool
    dry_run: bool
    force: bool
    repo_root: Path


def parse_args(argv: list[str] | None = None) -> CLIConfig:
    parser = argparse.ArgumentParser(
        prog="python -m cli.batch_translate",
        description="Batch translate and dub videos from an input directory into an output directory.",
    )
    parser.add_argument("input_dir", help="Directory that contains input videos")
    parser.add_argument("output_dir", help="Directory for final dubbed videos and state files")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan nested directories for input videos",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only scan and print the execution plan without processing videos",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run tasks even if they are already marked as successful",
    )

    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        parser.error(f"input_dir does not exist or is not a directory: {input_dir}")

    if input_dir == output_dir:
        parser.error("input_dir and output_dir must be different directories")

    try:
        output_dir.relative_to(input_dir)
        parser.error("output_dir cannot be inside input_dir")
    except ValueError:
        pass

    output_dir.mkdir(parents=True, exist_ok=True)

    return CLIConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        recursive=bool(args.recursive),
        dry_run=bool(args.dry_run),
        force=bool(args.force),
        repo_root=repo_root,
    )
