from __future__ import annotations

import unittest
from unittest.mock import patch

from cli.batch_translate_lib.preflight import validate_runtime_requirements


class PreflightTests(unittest.TestCase):
    def test_accepts_local_whisper_and_edge_tts_with_api_key(self) -> None:
        values = {
            "api.key": "demo-key",
            "whisper.runtime": "local",
            "tts_method": "edge_tts",
        }

        with patch("cli.batch_translate_lib.preflight.load_key", side_effect=values.__getitem__):
            validate_runtime_requirements()

    def test_rejects_missing_api_key(self) -> None:
        values = {
            "api.key": "",
            "whisper.runtime": "local",
            "tts_method": "edge_tts",
        }

        with patch("cli.batch_translate_lib.preflight.load_key", side_effect=values.__getitem__):
            with self.assertRaisesRegex(RuntimeError, "api.key"):
                validate_runtime_requirements()

    def test_requires_cloud_whisper_api_key(self) -> None:
        values = {
            "api.key": "demo-key",
            "whisper.runtime": "cloud",
            "whisper.whisperX_302_api_key": "",
            "tts_method": "edge_tts",
        }

        with patch("cli.batch_translate_lib.preflight.load_key", side_effect=values.__getitem__):
            with self.assertRaisesRegex(RuntimeError, "whisper.whisperX_302_api_key"):
                validate_runtime_requirements()

    def test_requires_tts_api_key_for_openai_tts(self) -> None:
        values = {
            "api.key": "demo-key",
            "whisper.runtime": "local",
            "tts_method": "openai_tts",
            "openai_tts.api_key": "",
        }

        with patch("cli.batch_translate_lib.preflight.load_key", side_effect=values.__getitem__):
            with self.assertRaisesRegex(RuntimeError, "openai_tts.api_key"):
                validate_runtime_requirements()