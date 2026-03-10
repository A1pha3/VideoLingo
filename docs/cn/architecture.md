# 架构设计

> VideoLingo 系统架构、处理流程与核心模块深度解析

## 学习目标

完成本教程后，你将能够：
- 理解 VideoLingo 的整体架构设计
- 掌握 15 步处理管线的详细流程
- 了解各模块之间的交互方式
- 理解缓存和断点续传机制

## 系统概述

VideoLingo 是一个高度模块化的视频翻译系统，采用流水线架构，每个步骤独立处理并缓存中间结果。

```
┌─────────────────────────────────────────────────────────────┐
│                        VideoLingo                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │
│  │  ASR    │ → │  NLP    │ → │   LLM   │ → │   TTS   │    │
│  │ Module  │   │ Module  │   │ Module  │   │ Module  │    │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘    │
│       ↓             ↓             ↓             ↓          │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │
│  │Backend  │   │spaCy    │   │OpenAI   │   │Backend  │    │
│  │Abstract │   │Utils    │   │Compatible│  │Abstract │    │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Config & Cache Layer                   │   │
│  │         (config.yaml + output/ cache)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              UI Layer (Streamlit)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 核心设计原则

### 1. 流水线架构

每个处理步骤都是独立的模块，按顺序执行：

- 输入 → 上一步的输出
- 输出 → 下一步的输入 + 缓存文件
- 失败 → 可从任意断点恢复

### 2. 后端抽象

ASR 和 TTS 采用统一接口，支持多种后端：

```python
# ASR 后端选择
whisper_runtime = load_key("whisper.runtime")
# local → whisperX_local.py
# cloud → whisperX_302.py
# elevenlabs → elevenlabs_asr.py

# TTS 后端选择
tts_method = load_key("tts_method")
# azure_tts → azure_tts.py
# openai_tts → openai_tts.py
# edge_tts → edge_tts.py
# ...
```

### 3. 配置驱动

所有行为通过 `config.yaml` 配置：

```python
# 线程安全的配置读写
value = load_key("path.to.key")
update_key("path.to.key", new_value)
```

### 4. 缓存优先

LLM 调用结果自动缓存：

```python
# 相同 prompt 直接返回缓存
result = ask_gpt(prompt, resp_type="json", log_title="translate")
# 缓存位置：output/gpt_log/translate.json
```

## 15 步处理管线

### 阶段一：视频处理与转录（步骤 1-2）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: _1_ytdlp.py - 视频下载                               │
├─────────────────────────────────────────────────────────────┤
│ 输入：YouTube URL 或本地文件                                │
│ 输出：output/video.mp4                                      │
│                                                               │
│ 功能：                                                        │
│   • yt-dlp 视频下载                                         │
│   • 分辨率选择 (360/1080/best)                              │
│   • Cookies 支持（会员视频）                                 │
│   • 文件名清理                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: _2_asr.py - 语音识别                                 │
├─────────────────────────────────────────────────────────────┤
│ 输入：output/video.mp4                                      │
│ 输出：output/log/asr_result.json                            │
│                                                               │
│ 子流程：                                                      │
│   1. 音频提取 (ffmpeg)                                       │
│   2. 可选：Demucs 人声分离                                   │
│   3. 音频分段（长音频处理）                                   │
│   4. WhisperX 转录与对齐                                     │
│   5. 结果合并与保存                                          │
│                                                               │
│ 后端选择：                                                    │
│   • local: whisperX_local.py                                │
│   • cloud: whisperX_302.py                                  │
│   • elevenlabs: elevenlabs_asr.py                            │
└─────────────────────────────────────────────────────────────┘
```

**ASR 数据格式**：

```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello world",
      "words": [
        {"start": 0.0, "end": 0.5, "word": "Hello"},
        {"start": 0.6, "end": 1.5, "word": "world"}
      ]
    }
  ]
}
```

