# 配置说明

> config.yaml 完整配置项详解

## 学习目标

完成本教程后，你将能够：
- 理解所有配置项的含义
- 根据需求优化配置
- 解决配置相关的常见问题

## 配置文件位置

VideoLingo 的主配置文件位于项目根目录：

```
VideoLingo/
└── config.yaml
```

配置使用 YAML 格式，通过 `ruamel.yaml` 读写，保留原有格式和注释。

## 配置读取与修改

### 通过代码

```python
from core.utils.config_utils import load_key, update_key

# 读取配置
api_key = load_key('api.key')
target_lang = load_key('target_language')

# 修改配置（线程安全）
update_key('target_language', '日本語')
update_key('whisper.model', 'large-v3-turbo')
```

### 通过 Web 界面

在 Streamlit 左侧设置面板可以修改大部分常用配置，修改后自动保存到 `config.yaml`。

### 直接编辑

```bash
# 使用文本编辑器直接编辑
vim config.yaml
```

> ⚠️ **注意**：直接编辑后需要重启 Streamlit 才能生效。

## 基础配置

### display_language

界面显示语言。

```yaml
display_language: "zh-CN"
```

| 值 | 说明 |
|----|------|
| `zh-CN` | 简体中文 |
| `zh-TW` | 繁体中文 |
| `en` | English |
| `ja` | 日本語 |
| `es` | Español |
| `fr` | Français |
| `ru` | Русский |

### api

LLM API 配置。

```yaml
api:
  key: 'your-api-key'           # API 密钥
  base_url: 'https://yunwu.ai'  # API 基础 URL
  model: 'gpt-4.1-2025-04-14'   # 模型名称
  llm_support_json: false       # 是否支持 JSON 模式
```

**兼容的 API 提供商**：

- OpenAI（官方）
- 302.ai（推荐，一站式服务）
- DeepSeek
- Groq
- 其他 OpenAI 兼容 API

**模型推荐**（按性能排序）：

1. `claude-3-5-sonnet` - 最佳翻译质量
2. `gpt-4.1-2025-04-14` - 综合性能最好
3. `deepseek-v3` - 性价比高
4. `gemini-2.0-flash` - 速度快
5. `gpt-4.1-mini` - 成本低

### max_workers

LLM 并发请求数。

```yaml
max_workers: 4
```

- 本地 LLM（如 Ollama）：建议设为 `1`
- 云端 API：根据 API 限速调整（通常 4-8）

### target_language

翻译目标语言，可使用自然语言描述。

```yaml
target_language: '简体中文'
```

示例：`日本語`、`English`、`Français`、`Español`

### demucs

是否在转录前进行音频分离。

```yaml
demucs: true
```

- `true`：分离人声和背景音乐，提高识别准确率
- `false`：直接使用原音频

> 💡 **建议**：有背景音乐的视频建议开启，处理时间增加约 30%。

## Whisper 配置

### whisper

语音识别配置。

```yaml
whisper:
  model: 'large-v3'              # 模型选择
  language: 'en'                 # 源语言 ISO 639-1 代码
  detected_language: 'en'        # 自动检测的语言（运行时更新）
  runtime: 'local'               # 运行模式
  whisperX_302_api_key: ''       # 302.ai API 密钥
  elevenlabs_api_key: ''         # ElevenLabs API 密钥
```

#### model

| 值 | 大小 | 速度 | 精度 |
|----|------|------|------|
| `large-v3-turbo` | ~3GB | 最快 | 高 |
| `large-v3` | ~3GB | 快 | 最高 |

中文视频会自动使用 `Belle/large-v3` 模型。

#### language

源语言代码（ISO 639-1）：

| 代码 | 语言 | 代码 | 语言 |
|------|------|------|------|
| `en` | 英语 | `zh` | 中文 |
| `ja` | 日语 | `ko` | 韩语 |
| `es` | 西班牙语 | `fr` | 法语 |
| `de` | 德语 | `ru` | 俄语 |
| `it` | 意大利语 | `pt` | 葡萄牙语 |

#### runtime

| 值 | 说明 | 成本 |
|----|------|------|
| `local` | 本地运行 WhisperX | 免费，需要 GPU |
| `cloud` | 302.ai API | 按量付费 |
| `elevenlabs` | ElevenLabs API | 实验性，按量付费 |

## 字幕配置

### burn_subtitles

是否将字幕烧录到视频中。

```yaml
burn_subtitles: true
```

- `true`：生成带字幕的视频
- `false`：仅生成 SRT 字幕文件

### subtitle

字幕分割参数。

```yaml
subtitle:
  max_length: 75           # 单行最大字符数
  target_multiplier: 1.2   # 翻译文本长度系数
```

- `max_length`：Netflix 标准建议 40-80 字符
- `target_multiplier`：翻译后文本通常更长，用于调整分割参考长度

### 其他相关配置

```yaml
# 摘要最大长度（影响术语提取）
summary_length: 8000

# 首次分割最大词数
max_split_length: 20

# 是否启用翻译反思
reflect_translate: true

# 是否在翻译前暂停（允许手动编辑术语表）
pause_before_translate: false
```

## 配音配置

### tts_method

TTS 引擎选择。

```yaml
tts_method: 'azure_tts'
```

