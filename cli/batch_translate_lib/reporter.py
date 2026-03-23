from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from cli.batch_translate_lib.args import CLIConfig
from cli.batch_translate_lib.scanner import ScanResult, Task


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Reporter:
    def __init__(self, config: CLIConfig, report_path: Path):
        self.config = config
        self.report_path = report_path
        self.started_at = _utc_now()

    def print_start_summary(self, scan_result: ScanResult) -> None:
        print(f"Input Dir: {self.config.input_dir}")
        print(f"Output Dir: {self.config.output_dir}")
        print(f"Recursive: {self.config.recursive}")
        print(f"Detected Videos: {scan_result.total_detected}")
        print(f"Will Run: {len(scan_result.planned_tasks)}")
        print(f"Will Skip: {scan_result.skipped_count}")

    def print_no_videos(self) -> None:
        print("No input videos found. Nothing to do.")

    def print_runtime_error(self, message: str) -> None:
        print(f"Error: {message}")

    def print_task_start(self, task: Task) -> None:
        print(f"Processing: {task.name}")

    def print_task_success(self, task_result) -> None:
        print(f"Succeeded: {task_result.task.name} -> {task_result.output_path}")

    def print_task_failure(self, task_result) -> None:
        print(
            f"Failed: {task_result.task.name} | "
            f"step={task_result.error_step} | message={task_result.error_message}"
        )

    def finish(self, scan_result: ScanResult, succeeded: int, failed_jobs: list[dict[str, str]]) -> None:
        finished_at = _utc_now()
        report = {
            "started_at": self.started_at,
            "finished_at": finished_at,
            "input_dir": str(self.config.input_dir),
            "output_dir": str(self.config.output_dir),
            "recursive": self.config.recursive,
            "total_detected": scan_result.total_detected,
            "planned": len(scan_result.planned_tasks),
            "skipped": scan_result.skipped_count,
            "succeeded": succeeded,
            "failed": len(failed_jobs),
            "failed_jobs": failed_jobs,
        }
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.report_path.with_suffix(self.report_path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(self.report_path)

        print(f"Processed: {len(scan_result.planned_tasks)}")
        print(f"Succeeded: {succeeded}")
        print(f"Failed: {len(failed_jobs)}")
        print(f"Skipped: {scan_result.skipped_count}")
        print(f"Report: {self.report_path}")
