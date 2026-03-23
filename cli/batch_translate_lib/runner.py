from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from batch.utils.video_processor import process_video
from cli.batch_translate_lib.args import CLIConfig
from cli.batch_translate_lib.paths import RuntimePaths
from cli.batch_translate_lib.scanner import Task
from cli.batch_translate_lib.state_store import StateStore
from core.utils.onekeycleanup import sanitize_filename


@dataclass(frozen=True)
class TaskResult:
    task: Task
    success: bool
    output_path: Path | None
    error_step: str | None = None
    error_message: str | None = None


def _atomic_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=dst.parent, suffix=dst.suffix) as handle:
        temp_path = Path(handle.name)
    shutil.copy2(src, temp_path)
    if not temp_path.exists() or temp_path.stat().st_size <= 0:
        raise RuntimeError(f"Atomic copy failed for {src}")
    temp_path.replace(dst)


def _archive_dir(task: Task, repo_root: Path) -> Path:
    return repo_root / "batch" / "output" / sanitize_filename(task.input_path.stem)


def _normalize_error_step(step_name: str | None) -> str:
    mapping = {
        "🎥 Processing input file": "process_input",
        "🎙️ Transcribing with Whisper": "transcribe",
        "✂️ Splitting sentences": "split_sentences",
        "📝 Summarizing and translating": "translate",
        "⚡ Processing and aligning subtitles": "align_subtitles",
        "🎬 Merging subtitles to video": "merge_subtitles",
        "🔊 Generating audio tasks": "generate_audio_tasks",
        "🎵 Extracting reference audio": "extract_reference_audio",
        "🗣️ Generating audio": "generate_audio",
        "🔄 Merging full audio": "merge_audio",
        "🎞️ Merging dubbing to video": "merge_dub_video",
    }
    if not step_name:
        return "unknown"
    return mapping.get(step_name, step_name)


def run_task(task: Task, config: CLIConfig, runtime_paths: RuntimePaths, state_store: StateStore) -> TaskResult:
    batch_input_dir = config.repo_root / "batch" / "input"
    batch_input_dir.mkdir(parents=True, exist_ok=True)
    bridge_path = batch_input_dir / task.name

    if bridge_path.exists():
        if bridge_path.is_dir():
            shutil.rmtree(bridge_path)
        else:
            bridge_path.unlink()

    state_store.mark_running(task.name, task.fingerprint)

    try:
        shutil.copy2(task.input_path, bridge_path)
        status, error_step, error_message = process_video(task.name, dubbing=True, is_retry=False)
        if not status:
            normalized_step = _normalize_error_step(error_step)
            state_store.mark_failed(task.name, task.fingerprint, normalized_step, error_message)
            return TaskResult(
                task=task,
                success=False,
                output_path=None,
                error_step=normalized_step,
                error_message=error_message,
            )

        archive_dir = _archive_dir(task, config.repo_root)
        dub_file = archive_dir / "output_dub.mp4"
        if not dub_file.exists() or dub_file.stat().st_size <= 0:
            raise RuntimeError(f"Expected dubbed output not found: {dub_file}")

        _atomic_copy(dub_file, task.output_path)
        state_store.mark_success(task.name, task.fingerprint, task.output_path.name)
        return TaskResult(task=task, success=True, output_path=task.output_path)
    except Exception as exc:
        state_store.mark_failed(task.name, task.fingerprint, "unhandled", str(exc))
        return TaskResult(
            task=task,
            success=False,
            output_path=None,
            error_step="unhandled",
            error_message=str(exc),
        )
    finally:
        try:
            if bridge_path.exists():
                bridge_path.unlink()
        except OSError:
            pass