| 值 | 说明 | 参考音频 | 成本 |
|----|------|----------|------|
| `azure_tts` | Microsoft Azure TTS | 否 | 按量付费 |
| `openai_tts` | OpenAI TTS | 否 | 按量付费 |
| `edge_tts` | Microsoft Edge TTS | 否 | 免费 |
| `sf_fish_tts` | SiliconFlow Fish TTS | 是 | 按量付费 |
| `sf_cosyvoice2` | SiliconFlow CosyVoice2 | 是 | 按量付费 |
| `fish_tts` | 302.ai Fish TTS | 是 | 按量付费 |
| `gpt_sovits` | 本地 GPT-SoVITS | 是 | 免费 |
| `f5tts` | 302.ai F5-TTS | 是 | 按量付费 |
| `custom_tts` | 自定义 TTS | 取决于实现 | - |

### 各 TTS 详细配置

#### sf_fish_tts

```yaml
sf_fish_tts:
  api_key: 'YOUR_API_KEY'
  voice: 'anna'              # 预设声音名称
  custom_name: ''            # 自定义声音名称
  voice_id: ''               # 自定义声音 ID
  mode: "preset"             # preset / custom / dynamic
```

#### azure_tts

```yaml
azure_tts:
  api_key: 'YOUR_302_API_KEY'
  voice: 'zh-CN-YunfengNeural'
```

常用声音：
- 中文：`zh-CN-YunfengNeural`（男）、`zh-CN-XiaoxiaoNeural`（女）
- 英文：`en-US-GuyNeural`（男）、`en-US-JennyNeural`（女）

#### openai_tts

```yaml
openai_tts:
  api_key: 'YOUR_302_API_KEY'
  voice: 'alloy'
```

可用声音：`alloy`、`echo`、`fable`、`onyx`、`nova`、`shimmer`

#### edge_tts

```yaml
edge_tts:
  voice: 'zh-CN-XiaoxiaoNeural'
```

#### gpt_sovits

```yaml
gpt_sovits:
  character: 'Huanyuv2'
  refer_mode: 3             # 参考模式：1/2/3
```

### speed_factor

配音速度调整参数。

```yaml
speed_factor:
  min: 1.0          # 最小速度（不加速）
  accept: 1.2       # 可接受速度
  max: 1.4          # 最大速度
```

当 TTS 音频时长超过目标时长时，会使用 ffmpeg `atempo` 滤镜加速播放。

### 合并配置

```yaml
min_subtitle_duration: 2.5   # 最小字幕时长（秒）
min_trim_duration: 3.5       # 不拆分的字幕最小时长
tolerance: 1.5               # 允许延长的时长（秒）
```

## 高级配置

### ffmpeg_gpu

是否使用 GPU 硬件加速（h264_nvenc）。

```yaml
ffmpeg_gpu: false
```

需要：
- NVIDIA GPU
- 支持 NVENC 的驱动
- FFmpeg 编译时包含 nvenc

### youtube

```yaml
youtube:
  cookies_path: ''      # Cookies 文件路径（用于会员视频）
ytb_resolution: '1080'  # 默认下载分辨率
```

### model_dir

模型缓存目录。

```yaml
model_dir: './_model_cache'
```

### 允许的文件格式

```yaml
allowed_video_formats:
  - 'mp4' - 'mov' - 'avi' - 'mkv'
  - 'flv' - 'wmv' - 'webm'

allowed_audio_formats:
  - 'wav' - 'mp3' - 'flac' - 'm4a'
```

### spaCy 模型映射

```yaml
spacy_model_map:
  en: 'en_core_web_md'
  ru: 'ru_core_news_md'
  fr: 'fr_core_news_md'
  ja: 'ja_core_news_md'
  es: 'es_core_news_md'
  de: 'de_core_news_md'
  it: 'it_core_news_md'
  zh: 'zh_core_web_md'
```

### 语言分隔符

```yaml
language_split_with_space:
  - 'en' - 'es' - 'fr' - 'de'
  - 'it' - 'ru'

language_split_without_space:
  - 'zh' - 'ja'
```

用于句子分割时的文本连接。

## 配置模板

### 本地免费方案

```yaml
api:
  key: 'fake-key'  # Ollama 不需要真实 key
  base_url: 'http://localhost:11434/v1'
  model: 'llama3'
  llm_support_json: false

whisper:
  runtime: 'local'
  model: 'large-v3-turbo'

tts_method: 'edge_tts'

max_workers: 1
```

### 云端高质量方案

```yaml
api:
  key: 'your-302-api-key'
  base_url: 'https://yunwu.ai'
  model: 'claude-3-5-sonnet-20241022'

whisper:
  runtime: 'cloud'
  whisperX_302_api_key: 'your-302-api-key'

tts_method: 'azure_tts'

demucs: true
reflect_translate: true
```

### 批处理优化

```yaml
max_workers: 8         # 提高 LLM 并发
summary_length: 4000   # 减少摘要长度以加快速度
whisper:
  model: 'large-v3-turbo'  # 使用更快的模型
```

## 常见问题

### Q: API 调用失败怎么办？

1. 检查 `api.key` 和 `api.base_url` 是否正确
2. 确认 API 账户有足够余额
3. 尝试设置 `llm_support_json: true`（如果模型支持）

### Q: 如何使用本地 LLM？

```yaml
api:
  key: 'any-key'
  base_url: 'http://localhost:11434/v1'  # Ollama
  model: 'llama3'
  llm_support_json: false

max_workers: 1  # 本地模型通常不支持高并发
```

### Q: TTS 没有声音？

1. 检查 TTS API 密钥
2. 确认语音名称正确
3. 查看 `output/` 目录下的日志文件

## 下一步

- 🏗️ 阅读 [架构设计](architecture.md) 了解配置如何影响处理流程
- 🔧 阅读 [故障排除](troubleshooting.md) 解决配置问题