### 阶段二：句子分割（步骤 3）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3.1: _3_1_split_nlp.py - NLP 分割                       │
├─────────────────────────────────────────────────────────────┤
│ 输入：output/log/asr_result.json                            │
│ 输出：output/log/split_nlp.json                             │
│                                                               │
│ spaCy 分割流程：                                              │
│   1. 加载对应语言的 spaCy 模型                               │
│   2. 按标点符号分割 (split_by_mark.py)                       │
│   3. 按逗号分割 (split_by_comma.py)                         │
│   4. 按连接词分割 (split_by_connector.py)                   │
│   5. 分割过长句子 (split_long_by_root.py)                   │
│                                                               │
│ 支持语言：en, zh, ja, ru, fr, de, es, it                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3.2: _3_2_split_meaning.py - 语义分割                   │
├─────────────────────────────────────────────────────────────┤
│ 输入：output/log/split_nlp.json                             │
│ 输出：output/log/split_result.json                          │
│                                                               │
│ 功能：使用 LLM 对长句进行语义分割                            │
│   • 分析句子结构                                            │
│   • 生成两种分割方案                                         │
│   • 选择最佳方案                                            │
│   • 确保每部分少于 max_split_length 词                      │
└─────────────────────────────────────────────────────────────┘
```

### 阶段三：翻译（步骤 4-5）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 4.1: _4_1_summarize.py - 摘要与术语提取                 │
├─────────────────────────────────────────────────────────────┤
│ 输入：output/log/split_result.json                          │
│ 输出：output/log/terminology.json                           │
│                                                               │
│ 功能：                                                        │
│   • 生成视频摘要（两句话）                                   │
│   • 提取专业术语和名称                                       │
│   • 为每个术语提供翻译和注释                                 │
│   • 支持自定义术语合并 (custom_terms.xlsx)                  │
│                                                               │
│ 输出格式：                                                    │
│ {                                                            │
│   "theme": "视频主题摘要",                                    │
│   "terms": [                                                │
│     {"src": "Machine Learning",                              │
│      "tgt": "机器学习",                                       │
│      "note": "AI 的核心技术"}                                 │
│   ]                                                          │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4.2: _4_2_translate.py - 翻译                           │
├─────────────────────────────────────────────────────────────┤
│ 输入：output/log/split_result.json + terminology.json       │
│ 输出：output/log/translation_result.xlsx                    │
│                                                               │
│ 两步翻译流程：                                                │
│                                                               │
│ 1. Faithfulness (忠实翻译)                                   │
│    • 准确传达原文含义                                        │
│    • 保持术语一致性                                          │
│    • 考虑上下文关系                                          │
│                                                               │
│ 2. Expressiveness (表达优化)                                 │
│    • 分析直译问题                                            │
│    • 优化语言流畅度                                          │
│    • 适配目标语言文化                                        │
│                                                               │
│ 配置控制：                                                    │
│   • reflect_translate: 是否启用第二步                        │
│   • summary_length: 上下文摘要长度                           │
└─────────────────────────────────────────────────────────────┘
```

