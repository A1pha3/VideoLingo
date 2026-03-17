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
    "whisper.whisperX_302_api_key": "WHISPER_302_API_KEY",
    "whisper.elevenlabs_api_key": "ELEVENLABS_API_KEY",
    "sf_fish_tts.api_key": "SF_FISH_API_KEY",
    "openai_tts.api_key": "OPENAI_TTS_API_KEY",
    "azure_tts.api_key": "AZURE_TTS_API_KEY",
    "fish_tts.api_key": "FISH_TTS_API_KEY",
    "sf_cosyvoice2.api_key": "SF_COSYVOICE2_API_KEY",
    "f5tts.302_api": "F5TTS_302_API_KEY",
}


# -----------------------
# load & update config
# -----------------------

_cached_config: Optional[dict] = None
_dotenv_loaded = False


def _get_dotenv_path() -> Path:
    return Path(CONFIG_PATH).resolve().with_name(".env")


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

    dotenv_path = _get_dotenv_path()
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
            return env_value

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


def update_env_key(key: str, new_value: str) -> bool:
    env_var = ENV_KEY_MAP.get(key)
    if not env_var:
        raise KeyError(f"Key '{key}' is not managed via .env")

    _ensure_dotenv_loaded()

    dotenv_path = _get_dotenv_path()
    lines: list[str] = []
    updated = False

    if dotenv_path.exists():
        lines = dotenv_path.read_text(encoding="utf-8").splitlines()

    new_lines: list[str] = []
    for line in lines:
        parsed = _parse_dotenv_line(line)
        if parsed and parsed[0] == env_var:
            new_lines.append(f"{env_var}={new_value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append(f"{env_var}={new_value}")

    dotenv_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ[env_var] = new_value
    return True


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
