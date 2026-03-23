from __future__ import annotations

from core.utils.config_utils import load_key


def _require_non_empty(config_key: str, help_text: str) -> None:
    try:
        value = load_key(config_key)
    except (FileNotFoundError, KeyError) as exc:
        raise RuntimeError(help_text) from exc

    if value is None:
        raise RuntimeError(help_text)

    if isinstance(value, str) and not value.strip():
        raise RuntimeError(help_text)


def validate_runtime_requirements() -> None:
    _require_non_empty(
        "api.key",
        "Missing required config: api.key. Configure MINIMAX_API_KEY in .env or set api.key in config.yaml before running batch_translate.",
    )

    whisper_runtime = str(load_key("whisper.runtime")).strip().lower()
    if whisper_runtime == "cloud":
        _require_non_empty(
            "whisper.whisperX_302_api_key",
            "Missing required config: whisper.whisperX_302_api_key for whisper.runtime=cloud.",
        )
    elif whisper_runtime == "elevenlabs":
        _require_non_empty(
            "whisper.elevenlabs_api_key",
            "Missing required config: whisper.elevenlabs_api_key for whisper.runtime=elevenlabs.",
        )

    tts_method = str(load_key("tts_method")).strip().lower()
    tts_requirements = {
        "sf_fish_tts": (
            "sf_fish_tts.api_key",
            "Missing required config: sf_fish_tts.api_key for tts_method=sf_fish_tts.",
        ),
        "openai_tts": (
            "openai_tts.api_key",
            "Missing required config: openai_tts.api_key for tts_method=openai_tts.",
        ),
        "azure_tts": (
            "azure_tts.api_key",
            "Missing required config: azure_tts.api_key for tts_method=azure_tts.",
        ),
        "fish_tts": (
            "fish_tts.api_key",
            "Missing required config: fish_tts.api_key for tts_method=fish_tts.",
        ),
        "sf_cosyvoice2": (
            "sf_cosyvoice2.api_key",
            "Missing required config: sf_cosyvoice2.api_key for tts_method=sf_cosyvoice2.",
        ),
        "f5tts": (
            "f5tts.302_api",
            "Missing required config: f5tts.302_api for tts_method=f5tts.",
        ),
    }
    requirement = tts_requirements.get(tts_method)
    if requirement:
        _require_non_empty(*requirement)