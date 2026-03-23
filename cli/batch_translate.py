from __future__ import annotations

import os
import sys

from cli.batch_translate_lib.args import parse_args


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)

    # Import heavy runtime modules only after argument parsing so --help stays fast and quiet.
    from cli.batch_translate_lib.lockfile import ProcessLock
    from cli.batch_translate_lib.paths import RuntimePaths, ensure_runtime_paths
    from cli.batch_translate_lib.preflight import validate_runtime_requirements
    from cli.batch_translate_lib.reporter import Reporter
    from cli.batch_translate_lib.scanner import scan_tasks
    from cli.batch_translate_lib.state_store import StateStore

    os.chdir(config.repo_root)

    runtime_paths: RuntimePaths = ensure_runtime_paths(config.repo_root)
    state_store = StateStore(config.output_dir / "batch_translate_status.json")
    reporter = Reporter(config, config.output_dir / "batch_translate_report.json")

    try:
        with ProcessLock(runtime_paths.lock_file):
            scan_result = scan_tasks(config, state_store)
            reporter.print_start_summary(scan_result)

            if config.dry_run:
                reporter.finish(scan_result, succeeded=0, failed_jobs=[])
                return 0

            if scan_result.total_detected == 0:
                reporter.print_no_videos()
                reporter.finish(scan_result, succeeded=0, failed_jobs=[])
                return 2

            validate_runtime_requirements()

            from cli.batch_translate_lib.runner import run_task

            failed_jobs: list[dict[str, str]] = []
            succeeded = 0

            for task in scan_result.planned_tasks:
                reporter.print_task_start(task)
                task_result = run_task(task, config, runtime_paths, state_store)
                if task_result.success:
                    succeeded += 1
                    reporter.print_task_success(task_result)
                else:
                    failed_jobs.append(
                        {
                            "file": task.name,
                            "step": task_result.error_step or "unknown",
                            "message": task_result.error_message or "unknown error",
                        }
                    )
                    reporter.print_task_failure(task_result)

            reporter.finish(scan_result, succeeded=succeeded, failed_jobs=failed_jobs)

            if failed_jobs:
                return 1

            return 0
    except RuntimeError as exc:
        reporter.print_runtime_error(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
