# 配置说明

> config.yaml 完整配置项详解

## 学习目标

完成本教程后，你将能够：

- 理解所有配置项的含义
- 根据需求优化配置
- 解决配置相关的常见问题

## 配置文件位置

VideoLingo 的主配置文件位于项目根目录：

```text
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

## 先看这一节：首次配置应该怎么做

如果你是第一次打开 VideoLingo，不建议一上来就逐个研究所有参数。更高效的方式是先完成一套能跑通的最小配置，再按效果逐步细调。

### 先分清 3 类配置

#### 第一类：必填项，不填就无法正常跑通

- `api.key`
- `api.base_url`
- `api.model`
- `whisper.runtime`
- `target_language`
- `tts_method`

#### 第二类：强烈建议确认的开关

- `whisper.language`
- `demucs`
- `burn_subtitles`
- `max_workers`
- `api.llm_support_json`

#### 第三类：进阶优化项，先不动也能用

- `subtitle.max_length`
- `summary_length`
- `max_split_length`
- `reflect_translate`
- `speed_factor`
- `ffmpeg_gpu`

### 推荐的首次配置顺序

#### 第 1 步：设置界面语言

先确认：

```yaml
display_language: 'zh-CN'
```

这只影响界面显示语言，不影响翻译结果。

#### 第 2 步：先把 LLM 配通

左侧边栏的 **LLM Configuration** 是最优先要配置的区域。

至少要填这 4 项：

```yaml
api:
  key: 'your-api-key'
  base_url: 'https://your-openai-compatible-host'
  model: 'your-model-name'
  llm_support_json: false
```

配置原则：

- `key`：你的 API 密钥
- `base_url`：只填服务根地址，不要手动补 `/v1/chat/completions`
- `model`：填服务商实际提供的模型名
- `llm_support_json`：只有模型明确支持 JSON 输出时再开

建议你在页面里填完后，点击模型右侧的校验按钮，先确认 API 能正常返回。

#### 第 3 步：确认字幕语言方向

在 **Subtitles Settings** 中先确认：

```yaml
whisper:
  language: 'en'

target_language: '简体中文'
```

含义是：

- `whisper.language`：原视频的语音语言
- `target_language`：最终要翻译成什么语言

如果源语言填错，后面整条链路都会变差，包括识别、断句、翻译和配音。

#### 第 4 步：选 Whisper 运行方式

这是最关键的运行模式选择：

```yaml
whisper:
  runtime: 'local'
```

三种模式的选择建议：

| 模式 | 适合谁 | 说明 |
| ---- | ---- | ---- |
| `local` | 本机算力够、希望降低成本 | 本地跑 WhisperX，最省钱，但吃算力和内存 |
| `cloud` | 希望更稳定省事 | 使用 302.ai 的 WhisperX 接口 |
| `elevenlabs` | 已有 ElevenLabs 能力 | 实验性方案，按量计费 |

补充说明：

- `local` 不要求你额外填写云端密钥，但本地性能不足时会明显变慢
- `cloud` 需要填写 `whisper.whisperX_302_api_key`
- `elevenlabs` 需要填写 `whisper.elevenlabs_api_key`

#### 第 5 步：选 TTS 引擎

在 **Dubbing Settings** 中先选一条最适合你的路线。

最常见的 3 种选择：

| 目标 | 推荐配置 | 原因 |
| ---- | ---- | ---- |
| 先跑通、尽量省钱 | `edge_tts` | 免费、配置最少 |
| 追求稳定、音色通用 | `azure_tts` | 易用、效果稳 |
| 想做角色复刻/参考音频配音 | `sf_fish_tts` / `fish_tts` / `gpt_sovits` | 支持参考音频或角色音色 |

如果你只是想先确认整条流程能跑通，建议第一轮直接使用：

```yaml
tts_method: 'edge_tts'
```

这样可以把问题先收敛到“识别 + 翻译 + 合成链路是否正常”，避免一开始就被多套付费 TTS 参数干扰。

#### 第 6 步：最后再决定要不要开增强项

两个最常用的增强开关：

```yaml
demucs: true
burn_subtitles: true
```

- `demucs`：视频背景音乐大、旁白被盖住时建议开启
- `burn_subtitles`：需要直接输出带硬字幕的视频时开启

如果你只想先验证流程，`demucs` 可以先关，速度会更快。

## 推荐的 4 套实战配置

下面不是“所有参数模板”，而是最容易真正用起来的 4 种配置方案。

### 方案 1：最稳的首次跑通方案

适合：第一次使用，先验证流程。

```yaml
api:
  key: 'your-api-key'
  base_url: 'https://your-openai-compatible-host'
  model: 'your-model-name'
  llm_support_json: false

whisper:
  runtime: 'local'
  language: 'en'

target_language: '简体中文'

tts_method: 'edge_tts'

demucs: false
burn_subtitles: true
max_workers: 2
```

特点：

- 配置最少
- 成本最低
- 便于快速定位问题

### 方案 2：识别本地，翻译云端，配音免费

适合：本地能跑 WhisperX，但不想为 TTS 付费。

```yaml
api:
  key: 'your-api-key'
  base_url: 'https://your-openai-compatible-host'
  model: 'your-model-name'
  llm_support_json: true

whisper:
  runtime: 'local'
  language: 'en'

target_language: '简体中文'

tts_method: 'edge_tts'

demucs: true
burn_subtitles: true
max_workers: 4
```

特点：

- 核心成本集中在 LLM
- 配音免费
- 适合大部分普通视频翻译场景

### 方案 3：云端识别 + 云端翻译 + Azure 配音

适合：希望成功率更高、体验更省心。

```yaml
api:
  key: 'your-api-key'
  base_url: 'https://your-openai-compatible-host'
  model: 'your-model-name'
  llm_support_json: true

