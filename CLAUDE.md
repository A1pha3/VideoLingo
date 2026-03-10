# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VideoLingo is an all-in-one video translation, localization, and dubbing tool that generates Netflix-quality single-line subtitles. The pipeline uses WhisperX for word-level transcription, spaCy/LLM for sentence segmentation, a 3-step translation process (faithfulness → reflection → adaptation), and multiple TTS backends for dubbing.

## Running the Application

```bash
# Installation (runs interactively - detects GPU, installs PyTorch, dependencies)
python install.py

# Start Streamlit UI
streamlit run st.py

# Batch processing (uses batch/tasks_setting.xlsx)
python -m batch.utils.batch_processor
```

## Core Processing Pipeline

The numbered files in `core/` represent sequential pipeline steps:

1. `_1_ytdlp.py` - YouTube download via yt-dlp
2. `_2_asr.py` - WhisperX transcription (local/302.ai/ElevenLabs)
3. `_3_1_split_nlp.py` - spaCy-based sentence splitting
4. `_3_2_split_meaning.py` - LLM-based semantic splitting
5. `_4_1_summarize.py` - Extract terminology and summarize
6. `_4_2_translate.py` - Translate (faithful → reflective)
7. `_5_split_sub.py` - Split long subtitles with alignment
8. `_6_gen_sub.py` - Generate SRT files
9. `_7_sub_into_vid.py` - Burn subtitles into video
10. `_8_1_audio_task.py` - Generate audio tasks for TTS
11. `_8_2_dub_chunks.py` - Calculate dubbing chunks
12. `_9_refer_audio.py` - Extract reference audio for cloning
13. `_10_gen_audio.py` - Generate TTS audio with speed adjustment
14. `_11_merge_audio.py` - Merge audio segments
15. `_12_dub_to_vid.py` - Final dubbing merge

Intermediate results are cached in `output/`. The pipeline can resume from any step - if output files exist, steps are skipped.

## Configuration

- **config.yaml** - Central configuration with `load_key()` and `update_key()` from `core/utils/config_utils.py`
- Settings are grouped: basic (API, language), whisper, subtitle, dubbing (TTS method selection)
- Thread-safe access via `threading.Lock` and `ruamel.yaml` (preserves formatting)
- `display_language` controls UI language (translations in `translations/`)

## Key Architecture Patterns

**Backend abstraction:** ASR (`core/asr_backend/`) and TTS (`core/tts_backend/`) use dispatcher pattern. Selected via `whisper.runtime` and `tts_method` config keys. New backends should follow the existing interface pattern.

**LLM integration:** `core/utils/ask_gpt.py` provides unified interface with:
- File-based caching in `output/gpt_log/` for idempotent retries
- JSON response repair via `json_repair`
- Custom validation via `valid_def` callback
- Retry logic via `@except_handler` decorator

**Prompts:** `core/prompts.py` contains all LLM prompt templates. Prompts are loaded dynamically based on detected language and target language from config.

**Translation quality:** Two-step process in `core/translate_lines.py`:
1. Faithfulness: Direct translation preserving original meaning
2. Expressiveness: Cultural adaptation and fluency improvements

**Audio speed adjustment:** Generated TTS audio is stretched/compressed via ffmpeg `atempo` filter to match subtitle timing. Speed range controlled by `speed_factor` config.

## Coding Conventions

- Use block comments with `# ------------` separators for major sections
- Avoid complex inline comments; no type hints in function signatures
- All comments and print statements in English
- When adding new TTS/ASR backends, follow the dispatcher pattern in `tts_main.py`

## Common File Locations

- `output/` - Intermediate files and final outputs
- `batch/input/` - Videos for batch processing
- `batch/tasks_setting.xlsx` - Batch job configuration
- `_model_cache/` - WhisperX and spaCy models
- `output/log/terminology.json` - Custom terminology (edit before translation if `pause_before_translate` is enabled)

## Dependencies Notes

- PyTorch version varies by GPU detection (CUDA 12.6-12.9 support for RTX 50 series)
- Demucs installed with `--no-deps` to avoid torchaudio conflicts
- WhisperX requires torchaudio 2.8+ at runtime
- FFmpeg is required (libmp3lame optional, falls back to WAV)
