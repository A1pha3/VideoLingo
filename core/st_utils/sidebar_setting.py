import asyncio

import streamlit as st
from translations.translations import translate as t
from translations.translations import DISPLAY_LANGUAGES
from core.utils import *


@st.cache_data(ttl=86400, show_spinner=False)
def get_edge_tts_voice_choices():
    try:
        import edge_tts as edge_tts_lib

        voices = asyncio.run(edge_tts_lib.list_voices())
        voices = sorted(voices, key=lambda voice: voice.get("ShortName", ""))
        options = [voice.get("ShortName") for voice in voices if voice.get("ShortName")]
        labels = {
            voice.get("ShortName"): f"{voice.get('ShortName')} | {voice.get('Locale', '')} | {voice.get('Gender', '')}"
            for voice in voices
            if voice.get("ShortName")
        }
        language_map = {
            voice.get("ShortName"): str(voice.get("Locale", "")).split("-")[0].lower()
            for voice in voices
            if voice.get("ShortName")
        }
        locale_map = {
            voice.get("ShortName"): voice.get("Locale", "")
            for voice in voices
            if voice.get("ShortName")
        }
        return options, labels, language_map, locale_map
    except Exception:
        return [], {}, {}, {}


def get_edge_tts_preferred_languages(target_language):
    normalized = str(target_language or "").strip().lower()
    if not normalized:
        return []

    language_keywords = {
        "zh": ["中文", "汉语", "漢語", "普通话", "普通話", "mandarin", "chinese", "simplified chinese", "traditional chinese"],
        "en": ["english", "英语", "英文"],
        "ja": ["japanese", "日语", "日語", "日文", "日本語"],
        "ko": ["korean", "韩语", "韓語", "한국어", "조선말"],
        "fr": ["french", "法语", "法語", "français"],
        "de": ["german", "德语", "德語", "deutsch"],
        "es": ["spanish", "西班牙语", "西班牙語", "español"],
        "it": ["italian", "意大利语", "意大利語", "italiano"],
        "ru": ["russian", "俄语", "俄語", "русский"],
        "pt": ["portuguese", "葡萄牙语", "葡萄牙語", "português"],
        "ar": ["arabic", "阿拉伯语", "阿拉伯語", "العربية"],
        "hi": ["hindi", "印地语", "印地語", "हिन्दी"],
        "tr": ["turkish", "土耳其语", "土耳其語", "türkçe"],
        "vi": ["vietnamese", "越南语", "越南語", "tiếng việt"],
        "th": ["thai", "泰语", "泰語", "ไทย"],
    }

    preferred = [code for code, keywords in language_keywords.items() if any(keyword in normalized for keyword in keywords)]
    return preferred


def format_edge_tts_language_group(group_code):
    language_names = {
        "all": "All languages / 全部语言",
        "ar": "Arabic / 阿拉伯语",
        "de": "German / 德语",
        "en": "English / 英语",
        "es": "Spanish / 西班牙语",
        "fr": "French / 法语",
        "hi": "Hindi / 印地语",
        "it": "Italian / 意大利语",
        "ja": "Japanese / 日语",
        "ko": "Korean / 韩语",
        "pt": "Portuguese / 葡萄牙语",
        "ru": "Russian / 俄语",
        "th": "Thai / 泰语",
        "tr": "Turkish / 土耳其语",
        "vi": "Vietnamese / 越南语",
        "zh": "Chinese / 中文",
    }
    return language_names.get(group_code, group_code.upper())


def get_default_edge_tts_language_group(language_groups, preferred_languages):
    for language_code in preferred_languages:
        if language_code in language_groups:
            return language_code
    return "all"

def mask_secret(value):
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def config_input(label, key, help=None, secret=False):
    """Generic config input handler"""
    current_value = load_key(key)

    if secret:
        session_key = f"__masked_input__{key}"
        if session_key not in st.session_state:
            st.session_state[session_key] = ""

        secret_help = help or ""
        if current_value:
            suffix = t("Leave blank to keep current value")
            secret_help = f"{secret_help} {suffix}".strip()

        val = st.text_input(
            label,
            value=st.session_state[session_key],
            help=secret_help,
            type="password",
            placeholder=mask_secret(current_value),
        )
        if val and val != current_value:
            update_env_key(key, val)
            st.session_state[session_key] = ""
        return current_value

    val = st.text_input(label, value=current_value, help=help)
    if val != current_value:
        update_key(key, val)
    return val

