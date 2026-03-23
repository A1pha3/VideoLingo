from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli.batch_translate_lib.lockfile import ProcessLock


class ProcessLockTests(unittest.TestCase):
    def test_creates_and_releases_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            lock_path = Path(tmp_dir) / "batch_translate.lock"

            with ProcessLock(lock_path):
                self.assertTrue(lock_path.exists())

            self.assertFalse(lock_path.exists())

    def test_rejects_live_lock_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            lock_path = Path(tmp_dir) / "batch_translate.lock"
            lock_path.write_text("4321", encoding="utf-8")

            with patch("cli.batch_translate_lib.lockfile.os.kill") as mock_kill:
                mock_kill.return_value = None
                with self.assertRaisesRegex(RuntimeError, "already running"):
                    with ProcessLock(lock_path):
                        pass

    def test_recovers_stale_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            lock_path = Path(tmp_dir) / "batch_translate.lock"
            lock_path.write_text("4321", encoding="utf-8")

            with patch(
                "cli.batch_translate_lib.lockfile.os.kill",
                side_effect=ProcessLookupError,
            ):
                with ProcessLock(lock_path):
                    self.assertTrue(lock_path.exists())