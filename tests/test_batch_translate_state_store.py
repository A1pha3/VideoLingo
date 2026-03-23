from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cli.batch_translate_lib.state_store import StateStore


class StateStoreTests(unittest.TestCase):
    def test_mark_success_and_reload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "status.json"
            store = StateStore(state_path)
            fingerprint = {"size": 123, "mtime": 456}

            store.mark_success("sample.mp4", fingerprint, "sample_dub.mp4")

            reloaded = StateStore(state_path)
            job = reloaded.get_job("sample.mp4")
            self.assertIsNotNone(job)
            self.assertEqual(job["status"], "success")
            self.assertEqual(job["fingerprint"], fingerprint)
            self.assertEqual(job["output_file"], "sample_dub.mp4")

    def test_should_skip_requires_success_fingerprint_and_real_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            state_path = root / "status.json"
            output_file = root / "sample_dub.mp4"
            fingerprint = {"size": 111, "mtime": 222}
            store = StateStore(state_path)

            store.mark_success("sample.mp4", fingerprint, output_file.name)

            self.assertFalse(store.should_skip("sample.mp4", fingerprint, output_file, force=False))

            output_file.write_bytes(b"video")
            self.assertTrue(store.should_skip("sample.mp4", fingerprint, output_file, force=False))
            self.assertFalse(store.should_skip("sample.mp4", fingerprint, output_file, force=True))

    def test_state_file_is_valid_json_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "status.json"
            store = StateStore(state_path)
            store.mark_failed("sample.mp4", {"size": 1, "mtime": 2}, "translate", "boom")

            content = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("jobs", content)
            self.assertEqual(content["jobs"]["sample.mp4"]["status"], "failed")