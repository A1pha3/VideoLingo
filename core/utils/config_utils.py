from ruamel.yaml import YAML
import threading
import os
from typing import Any, Optional

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
    return int(value)


def _convert_env_value(env_key: str, value: str) -> Any:
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


def load_key(key: str) -> Any:
    global _cached_config

    if key in ENV_KEY_MAP:
        env_var = ENV_KEY_MAP[key]
        env_value = os.environ.get(env_var)
        if env_value is not None:
            return _convert_env_value(env_var, env_value)

    with lock:
        if _cached_config is None:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _cached_config = yaml.load(f)

    keys = key.split(".")
    value = _cached_config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            raise KeyError(f"Key '{key}' not found in configuration")
    return value


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