### 阶段四：字幕生成（步骤 5-7）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 5: _5_split_sub.py - 字幕分割                           │
├─────────────────────────────────────────────────────────────┤
│ 输入：translation_result.xlsx + asr_result.json             │
│ 输出：output/log/split_for_sub.json                         │
│                                                               │
│ 功能：                                                        │
│   • 分割过长的翻译字幕                                       │
│   • 与源字幕对齐                                            │
│   • 使用 LLM 确保分割合理                                    │
│   • 考虑目标语言的长度系数                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: _6_gen_sub.py - 字幕生成                             │
├─────────────────────────────────────────────────────────────┤
│ 输入：split_for_sub.json + asr_result.json                  │
│ 输出：output/srt_files/*.srt                                │
│                                                               │
│ 功能：                                                        │
│   • 对齐翻译与源字幕时间戳                                   │
│   • 清理文本（移除多余空格）                                 │
│   • 格式化为 SRT                                            │
│   • 处理小间隙（合并相近字幕）                               │
│   • 生成多种格式：                                           │
│     - 源语言字幕                                             │
│     - 翻译字幕                                               │
│     - 双语字幕                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7: _7_sub_into_vid.py - 字幕烧录                        │
├─────────────────────────────────────────────────────────────┤
│ 输入：srt_files/*.srt + video.mp4                           │
│ 输出：output/output_sub.mp4                                 │
│                                                               │
│ 功能：                                                        │
│   • 使用 ffmpeg 烧录字幕                                     │
│   • 支持自定义样式                                           │
│   • 可选 GPU 加速 (h264_nvenc)                              │
│   • 双字幕布局（上下排列）                                    │
│                                                               │
│ 配置：                                                        │
│   • burn_subtitles: 是否烧录                                 │
│   • ffmpeg_gpu: 是否使用 GPU                                 │
└─────────────────────────────────────────────────────────────┘
```

### 阶段五：配音（步骤 8-12）

```
┌─────────────────────────────────────────────────────────────┐
│ Step 8.1: _8_1_audio_task.py - 音频任务生成                  │
├─────────────────────────────────────────────────────────────┤
│ 输入：srt_files/*.srt                                       │
│ 输出：output/log/_8_1_AUDIO_TASK.xlsx                       │
│                                                               │
│ 功能：                                                        │
│   • 解析 SRT 文件                                            │
│   • 合并短字幕                                               │
│   • 清理文本（TTS 优化）                                     │
│   • 根据时长裁剪过长的文本                                   │
│   • 估计音频时长                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 8.2: _8_2_dub_chunks.py - 配音分块                      │
├─────────────────────────────────────────────────────────────┤
│ 输入：_8_1_AUDIO_TASK.xlsx                                  │
│ 输出：更新后的 _8_1_AUDIO_TASK.xlsx                         │
│                                                               │
│ 功能：                                                        │
│   • 分析时间间隙                                             │
│   • 计算语速                                                 │
│   • 确定最佳切分点                                          │
│   • 合并相邻短句                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 9: _9_refer_audio.py - 参考音频提取                     │
├─────────────────────────────────────────────────────────────┤
│ 输入：_8_1_AUDIO_TASK.xlsx + vocal.wav                      │
│ 输出：output/audio/segs/*.wav                               │
│                                                               │
│ 功能：                                                        │
│   • 从原音频中提取参考片段                                   │
│   • 用于支持声音克隆的 TTS 引擎                               │
│   • GPT-SoVITS, F5-TTS, Fish-TTS 等                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 10: _10_gen_audio.py - 音频生成                         │
├─────────────────────────────────────────────────────────────┤
│ 输入：_8_1_AUDIO_TASK.xlsx                                  │
│ 输出：output/audio_segments/*.wav                           │
│                                                               │
│ 功能：                                                        │
│   • 调用 TTS 后端生成音频                                    │
│   • 根据目标时长调整播放速度                                 │
│   • 使用 ffmpeg atempo 滤镜                                  │
│   • 并行处理（ThreadPoolExecutor）                           │
│                                                               │
│ 速度调整：                                                    │
│   min: 1.0（不加速）                                         │
│   accept: 1.2（可接受）                                      │
│   max: 1.4（最大）                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 11: _11_merge_audio.py - 音频合并                       │
├─────────────────────────────────────────────────────────────┤
│ 输入：audio_segments/*.wav + _8_1_AUDIO_TASK.xlsx           │
│ 输出：output/dub.wav + output/dub.srt                       │
│                                                               │
│ 功能：                                                        │
│   • 按时间顺序合并音频片段                                   │
│   • 插入静音（根据字幕间隙）                                 │
│   • 生成对应的 SRT 文件                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 12: _12_dub_to_vid.py - 视频合成                        │
├─────────────────────────────────────────────────────────────┤
│ 输入：video.mp4 + dub.wav + background.mp3                  │
│ 输出：output/output_dub.mp4                                 │
│                                                               │
│ 功能：                                                        │
│   • 合并视频、配音、背景音乐                                 │
│   • 可选：烧录字幕                                           │
│   • 音频归一化                                              │
│   • 使用 ffmpeg 处理                                         │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块

### LLM 接口层 (core/utils/ask_gpt.py)

```python
def ask_gpt(prompt, resp_type=None, valid_def=None, log_title="default"):
    """
    统一的 LLM 调用接口

    特性：
    - 文件缓存（相同 prompt 直接返回）
    - JSON 修复（json_repair）
    - 自定义验证
    - 自动重试（@except_handler）
    - 日志记录
    """
```

**缓存机制**：

```python
# 检查缓存
cached = _load_cache(prompt, resp_type, log_title)
if cached:
    return cached

# 调用 API
resp = call_api(...)

# 保存缓存
_save_cache(model, prompt, resp_content, resp_type, resp, log_title)
```

### 配置管理 (core/utils/config_utils.py)

```python
# 线程安全的配置读写
def load_key(key):
    """支持点号路径：'api.key' -> data['api']['key']"""
    with lock:
        with open(CONFIG_PATH, 'r') as file:
            data = yaml.load(file)
    # ... 遍历路径获取值

def update_key(key, new_value):
    """原子性更新配置，保留格式"""
```

### Prompt 管理 (core/prompts.py)

所有 LLM Prompt 集中管理：

```python
# 句子分割 Prompt
def get_split_prompt(sentence, num_parts=2, word_limit=20)

# 摘要 Prompt
def get_summary_prompt(source_content, custom_terms_json=None)

# 翻译 Prompt
def get_prompt_faithfulness(lines, shared_prompt)
def get_prompt_expressiveness(faithfulness_result, lines, shared_prompt)

# 字幕对齐 Prompt
def get_align_prompt(src_sub, tr_sub, src_part)

# TTS 文本清理 Prompt
def get_subtitle_trim_prompt(text, duration)
def get_correct_text_prompt(text)
```

## 数据流

### 主要中间文件

```
output/
├── video.mp4                    # 输入视频
├── audio.wav                    # 提取的音频
├── vocal.wav                    # 分离的人声
├── background.mp3               # 分离的背景音乐
├── log/
│   ├── asr_result.json         # ASR 结果（词级对齐）
│   ├── split_nlp.json          # NLP 分割结果
│   ├── split_result.json       # 最终分割结果
│   ├── terminology.json        # 提取的术语表
│   ├── translation_result.xlsx # 翻译结果
│   ├── split_for_sub.json      # 字幕分割
│   ├── gpt_log/                # LLM 调用缓存
│   └── _8_1_AUDIO_TASK.xlsx    # 音频任务表
├── srt_files/
│   ├── en.srt                  # 源语言字幕
│   ├── zh-CN.srt               # 翻译字幕
│   └── bilingual.srt           # 双语字幕
├── audio/
│   ├── segs/                   # 参考音频
│   └── segments/               # TTS 生成的音频
├── dub.wav                      # 合并的配音
├── dub.srt                      # 配音字幕
├── output_sub.mp4              # 带字幕的视频
└── output_dub.mp4              # 带配音的视频
```

### 断点续传

每个步骤检查输出文件是否存在：

```python
@check_file_exists("output/log/asr_result.json")
def transcribe():
    # 如果文件存在，跳过执行
    ...
```

## 扩展点

### 添加新的 ASR 后端

1. 在 `core/asr_backend/` 创建新文件
2. 实现统一的返回格式
3. 在 `config.yaml` 添加 `whisper.runtime` 选项
4. 在 `_2_asr.py` 添加路由逻辑

### 添加新的 TTS 后端

1. 在 `core/tts_backend/` 创建新文件
2. 实现接口函数
3. 在 `config.yaml` 添加 `tts_method` 选项
4. 在 `tts_main.py` 添加路由逻辑

```python
# TTS 后端接口示例
def tts(text, output_path, voice="default", refer_audio=None):
    """
    生成 TTS 音频

    参数：
        text: 要合成的文本
        output_path: 输出 WAV 文件路径
        voice: 声音名称
        refer_audio: 参考音频路径（可选，用于声音克隆）

    返回：
        成功返回 output_path，失败抛出异常
    """
```

## 下一步

- 📖 阅读 [翻译原理](advanced/translation.md) 深入了解翻译系统
- 🔧 阅读 [开发指南](development.md) 学习如何开发
- 🔌 阅读 [TTS 后端扩展](advanced/tts-backend.md) 了解如何添加 TTS 引擎
