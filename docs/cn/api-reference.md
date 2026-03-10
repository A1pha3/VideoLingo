# API 参考

> VideoLingo 核心模块 API 文档

## 学习目标

完成本教程后，你将能够：
- 理解核心模块的 API 接口
- 在自定义代码中调用 VideoLingo 功能
- 正确处理返回值和异常

## 目录

- [配置管理 API](#配置管理-api)
- [LLM 交互 API](#llm-交互-api)
- [ASR 后端 API](#asr-后端-api)
- [TTS 后端 API](#tts-后端-api)
- [处理流程 API](#处理流程-api)
- [工具函数 API](#工具函数-api)

---

## 配置管理 API

### 模块：`core.utils.config_utils`

### `load_key(key)`

从配置文件读取值。

```python
def load_key(key: str) -> Any
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `key` | `str` | 配置键路径，使用点号分隔（如 `'api.key'`） |

**返回**：配置值（类型取决于配置）

**异常**：
- `KeyError`：键不存在

**示例**：

```python
from core.utils.config_utils import load_key

# 读取简单配置
api_key = load_key('api.key')
target_lang = load_key('target_language')

# 读取嵌套配置
model = load_key('whisper.model')
voice = load_key('azure_tts.voice')
```

### `update_key(key, new_value)`

更新配置值。

```python
def update_key(key: str, new_value: Any) -> bool
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `key` | `str` | 配置键路径 |
| `new_value` | `Any` | 新值 |

**返回**：`True` 表示成功，`False` 表示失败

**异常**：
- `KeyError`：键不存在

**示例**：

```python
from core.utils.config_utils import update_key

# 更新配置
update_key('target_language', '日本語')
update_key('whisper.model', 'large-v3-turbo')
update_key('max_workers', 8)
```

### `get_joiner(language)`

获取语言的文本连接符。

```python
def get_joiner(language: str) -> str
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `language` | `str` | 语言代码 |

**返回**：`" "`（空格）或 `""`（无空格）

**示例**：

```python
from core.utils.config_utils import get_joiner

get_joiner('en')  # 返回 ' '
get_joiner('zh')  # 返回 ''
```

---

## LLM 交互 API

### 模块：`core.utils.ask_gpt`

### `ask_gpt(prompt, resp_type, valid_def, log_title)`

调用 LLM 并获取响应。

```python
def ask_gpt(
    prompt: str,
    resp_type: str = None,
    valid_def: Callable = None,
    log_title: str = "default"
) -> Any
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | `str` | 完整的提示词 |
| `resp_type` | `str` | 可选，`"json"` 表示期望 JSON 响应 |
| `valid_def` | `Callable` | 可选，响应验证函数 |
| `log_title` | `str` | 缓存文件名，默认 `"default"` |

**返回**：
- `resp_type="json"`：解析后的 Python 对象（dict/list）
- 其他：原始文本字符串

**异常**：
- `ValueError`：API 密钥未设置或响应验证失败
- 其他 OpenAI API 异常

**验证函数格式**：

```python
def validate_response(resp):
    """
    返回格式：
    {
        'status': 'success' | 'error',
        'message': '错误描述'
    }
    """
    if 'required_field' not in resp:
        return {'status': 'error', 'message': '缺少必需字段'}
    return {'status': 'success'}
```

**示例**：

```python
from core.utils.ask_gpt import ask_gpt

# 文本响应
result = ask_gpt("将以下文本翻译成中文：Hello World")

# JSON 响应
prompt = """
请分析以下文本：
```json
{
    "sentiment": "positive/negative",
    "keywords": ["keyword1", "keyword2"]
}
```
"""
result = ask_gpt(prompt, resp_type="json")

# 带验证
def validate(data):
    if 'sentiment' not in data:
        return {'status': 'error', 'message': '缺少 sentiment 字段'}
    return {'status': 'success'}

result = ask_gpt(prompt, resp_type="json", valid_def=validate)
```

**缓存行为**：

```python
# 首次调用：发送 API 请求
result1 = ask_gpt("翻译：Hello", log_title="test")

# 相同 prompt：直接返回缓存
result2 = ask_gpt("翻译：Hello", log_title="test")
# 输出：use cache response
```

---

## ASR 后端 API

### 模块：`core.asr_backend.whisperX_local`

### `transcribe_local(audio_path, whisper_model, language)`

本地 WhisperX 转录。

```python
def transcribe_local(
    audio_path: str,
    whisper_model: str = "large-v3",
    language: str = None
) -> dict
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `audio_path` | `str` | 音频文件路径 |
| `whisper_model` | `str` | Whisper 模型名称 |
| `language` | `str` | 语言代码，`None` 表示自动检测 |

**返回**：

```python
{
    "segments": [
        {
            "start": float,      # 开始时间（秒）
            "end": float,        # 结束时间（秒）
            "text": str,         # 文本
            "words": [           # 词级对齐
                {
                    "start": float,
                    "end": float,
                    "word": str,
                    "score": float
                }
            ]
        }
    ],
    "language": str  # 检测到的语言
}
```

### 模块：`core.asr_backend.audio_preprocess`

### `extract_audio(video_path, output_path)`

从视频提取音频。

```python
def extract_audio(video_path: str, output_path: str) -> str
```

### `split_audio(audio_path, max_duration=1800)`

分割长音频文件。

```python
def split_audio(audio_path: str, max_duration: int = 1800) -> list[str]
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `audio_path` | `str` | 音频文件路径 |
| `max_duration` | `int` | 最大时长（秒），默认 30 分钟 |

**返回**：分割后的音频文件路径列表

### `normalize_audio(audio_path, output_path)`

音频音量归一化。

```python
def normalize_audio(audio_path: str, output_path: str) -> str
```

---

## TTS 后端 API

### 模块：`core.tts_backend.tts_main`

### `tts(text, output_path, refer_wav=None)`

统一的 TTS 接口。

```python
def tts(
    text: str,
    output_path: str,
    refer_wav: str = None
) -> str
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `text` | `str` | 要合成的文本 |
| `output_path` | `str` | 输出 WAV 文件路径 |
| `refer_wav` | `str` | 可选，参考音频路径（用于声音克隆） |

**返回**：输出文件路径

**异常**：TTS 失败时抛出异常

**行为**：
1. 根据 `config.yaml` 的 `tts_method` 选择后端
2. 清理文本（移除特殊字符）
3. 调用对应的 TTS 引擎
4. 验证音频时长
5. 失败时自动重试

### TTS 后端接口

所有 TTS 后端应实现以下接口：

```python
def tts_backend(text: str, output_path: str, **kwargs) -> str:
    """
    TTS 后端标准接口

    参数：
        text: 要合成的文本
        output_path: 输出 WAV 文件路径
        **kwargs: 额外参数（如 voice, refer_audio 等）

    返回：
        output_path

    异常：
        失败时抛出异常，由 tts_main.py 处理
    """
```

### 各后端额外参数

| 后端 | 额外参数 |
|------|----------|
| `azure_tts` | `voice` |
| `openai_tts` | `voice` |
| `edge_tts` | `voice` |
| `gpt_sovits` | `refer_wav`, `character`, `refer_mode` |
| `sf_fish_tts` | `voice`, `mode`, `refer_wav` |
| `fish_tts` | `character`, `refer_wav` |

### 模块：`core.tts_backend.estimate_duration`

### `estimate_text_duration(text, language)`

估计文本朗读时长。

```python
def estimate_text_duration(text: str, language: str) -> float
```

**返回**：估计的秒数

---

## 处理流程 API

### 模块：`core`（主入口）

### 步骤 1：视频下载

```python
from core import _1_ytdlp

# 下载 YouTube 视频
_1_ytdlp.download_video_ytdlp(url, resolution="1080")

# 查找视频文件
video_path = _1_ytdlp.find_video_files()
```

### 步骤 2：转录

```python
from core import _2_asr

# 执行转录
_2_asr.transcribe()
```

### 步骤 3-4：分割与翻译

```python
from core import (
    _3_1_split_nlp,
    _3_2_split_meaning,
    _4_1_summarize,
    _4_2_translate
)

# NLP 分割
_3_1_split_nlp.split_by_spacy()

# 语义分割
_3_2_split_meaning.split_sentences_by_meaning()

# 摘要与术语
_4_1_summarize.get_summary()

# 翻译
_4_2_translate.translate_all()
```

### 步骤 5-7：字幕生成

```python
from core import _5_split_sub, _6_gen_sub, _7_sub_into_vid

# 分割字幕
_5_split_sub.split_for_sub_main()

# 生成 SRT
_6_gen_sub.align_timestamp_main()

# 烧录字幕
_7_sub_into_vid.merge_subtitles_to_video()
```

### 步骤 8-12：配音

```python
from core import (
    _8_1_audio_task,
    _8_2_dub_chunks,
    _9_refer_audio,
    _10_gen_audio,
    _11_merge_audio,
    _12_dub_to_vid
)

# 生成音频任务
_8_1_audio_task.gen_audio_task_main()
_8_2_dub_chunks.gen_dub_chunks()

# 提取参考音频
_9_refer_audio.extract_refer_audio_main()

# 生成音频
_10_gen_audio.gen_audio()

# 合并音频
_11_merge_audio.merge_full_audio()

# 合成视频
_12_dub_to_vid.merge_video_audio()
```

---

## 工具函数 API

### 模块：`core.utils.models`

路径常量定义。

```python
# 常用路径
ASR_RESULT_PATH = "output/log/asr_result.json"
SPLIT_RESULT_PATH = "output/log/split_result.json"
TRANSLATION_RESULT_PATH = "output/log/translation_result.xlsx"
AUDIO_TASK_PATH = "output/log/_8_1_AUDIO_TASK.xlsx"
TERMINOLOGY_PATH = "output/log/terminology.json"
```

### 模块：`core.utils.onekeycleanup`

### `cleanup(target_dir=None)`

清理和归档输出文件。

```python
def cleanup(target_dir: str = None) -> None
```

**参数**：
- `target_dir`：归档目录，默认为 `history/视频名/`

**行为**：
1. 获取视频文件名
2. 创建归档目录
3. 移动所有输出文件到归档目录
4. 清空 `output/` 目录

### 模块：`core.utils.delete_retry_dubbing`

### `delete_dubbing_files()`

删除配音相关文件。

```python
def delete_dubbing_files() -> None
```

### 模块：`core.utils.decorator`

### `@except_handler(message, retry=0)`

异常处理装饰器。

```python
from core.utils.decorator import except_handler

@except_handler("处理失败", retry=3)
def my_function():
    # 失败时会自动重试 3 次
    # 每次失败显示 "处理失败 (attempt X/3)"
    pass
```

### `@check_file_exists(file_path)`

文件存在检查装饰器。

```python
from core.utils.decorator import check_file_exists

@check_file_exists("output/result.json")
def process():
    # 如果文件存在，跳过执行
    # 输出：File exists, skipping...
    pass
```

---

## Prompt API

### 模块：`core.prompts`

### `get_split_prompt(sentence, num_parts, word_limit)`

生成句子分割 Prompt。

```python
def get_split_prompt(sentence: str, num_parts: int = 2, word_limit: int = 20) -> str
```

### `get_summary_prompt(source_content, custom_terms_json)`

生成摘要和术语提取 Prompt。

```python
def get_summary_prompt(source_content: str, custom_terms_json: dict = None) -> str
```

### `get_prompt_faithfulness(lines, shared_prompt)`

生成忠实翻译 Prompt。

```python
def get_prompt_faithfulness(lines: str, shared_prompt: str) -> str
```

### `get_prompt_expressiveness(faithfulness_result, lines, shared_prompt)`

生成表达优化 Prompt。

```python
def get_prompt_expressiveness(faithfulness_result: dict, lines: str, shared_prompt: str) -> str
```

### `get_align_prompt(src_sub, tr_sub, src_part)`

生成字幕对齐 Prompt。

```python
def get_align_prompt(src_sub: str, tr_sub: str, src_part: str) -> str
```

### `get_subtitle_trim_prompt(text, duration)`

生成字幕裁剪 Prompt。

```python
def get_subtitle_trim_prompt(text: str, duration: float) -> str
```

---

## 批处理 API

### 模块：`batch.utils.video_processor`

### `process_video(file, dubbing=False, is_retry=False)`

处理单个视频。

```python
def process_video(file: str, dubbing: bool = False, is_retry: bool = False) -> tuple
```

**参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | `str` | 视频文件名或 URL |
| `dubbing` | `bool` | 是否生成配音 |
| `is_retry` | `bool` | 是否为重试 |

**返回**：`(status: bool, error_step: str, error_message: str)`

---

## 错误处理

### 通用异常处理模式

```python
from core.utils.decorator import except_handler
from rich.console import Console

console = Console()

@except_handler("操作失败", retry=3)
def my_operation():
    # 你的代码
    pass

try:
    my_operation()
except Exception as e:
    console.print(f"[red]错误：{e}[/]")
```

### API 错误码

| 错误 | 说明 | 解决方案 |
|------|------|----------|
| `API key is not set` | API 密钥未配置 | 检查 `config.yaml` |
| `CUDA out of memory` | GPU 内存不足 | 减小批处理大小或使用 CPU |
| `File not found` | 文件不存在 | 检查输入路径 |
| `Invalid response format` | LLM 响应格式错误 | 重试或更换模型 |

---

## 自测问题

阅读完 API 参考后，尝试回答以下问题：

1. **如何只执行字幕生成流程，跳过配音？**
   
   <details>
   <summary>点击查看答案</summary>
   只调用步骤 1-7 的函数，不调用步骤 8-12 的配音相关函数。也可以在配置中设置 `dubbing.enabled: false`。
   </details>

2. **`@check_file_exists` 装饰器的作用是什么？**
   
   <details>
   <summary>点击查看答案</summary>
   实现断点续传功能。如果目标文件已存在，则跳过函数执行，直接使用已有结果。这对于长时间处理任务非常有用。
   </details>

3. **如何自定义 LLM Prompt？**
   
   <details>
   <summary>点击查看答案</summary>
   在 `core/prompts.py` 中修改对应的 Prompt 函数。建议保留原有的 JSON 输出格式，以确保后续解析正常工作。
   </details>

## 下一步

- 🔧 阅读 [开发指南](development.md) 学习开发环境搭建
- 🔌 阅读 [TTS 后端扩展](advanced/tts-backend.md) 了解如何添加 TTS 引擎
