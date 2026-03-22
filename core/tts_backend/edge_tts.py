import asyncio
from pathlib import Path

import edge_tts as edge_tts_lib
from pydub import AudioSegment

from core.utils import *

# Available voices can be listed using: edge-tts --list-voices
VOICE_ALIASES = {
    "jenny": "en-US-JennyNeural",
    "guy": "en-US-GuyNeural",
    "sonia": "en-GB-SoniaNeural",
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "nanami": "ja-JP-NanamiNeural",
    "keita": "ja-JP-KeitaNeural",
}


def _default_voice_for_target_language() -> str:
    try:
        target_language = str(load_key("target_language")).lower()
    except Exception:
        return "en-US-JennyNeural"

    if any(keyword in target_language for keyword in ("中文", "chinese", "mandarin", "简体", "繁體", "繁体")):
        return "zh-CN-XiaoxiaoNeural"
    if any(keyword in target_language for keyword in ("english", "英语", "英文")):
        return "en-US-JennyNeural"
    if any(keyword in target_language for keyword in ("日本", "japanese", "日语", "日文")):
        return "ja-JP-NanamiNeural"
    if any(keyword in target_language for keyword in ("한국", "korean", "韩语", "韓語")):
        return "ko-KR-SunHiNeural"
    return "en-US-JennyNeural"


def _resolve_voice() -> tuple[str, str, str]:
    edge_set = load_key("edge_tts")
    configured_voice = str(edge_set.get("voice", "") or "").strip()
    if not configured_voice:
        default_voice = _default_voice_for_target_language()
        return default_voice, "default", configured_voice

    resolved_voice = VOICE_ALIASES.get(configured_voice.lower(), configured_voice)
    if resolved_voice != configured_voice:
        return resolved_voice, "alias", configured_voice

    return resolved_voice, "configured", configured_voice


async def _save_edge_audio(text: str, save_path: Path, voice: str) -> None:
    temp_audio_path = save_path.with_suffix(".edge_tmp.mp3")
    communicate = edge_tts_lib.Communicate(text=text, voice=voice)
    try:
        await communicate.save(str(temp_audio_path))
        if save_path.suffix.lower() == ".wav":
            audio = AudioSegment.from_file(temp_audio_path)
            audio.export(
                save_path,
                format="wav",
                parameters=["-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1"],
            )
        else:
            temp_audio_path.replace(save_path)
    finally:
        if temp_audio_path.exists():
            temp_audio_path.unlink()


def edge_tts(text, save_path):
    voice, voice_source, configured_voice = _resolve_voice()

    speech_file_path = Path(save_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)

    if voice_source == "default":
        print(f"Edge TTS voice not configured, fallback to default voice: {voice}")
    elif voice_source == "alias":
        print(f"Edge TTS voice alias resolved: {configured_voice} -> {voice}")
    else:
        print(f"Edge TTS using configured voice: {voice}")

    asyncio.run(_save_edge_audio(text=text, save_path=speech_file_path, voice=voice))
    print(f"Audio saved to {speech_file_path} with voice {voice}")

if __name__ == "__main__":
    edge_tts("Today is a good day!", "edge_tts.wav")
