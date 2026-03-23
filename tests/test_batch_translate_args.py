from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cli.batch_translate_lib.args import parse_args


class ParseArgsTests(unittest.TestCase):
    def test_parse_basic_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()

            config = parse_args([str(input_dir), str(output_dir), "--recursive", "--dry-run", "--force"])

            self.assertEqual(config.input_dir, input_dir.resolve())
            self.assertEqual(config.output_dir, output_dir.resolve())
            self.assertTrue(config.recursive)
            self.assertTrue(config.dry_run)
            self.assertTrue(config.force)
            self.assertTrue(output_dir.exists())

    def test_reject_same_input_and_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir)

            with self.assertRaises(SystemExit):
                parse_args([str(path), str(path)])

    def test_reject_output_inside_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            input_dir = root / "input"
            output_dir = input_dir / "output"
            input_dir.mkdir(parents=True)

            with self.assertRaises(SystemExit):
                parse_args([str(input_dir), str(output_dir)])