whisper:
  runtime: 'cloud'
  language: 'en'
  whisperX_302_api_key: 'your-302-api-key'

target_language: '简体中文'

tts_method: 'azure_tts'

azure_tts:
  api_key: 'your-302-api-key'
  voice: 'zh-CN-YunfengNeural'
```

特点：

- 依赖本地算力更少
- 适合批量处理或长期使用
- 费用高于本地方案

### 方案 4：需要参考音频/角色感的配音方案

适合：想要更像“原角色口型和人设”的配音效果。

```yaml
tts_method: 'sf_fish_tts'

sf_fish_tts:
  api_key: 'your-siliconflow-key'
  mode: 'preset'
  voice: 'anna'
```

如果后续你要做自定义音色，再切换到：

- `mode: custom`
- `mode: dynamic`

建议：先把整条流程跑通，再升级到参考音频模式。

## 页面配置和 config.yaml 的关系

很多用户会混淆“页面改”和“文件改”的区别。实际规则很简单：

- 日常使用时，优先在 Streamlit 左侧边栏修改
- 页面里改动后，会自动写回 `config.yaml`
- 只有高级参数才建议手动编辑 `config.yaml`

### 页面里能直接改的内容

主要包括：

- 显示语言
- LLM 配置
- 源语言与目标语言
- Whisper 运行模式
- Demucs 开关
- 烧录字幕开关
- TTS 方法及其常用参数

### 更适合手动编辑的内容

主要包括：

- `subtitle.max_length`
- `subtitle.target_multiplier`
- `summary_length`
- `max_split_length`
- `reflect_translate`
- `speed_factor`
- `ffmpeg_gpu`
- `model_dir`

经验上，先把页面中可见配置调通，再动这些高级参数，效率最高。

## 最容易配错的地方

### 1. `api.base_url` 填成了完整接口地址

错误思路：

- 填成 `/v1/chat/completions`
- 填成某个具体模型的调用路径

正确思路：

- 只填 API 服务的基础地址
- 保持 OpenAI 兼容格式

如果你的服务商文档写的是 OpenAI-compatible，一般就按基础地址填写。

### 2. `api.base_url` 末尾有空格

这是非常隐蔽但很常见的问题。复制网址时如果多带了前后空格，接口校验可能失败。

建议：

- 手动删除前后空格
- 尽量通过页面重新输入，不要整段粘贴后不检查

### 3. `llm_support_json` 开错

这个开关不是“建议默认开启”，而是“模型明确支持时再开启”。

现象通常是：

- API 能返回，但流程里 JSON 解析失败
- 提示格式错误或关键字段缺失

拿不准时，先设为：

```yaml
llm_support_json: false
```

### 4. `whisper.language` 填错

这里填的是原视频语言，不是目标翻译语言。

例如：

- 英文视频翻成中文：`whisper.language: 'en'`
- 日文视频翻成中文：`whisper.language: 'ja'`

### 5. 一开始就开太多增强功能

比如同时启用：

- `demucs: true`
- 高质量云端 TTS
- `reflect_translate: true`
- 较高 `max_workers`

这样一旦出问题，很难判断到底是哪一层出了问题。

更合理的方式是：

1. 先用最小配置跑通
2. 再开 Demucs
3. 再升级 TTS
4. 最后再调翻译质量参数

## 推荐排障顺序

当你遇到“能启动，但处理失败”时，按这个顺序排查最快。

### 第 1 层：先检查 LLM 是否可用

检查点：

- `api.key` 是否有效
- `api.base_url` 是否正确
- `api.model` 是否存在
- 页面校验按钮是否通过

### 第 2 层：再检查 Whisper 路线

如果是本地：

- 本机算力是否足够
- 本地模型是否已正常下载
- `whisper.language` 是否正确

如果是云端：

- `whisper.whisperX_302_api_key` 是否可用
- `whisper.runtime` 是否确实切到 `cloud`

### 第 3 层：最后检查 TTS

检查点：

- `tts_method` 选的是什么
- 对应 TTS 的 API key 是否已填
- 语音名或角色名是否存在

如果你不确定问题是否来自配音，先切回：

```yaml
tts_method: 'edge_tts'
```

这样最容易验证是不是某个付费 TTS 配置本身出了问题。

## 我该优先改哪些参数

如果你不想研究太多，日常最常改的其实只有下面这些：

```yaml
api.key
api.base_url
api.model
api.llm_support_json
whisper.language
whisper.runtime
target_language
demucs
burn_subtitles
tts_method
```

把这 10 个参数理解透，大多数场景就已经够用了。

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

## 自测问题

完成配置后，尝试回答以下问题：

1. **为什么 `max_workers` 对本地 LLM 和云端 API 的建议值不同？**
   
   <details>
   <summary>点击查看答案</summary>
   本地 LLM（如 Ollama）通常不支持高并发请求，设置过高的 `max_workers` 会导致请求排队或失败。云端 API 则可以处理更高的并发，但也受限于 API 的速率限制。
   </details>

2. **`reflect_translate: true` 会带来什么影响？**
   
   <details>
   <summary>点击查看答案</summary>
   启用反思翻译会进行两步翻译（忠实→反思→改编），翻译质量提升约 30%，但处理时间也会增加约 50%，API 调用成本翻倍。
   </details>

3. **什么情况下应该启用 `demucs: true`？**
   
   <details>
   <summary>点击查看答案</summary>
   当视频有明显的背景音乐或噪音时，启用 Demucs 可以分离人声，显著提高 WhisperX 的识别准确率。但处理时间会增加约 30%。
   </details>

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
