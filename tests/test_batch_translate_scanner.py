from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.batch_translate_lib.args import CLIConfig
from cli.batch_translate_lib.scanner import scan_tasks
from cli.batch_translate_lib.state_store import StateStore


class ScannerTests(unittest.TestCase):
    def test_scan_tasks_plans_supported_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            output_dir.mkdir()
            (input_dir / "a.mp4").write_bytes(b"1")
            (input_dir / "b.txt").write_text("ignore", encoding="utf-8")

            config = CLIConfig(
                input_dir=input_dir,
                output_dir=output_dir,
                recursive=False,
                dry_run=False,
                force=False,
                repo_root=root,
            )
            state_store = StateStore(output_dir / "status.json")

            with patch("cli.batch_translate_lib.scanner.load_key", return_value=["mp4", "mkv"]):
                result = scan_tasks(config, state_store)

            self.assertEqual(result.total_detected, 1)
            self.assertEqual(result.skipped_count, 0)
            self.assertEqual(len(result.planned_tasks), 1)
            self.assertEqual(result.planned_tasks[0].name, "a.mp4")
            self.assertEqual(result.planned_tasks[0].output_path.name, "a_dub.mp4")

    def test_scan_tasks_skips_successful_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            output_dir.mkdir()
            video_path = input_dir / "a.mp4"
            video_path.write_bytes(b"123")
            output_file = output_dir / "a_dub.mp4"
            output_file.write_bytes(b"dub")

            config = CLIConfig(
                input_dir=input_dir,
                output_dir=output_dir,
                recursive=False,
                dry_run=False,
                force=False,
                repo_root=root,
            )
            state_store = StateStore(output_dir / "status.json")
            fingerprint = {"size": int(video_path.stat().st_size), "mtime": int(video_path.stat().st_mtime)}
            state_store.mark_success("a.mp4", fingerprint, output_file.name)

            with patch("cli.batch_translate_lib.scanner.load_key", return_value=["mp4"]):
                result = scan_tasks(config, state_store)

            self.assertEqual(result.total_detected, 1)
            self.assertEqual(result.skipped_count, 1)
            self.assertEqual(len(result.planned_tasks), 0)

    def test_scan_tasks_rejects_duplicate_basenames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output"
            (input_dir / "d1").mkdir(parents=True)
            (input_dir / "d2").mkdir(parents=True)
            output_dir.mkdir()
            (input_dir / "d1" / "same.mp4").write_bytes(b"1")
            (input_dir / "d2" / "same.mp4").write_bytes(b"2")

            config = CLIConfig(
                input_dir=input_dir,
                output_dir=output_dir,
                recursive=True,
                dry_run=False,
                force=False,
                repo_root=root,
            )
            state_store = StateStore(output_dir / "status.json")

            with patch("cli.batch_translate_lib.scanner.load_key", return_value=["mp4"]):
                with self.assertRaises(RuntimeError):
                    scan_tasks(config, state_store)