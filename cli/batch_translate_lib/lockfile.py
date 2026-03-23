from __future__ import annotations

import os
from pathlib import Path


class ProcessLock:
    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.fd: int | None = None

    def _read_pid(self) -> int | None:
        try:
            raw = self.lock_file.read_text(encoding="utf-8").strip()
        except OSError:
            return None

        if not raw:
            return None

        try:
            return int(raw)
        except ValueError:
            return None

    def _pid_is_running(self, pid: int) -> bool:
        if pid <= 0:
            return False

        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True

        return True

    def _clear_stale_lock(self) -> None:
        pid = self._read_pid()
        if pid is not None and self._pid_is_running(pid):
            raise RuntimeError(
                f"Another batch_translate process is already running: {self.lock_file}"
            )

        try:
            self.lock_file.unlink(missing_ok=True)
        except OSError as exc:
            raise RuntimeError(f"Unable to recover stale lock: {self.lock_file}") from exc

    def __enter__(self) -> "ProcessLock":
        for _attempt in range(2):
            try:
                self.fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, str(os.getpid()).encode("utf-8"))
                os.fsync(self.fd)
                return self
            except FileExistsError:
                self._clear_stale_lock()

        raise RuntimeError(f"Unable to acquire process lock: {self.lock_file}")

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        try:
            self.lock_file.unlink(missing_ok=True)
        except OSError:
            pass
