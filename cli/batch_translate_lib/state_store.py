from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class StateStore:
    def __init__(self, path: Path):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "jobs": {}}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(self.path)

    def get_job(self, name: str) -> dict[str, Any] | None:
        return self.data.setdefault("jobs", {}).get(name)

    def should_skip(self, name: str, fingerprint: dict[str, int], output_file: Path, force: bool) -> bool:
        if force:
            return False
        job = self.get_job(name)
        if not job:
            return False
        return (
            job.get("status") == "success"
            and job.get("fingerprint") == fingerprint
            and output_file.exists()
            and output_file.stat().st_size > 0
        )

    def mark_running(self, name: str, fingerprint: dict[str, int]) -> None:
        self.data.setdefault("jobs", {})[name] = {
            "status": "running",
            "fingerprint": fingerprint,
            "error_step": None,
            "error_message": None,
            "output_file": None,
            "updated_at": _utc_now(),
        }
        self._write()

    def mark_success(self, name: str, fingerprint: dict[str, int], output_file: str) -> None:
        self.data.setdefault("jobs", {})[name] = {
            "status": "success",
            "fingerprint": fingerprint,
            "error_step": None,
            "error_message": None,
            "output_file": output_file,
            "updated_at": _utc_now(),
        }
        self._write()

    def mark_failed(self, name: str, fingerprint: dict[str, int], error_step: str, error_message: str) -> None:
        self.data.setdefault("jobs", {})[name] = {
            "status": "failed",
            "fingerprint": fingerprint,
            "error_step": error_step,
            "error_message": error_message,
            "output_file": None,
            "updated_at": _utc_now(),
        }
        self._write()