def page_setting():

    display_language = st.selectbox("Display Language 🌐", 
                                  options=list(DISPLAY_LANGUAGES.keys()),
                                  index=list(DISPLAY_LANGUAGES.values()).index(load_key("display_language")))
    if DISPLAY_LANGUAGES[display_language] != load_key("display_language"):
        update_key("display_language", DISPLAY_LANGUAGES[display_language])
        st.rerun()

    # with st.expander(t("Youtube Settings"), expanded=True):
    #     config_input(t("Cookies Path"), "youtube.cookies_path")

    with st.expander(t("LLM Configuration"), expanded=True):
        config_input(t("API_KEY"), "api.key", secret=True)
        config_input(t("BASE_URL"), "api.base_url", help=t("Openai format, will add /v1/chat/completions automatically"))
        
        c1, c2 = st.columns([4, 1])
        with c1:
            config_input(t("MODEL"), "api.model", help=t("click to check API validity")+ " 👉")
        with c2:
            if st.button("📡", key="api"):
                st.toast(t("API Key is valid") if check_api() else t("API Key is invalid"), 
                        icon="✅" if check_api() else "❌")
        llm_support_json = st.toggle(t("LLM JSON Format Support"), value=load_key("api.llm_support_json"), help=t("Enable if your LLM supports JSON mode output"))
        if llm_support_json != load_key("api.llm_support_json"):
            update_key("api.llm_support_json", llm_support_json)
            st.rerun()
    with st.expander(t("Subtitles Settings"), expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            langs = {
                "🇺🇸 English": "en",
                "🇨🇳 简体中文": "zh",
                "🇪🇸 Español": "es",
                "🇷🇺 Русский": "ru",
                "🇫🇷 Français": "fr",
                "🇩🇪 Deutsch": "de",
                "🇮🇹 Italiano": "it",
                "🇯🇵 日本語": "ja"
            }
            lang = st.selectbox(
                t("Recog Lang"),
                options=list(langs.keys()),
                index=list(langs.values()).index(load_key("whisper.language"))
            )
            if langs[lang] != load_key("whisper.language"):
                update_key("whisper.language", langs[lang])
                st.rerun()

        runtime = st.selectbox(t("WhisperX Runtime"), options=["local", "cloud", "elevenlabs"], index=["local", "cloud", "elevenlabs"].index(load_key("whisper.runtime")), help=t("Local runtime requires >8GB GPU, cloud runtime requires 302ai API key, elevenlabs runtime requires ElevenLabs API key"))
        if runtime != load_key("whisper.runtime"):
            update_key("whisper.runtime", runtime)
            st.rerun()
        if runtime == "cloud":
            config_input(t("WhisperX 302ai API"), "whisper.whisperX_302_api_key", secret=True)
        if runtime == "elevenlabs":
            config_input(("ElevenLabs API"), "whisper.elevenlabs_api_key", secret=True)

        with c2:
            target_language = st.text_input(t("Target Lang"), value=load_key("target_language"), help=t("Input any language in natural language, as long as llm can understand"))
            if target_language != load_key("target_language"):
                update_key("target_language", target_language)
                st.rerun()

        demucs = st.toggle(t("Vocal separation enhance"), value=load_key("demucs"), help=t("Recommended for videos with loud background noise, but will increase processing time"))
        if demucs != load_key("demucs"):
            update_key("demucs", demucs)
            st.rerun()
        
        burn_subtitles = st.toggle(t("Burn-in Subtitles"), value=load_key("burn_subtitles"), help=t("Whether to burn subtitles into the video, will increase processing time"))
        if burn_subtitles != load_key("burn_subtitles"):
            update_key("burn_subtitles", burn_subtitles)
            st.rerun()
    with st.expander(t("Dubbing Settings"), expanded=True):
        tts_methods = ["azure_tts", "openai_tts", "fish_tts", "sf_fish_tts", "edge_tts", "gpt_sovits", "custom_tts", "sf_cosyvoice2", "f5tts"]
        bilingual_dub_subtitles = st.toggle(
            t("Bilingual Dubbing Subtitles"),
            value=load_key("bilingual_dub_subtitles"),
            help=t("Show source text together with translated subtitles in dubbed video."),
        )
        if bilingual_dub_subtitles != load_key("bilingual_dub_subtitles"):
            update_key("bilingual_dub_subtitles", bilingual_dub_subtitles)
            st.rerun()

        current_tts_method = load_key("tts_method")
        select_tts = st.selectbox(
            t("TTS Method"),
            options=tts_methods,
            index=tts_methods.index(current_tts_method),
            key="tts_method_select",
        )
        if select_tts != current_tts_method:
            update_key("tts_method", select_tts)

        # sub settings for each tts method
        if select_tts == "sf_fish_tts":
            config_input(t("SiliconFlow API Key"), "sf_fish_tts.api_key", secret=True)
            
            # Add mode selection dropdown
            mode_options = {
                "preset": t("Preset"),
                "custom": t("Refer_stable"),
                "dynamic": t("Refer_dynamic")
            }
            selected_mode = st.selectbox(
                t("Mode Selection"),
                options=list(mode_options.keys()),
                format_func=lambda x: mode_options[x],
                index=list(mode_options.keys()).index(load_key("sf_fish_tts.mode")) if load_key("sf_fish_tts.mode") in mode_options.keys() else 0
            )
            if selected_mode != load_key("sf_fish_tts.mode"):
                update_key("sf_fish_tts.mode", selected_mode)
                st.rerun()
            if selected_mode == "preset":
                config_input("Voice", "sf_fish_tts.voice")

        elif select_tts == "openai_tts":
            config_input("302ai API", "openai_tts.api_key", secret=True)
            config_input(t("OpenAI Voice"), "openai_tts.voice")

        elif select_tts == "fish_tts":
            config_input("302ai API", "fish_tts.api_key", secret=True)
            fish_tts_character = st.selectbox(t("Fish TTS Character"), options=list(load_key("fish_tts.character_id_dict").keys()), index=list(load_key("fish_tts.character_id_dict").keys()).index(load_key("fish_tts.character")))
            if fish_tts_character != load_key("fish_tts.character"):
                update_key("fish_tts.character", fish_tts_character)
                st.rerun()

        elif select_tts == "azure_tts":
            config_input("302ai API", "azure_tts.api_key", secret=True)
            config_input(t("Azure Voice"), "azure_tts.voice")
        
        elif select_tts == "gpt_sovits":
            st.info(t("Please refer to Github homepage for GPT_SoVITS configuration"))
            config_input(t("SoVITS Character"), "gpt_sovits.character")
            
            refer_mode_options = {1: t("Mode 1: Use provided reference audio only"), 2: t("Mode 2: Use first audio from video as reference"), 3: t("Mode 3: Use each audio from video as reference")}
            selected_refer_mode = st.selectbox(
                t("Refer Mode"),
                options=list(refer_mode_options.keys()),
                format_func=lambda x: refer_mode_options[x],
                index=list(refer_mode_options.keys()).index(load_key("gpt_sovits.refer_mode")),
                help=t("Configure reference audio mode for GPT-SoVITS")
            )
            if selected_refer_mode != load_key("gpt_sovits.refer_mode"):
                update_key("gpt_sovits.refer_mode", selected_refer_mode)
                st.rerun()
                
        elif select_tts == "edge_tts":
            edge_voice_options, edge_voice_labels, edge_voice_languages, edge_voice_locales = get_edge_tts_voice_choices()
            current_edge_voice = load_key("edge_tts.voice")
            preferred_languages = get_edge_tts_preferred_languages(load_key("target_language"))

            if current_edge_voice not in edge_voice_options:
                edge_voice_options = [current_edge_voice, *edge_voice_options] if current_edge_voice else edge_voice_options
                if current_edge_voice:
                    edge_voice_languages[current_edge_voice] = str(current_edge_voice).split("-")[0].lower() if "-" in str(current_edge_voice) else ""
                    edge_voice_locales[current_edge_voice] = ""

            language_groups = sorted({lang for lang in edge_voice_languages.values() if lang})

            if edge_voice_options:
                default_language_group = get_default_edge_tts_language_group(language_groups, preferred_languages)
                language_group_session_key = "edge_tts_language_group"
                language_group_pref_key = "edge_tts_language_group_pref"
                current_group_preference = (tuple(language_groups), tuple(preferred_languages))

                if st.session_state.get(language_group_pref_key) != current_group_preference:
                    st.session_state[language_group_session_key] = default_language_group
                    st.session_state[language_group_pref_key] = current_group_preference

                filter_col, toggle_col = st.columns([3, 2])
                with filter_col:
                    selected_language_group = st.selectbox(
                        "Edge TTS language group",
                        options=["all", *language_groups],
                        format_func=format_edge_tts_language_group,
                        index=["all", *language_groups].index(st.session_state.get(language_group_session_key, default_language_group)),
                        key=language_group_session_key,
                        help="Filter Edge TTS voices by language group.",
                    )
                with toggle_col:
                    prioritize_target_language = st.toggle(
                        "Target first",
                        value=bool(preferred_languages),
                        help="Show voices matching Target Lang first.",
                    )

                filtered_edge_voice_options = [
                    voice for voice in edge_voice_options
                    if selected_language_group == "all" or edge_voice_languages.get(voice) == selected_language_group
                ]

                if prioritize_target_language and preferred_languages:
                    filtered_edge_voice_options = sorted(
                        filtered_edge_voice_options,
                        key=lambda voice: (
                            0 if edge_voice_languages.get(voice) in preferred_languages else 1,
                            edge_voice_locales.get(voice, ""),
                            voice,
                        ),
                    )

                if not filtered_edge_voice_options:
                    filtered_edge_voice_options = edge_voice_options

                selected_edge_voice = st.selectbox(
                    t("Edge TTS Voice"),
                    options=filtered_edge_voice_options,
                    index=filtered_edge_voice_options.index(current_edge_voice) if current_edge_voice in filtered_edge_voice_options else 0,
                    format_func=lambda voice: edge_voice_labels.get(voice, voice),
                    help=t("Select an available Edge voice"),
                )
                if selected_edge_voice != current_edge_voice:
                    update_key("edge_tts.voice", selected_edge_voice)
                    st.rerun()
            else:
                config_input(t("Edge TTS Voice"), "edge_tts.voice")

        elif select_tts == "sf_cosyvoice2":
            config_input(t("SiliconFlow API Key"), "sf_cosyvoice2.api_key", secret=True)
        
        elif select_tts == "f5tts":
            config_input("302ai API", "f5tts.302_api", secret=True)
        
def check_api():
    try:
        resp = ask_gpt("This is a test, response 'message':'success' in json format.", 
                      resp_type="json", log_title='None')
        return resp.get('message') == 'success'
    except Exception:
        return False
    
if __name__ == "__main__":
    check_api()
