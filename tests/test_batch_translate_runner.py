from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.batch_translate_lib.args import CLIConfig
from cli.batch_translate_lib.paths import ensure_runtime_paths
from cli.batch_translate_lib.runner import run_task
from cli.batch_translate_lib.scanner import Task
from cli.batch_translate_lib.state_store import StateStore


class RunnerTests(unittest.TestCase):
    def test_run_task_marks_success_and_copies_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output_final"
            batch_output_dir = root / "batch" / "output" / "sample"
            input_dir.mkdir(parents=True)
            output_dir.mkdir(parents=True)
            batch_output_dir.mkdir(parents=True)

            input_file = input_dir / "sample.mp4"
            input_file.write_bytes(b"input")
            archived_output = batch_output_dir / "output_dub.mp4"
            archived_output.write_bytes(b"dubbed-video")

            config = CLIConfig(
                input_dir=input_dir,
                output_dir=output_dir,
                recursive=False,
                dry_run=False,
                force=False,
                repo_root=root,
            )
            runtime_paths = ensure_runtime_paths(root)
            state_store = StateStore(output_dir / "batch_translate_status.json")
            task = Task(
                name="sample.mp4",
                input_path=input_file,
                output_path=output_dir / "sample_dub.mp4",
                fingerprint={"size": int(input_file.stat().st_size), "mtime": int(input_file.stat().st_mtime)},
            )

            with patch("cli.batch_translate_lib.runner.process_video", return_value=(True, "", "")):
                result = run_task(task, config, runtime_paths, state_store)

            self.assertTrue(result.success)
            self.assertEqual(task.output_path.read_bytes(), b"dubbed-video")
            self.assertEqual(state_store.get_job(task.name)["status"], "success")

    def test_run_task_marks_failed_when_process_video_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output_final"
            input_dir.mkdir(parents=True)
            output_dir.mkdir(parents=True)

            input_file = input_dir / "sample.mp4"
            input_file.write_bytes(b"input")

            config = CLIConfig(
                input_dir=input_dir,
                output_dir=output_dir,
                recursive=False,
                dry_run=False,
                force=False,
                repo_root=root,
            )
            runtime_paths = ensure_runtime_paths(root)
            state_store = StateStore(output_dir / "batch_translate_status.json")
            task = Task(
                name="sample.mp4",
                input_path=input_file,
                output_path=output_dir / "sample_dub.mp4",
                fingerprint={"size": int(input_file.stat().st_size), "mtime": int(input_file.stat().st_mtime)},
            )

            with patch(
                "cli.batch_translate_lib.runner.process_video",
                return_value=(False, "🗣️ Generating audio", "tts api timeout"),
            ):
                result = run_task(task, config, runtime_paths, state_store)

            self.assertFalse(result.success)
            self.assertEqual(result.error_step, "generate_audio")
            self.assertEqual(state_store.get_job(task.name)["status"], "failed")
            self.assertFalse(task.output_path.exists())