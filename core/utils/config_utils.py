from ruamel.yaml import YAML
import threading
import os
from typing import Any, Optional
from pathlib import Path

CONFIG_PATH = "config.yaml"
lock = threading.Lock()

yaml = YAML()
yaml.preserve_quotes = True

ENV_KEY_MAP = {
    "api.key": "MINIMAX_API_KEY",
    "api.base_url": "MINIMAX_BASE_URL",
    "api.model": "MINIMAX_MODEL",
    "api.llm_support_json": "MINIMAX_LLM_SUPPORT_JSON",
    "whisper.whisperX_302_api_key": "WHISPER_302_API_KEY",
    "whisper.elevenlabs_api_key": "ELEVENLABS_API_KEY",
    "whisper.runtime": "WHISPER_RUNTIME",
    "sf_fish_tts.api_key": "SF_FISH_API_KEY",
    "sf_fish_tts.mode": "SF_FISH_MODE",
    "openai_tts.api_key": "OPENAI_TTS_API_KEY",
    "openai_tts.voice": "OPENAI_TTS_VOICE",
    "azure_tts.api_key": "AZURE_TTS_API_KEY",
    "azure_tts.voice": "AZURE_TTS_VOICE",
    "fish_tts.api_key": "FISH_TTS_API_KEY",
    "fish_tts.character": "FISH_TTS_CHARACTER",
    "sf_cosyvoice2.api_key": "SF_COSYVOICE2_API_KEY",
    "f5tts.302_api": "F5TTS_302_API_KEY",
    "youtube.cookies_path": "YOUTUBE_COOKIES_PATH",
    "max_workers": "MAX_WORKERS",
    "demucs": "DEMUCS_ENABLED",
    "burn_subtitles": "BURN_SUBTITLES",
    "ffmpeg_gpu": "FFMPEG_GPU",
    "tts_method": "TTS_METHOD",
    "target_language": "TARGET_LANGUAGE",
    "summary_length": "SUMMARY_LENGTH",
    "max_split_length": "MAX_SPLIT_LENGTH",
    "reflect_translate": "REFLECT_TRANSLATE",
    "pause_before_translate": "PAUSE_BEFORE_TRANSLATE",
    "subtitle.max_length": "SUBTITLE_MAX_LENGTH",
    "subtitle.target_multiplier": "SUBTITLE_TARGET_MULTIPLIER",
    "model_dir": "MODEL_DIR",
    "ytb_resolution": "YTB_RESOLUTION",
}


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def _parse_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Cannot convert '{value}' to int")


def _convert_env_value(env_key: str, value: str) -> Any:
    if not value:
        return value

    bool_envs = (
        "MINIMAX_LLM_SUPPORT_JSON",
        "DEMUCS_ENABLED",
        "BURN_SUBTITLES",
        "FFMPEG_GPU",
        "REFLECT_TRANSLATE",
        "PAUSE_BEFORE_TRANSLATE",
    )
    int_envs = (
        "MAX_WORKERS",
        "SUMMARY_LENGTH",
        "MAX_SPLIT_LENGTH",
        "SUBTITLE_MAX_LENGTH",
    )

    if env_key.endswith("_ENABLED") or env_key in bool_envs:
        return _parse_bool(value)
    if env_key in int_envs:
        return _parse_int(value)
    if env_key == "SUBTITLE_TARGET_MULTIPLIER":
        return float(value)
    return value


# -----------------------
# load & update config
# -----------------------

_cached_config: Optional[dict] = None
_dotenv_loaded = False


def _parse_dotenv_line(line: str) -> Optional[tuple[str, str]]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()

    if not key:
        return None

    if value and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]

    return key, value


def _ensure_dotenv_loaded() -> None:
    global _dotenv_loaded

    if _dotenv_loaded:
        return

    dotenv_path = Path(CONFIG_PATH).resolve().with_name(".env")
    if dotenv_path.exists():
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_dotenv_line(line)
            if not parsed:
                continue
            key, value = parsed
            os.environ.setdefault(key, value)

    _dotenv_loaded = True


def load_key(key: str) -> Any:
    global _cached_config

    _ensure_dotenv_loaded()

    if key in ENV_KEY_MAP:
        env_var = ENV_KEY_MAP[key]
        env_value = os.environ.get(env_var)
        if env_value is not None:
            return _convert_env_value(env_var, env_value)

    with lock:
        if _cached_config is None:
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    _cached_config = yaml.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Config file '{CONFIG_PATH}' not found. "
                    "Please copy .env.example to .env and configure "
                    "your API keys."
                )

    keys = key.split(".")
    value = _cached_config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            raise KeyError(f"Key '{key}' not found in configuration")
    return value


def get_env_override(key: str) -> Optional[str]:
    _ensure_dotenv_loaded()

    env_var = ENV_KEY_MAP.get(key)
    if not env_var:
        return None

    return os.environ.get(env_var)


def update_key(key: str, new_value: Any) -> bool:
    global _cached_config
    _cached_config = None

    with lock:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.load(f)

        keys = key.split(".")
        current = data
        for k in keys[:-1]:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return False

        if isinstance(current, dict) and keys[-1] in current:
            current[keys[-1]] = new_value
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(data, f)
            return True
        else:
            raise KeyError(f"Key '{keys[-1]}' not found in configuration")


def reload_config() -> None:
    global _cached_config
    _cached_config = None


def get_joiner(language: str) -> str:
    if language in load_key("language_split_with_space"):
        return " "
    elif language in load_key("language_split_without_space"):
        return ""
    else:
        raise ValueError(f"Unsupported language code: {language}")


if __name__ == "__main__":
    print(load_key("language_split_with_space"))
