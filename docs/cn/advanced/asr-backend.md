# ASR 后端扩展

> 如何为 VideoLingo 添加自定义 ASR 引擎

## 学习目标

完成本教程后，你将能够：
- 理解 ASR 后端接口设计
- 实现自定义 ASR 引擎
- 集成到 VideoLingo 系统

## ASR 架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                     ASR 调用流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  _2_asr.py (ASR 主流程)                                       │
│       │                                                       │
│       ├─→ 音频提取                                           │
│       ├─→ 可选：Demucs 分离                                  │
│       ├─→ 音频分段                                           │
│       │                                                       │
│       └─→ 后端选择 (load_key("whisper.runtime"))              │
│              │                                                │
│              ├─→ whisperX_local.py (本地 WhisperX)            │
│              ├─→ whisperX_302.py (302.ai API)                 │
│              ├─→ elevenlabs_asr.py (ElevenLabs)               │
│              └─→ my_asr.py  ← 你的实现                         │
│                                                               │
│       │                                                       │
│       └─→ 结果合并与保存                                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## ASR 后端接口

### 标准返回格式

所有 ASR 后端必须返回以下格式的字典：

```python
{
    "segments": [
        {
            "start": float,      # 开始时间（秒）
            "end": float,        # 结束时间（秒）
            "text": str,         # 转录文本
            "words": [           # 词级时间戳（可选但推荐）
                {
                    "word": str,      # 单词
                    "start": float,   # 开始时间
                    "end": float,     # 结束时间
                    "score": float    # 置信度（可选）
                }
            ]
        }
    ],
    "language": str  # 检测到的语言代码（ISO 639-1）
}
```

### 标准接口定义

```python
def transcribe(
    audio_path: str,
    language: str = None,
    model: str = "base",
    **kwargs
) -> dict:
    """
    ASR 后端标准接口

    参数：
        audio_path: 输入音频文件路径
        language: 语言代码（None 表示自动检测）
        model: 模型名称
        **kwargs: 额外参数

    返回：
        标准格式的转录结果字典

    异常：
        失败时抛出异常
    """
```

## 实现步骤

### 步骤 1：创建后端文件

在 `core/asr_backend/` 创建新文件：

```bash
touch core/asr_backend/my_asr.py
```

### 步骤 2：实现转录函数

```python
# ------------
# My ASR Backend
# ------------
import os
from pathlib import Path

def transcribe(
    audio_path: str,
    language: str = None,
    model: str = "base",
    **kwargs
) -> dict:
    """
    My Custom ASR Backend

    额外参数：
        api_key: API 密钥（必需）
        endpoint: API 端点（可选）
    """
    # 参数验证
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    api_key = kwargs.get('api_key')
    if not api_key:
        raise ValueError("api_key is required")

    endpoint = kwargs.get('endpoint', 'https://api.myasr.com/v1/transcribe')

    # 调用 ASR API
    try:
        import requests

        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            data = {
                'language': language or 'auto',
                'model': model
            }
            headers = {'Authorization': f'Bearer {api_key}'}

            response = requests.post(
                endpoint,
                headers=headers,
                data=data,
                files=files,
                timeout=300
            )
            response.raise_for_status()
            result = response.json()

        # 转换为标准格式
        return convert_to_standard_format(result)

    except requests.RequestException as e:
        raise Exception(f"My ASR API error: {e}")

def convert_to_standard_format(api_result):
    """将 API 结果转换为 VideoLingo 标准格式"""
    segments = []

    for seg in api_result.get('transcripts', []):
        segment = {
            'start': seg['start_time'],
            'end': seg['end_time'],
            'text': seg['text'],
            'words': []
        }

        # 添加词级时间戳（如果有）
        if 'words' in seg:
            for word in seg['words']:
                segment['words'].append({
                    'word': word['text'],
                    'start': word['start_time'],
                    'end': word['end_time'],
                    'score': word.get('confidence', 1.0)
                })

        segments.append(segment)

    return {
        'segments': segments,
        'language': api_result.get('detected_language', 'en')
    }

# ------------
# 本地测试
# ------------
if __name__ == "__main__":
    result = transcribe(
        audio_path="test_audio.wav",
        language="en",
        model="base",
        api_key="your-api-key"
    )
    print(f"Transcribed {len(result['segments'])} segments")
    print(f"Language: {result['language']}")
```

### 步骤 3：添加配置

在 `config.yaml` 添加配置：

```yaml
whisper:
  runtime: 'my_asr'        # 使用自定义 ASR
  model: 'base'

my_asr:
  api_key: 'your-api-key'
  endpoint: 'https://api.myasr.com/v1/transcribe'
```

### 步骤 4：集成到 _2_asr.py

编辑 `core/_2_asr.py`，添加后端路由：

```python
# 在 ASR 后端选择部分添加
runtime = load_key("whisper.runtime")

if runtime == 'local':
    from core.asr_backend import whisperX_local
    asr_result = whisperX_local.transcribe_local(...)
elif runtime == 'cloud':
    from core.asr_backend import whisperX_302
    asr_result = whisperX_302.transcribe_302(...)
elif runtime == 'elevenlabs':
    from core.asr_backend import elevenlabs_asr
    asr_result = elevenlabs_asr.transcribe_elevenlabs(...)
elif runtime == 'my_asr':
    from core.asr_backend import my_asr
    asr_result = my_asr.transcribe(
        audio_path=audio_file,
        language=load_key("whisper.language"),
        model=load_key("whisper.model"),
        api_key=load_key("my_asr.api_key"),
        endpoint=load_key("my_asr.endpoint")
    )
else:
    raise ValueError(f"Unknown ASR runtime: {runtime}")
```

### 步骤 5：添加 Streamlit 配置

编辑 `core/st_utils/sidebar_setting.py`：

```python
# 在 Whisper 配置区域添加选项
whisper_runtime = st.selectbox(
    "Whisper 运行模式",
    ['local', 'cloud', 'elevenlabs', 'my_asr'],
    format_func=lambda x: {
        'local': '本地 (WhisperX)',
        'cloud': '云端 (302.ai)',
        'elevenlabs': 'ElevenLabs',
        'my_asr': 'My Custom ASR'
    }.get(x, x),
    key='whisper.runtime'
)

# 根据选择显示不同配置
if whisper_runtime == 'my_asr':
    st.text_input(
        "API 密钥",
        type="password",
        key='my_asr.api_key'
    )
    st.text_input(
        "API 端点",
        key='my_asr.endpoint'
    )
```

## 高级功能实现

### 支持音频分段处理

```python
def transcribe_long_audio(
    audio_path: str,
    language: str = None,
    model: str = "base",
    max_duration: int = 1800,
    **kwargs
) -> dict:
    """处理长音频文件"""
    from pydub import AudioSegment

    # 加载音频
    audio = AudioSegment.from_file(audio_path)
    duration_ms = len(audio)

    # 如果音频较短，直接处理
    if duration_ms <= max_duration * 1000:
        return transcribe(audio_path, language, model, **kwargs)

    # 分段处理
    segments = []
    chunk_ms = max_duration * 1000

    for i, start in enumerate(range(0, duration_ms, chunk_ms)):
        end = min(start + chunk_ms, duration_ms)

        # 导出分段
        chunk_path = f"temp_chunk_{i}.wav"
        audio[start:end].export(chunk_path, format="wav")

        # 转录分段
        chunk_result = transcribe(chunk_path, language, model, **kwargs)

        # 调整时间偏移
        offset = start / 1000.0
        for seg in chunk_result['segments']:
            seg['start'] += offset
            seg['end'] += offset
            for word in seg.get('words', []):
                word['start'] += offset
                word['end'] += offset

        segments.extend(chunk_result['segments'])

        # 清理临时文件
        os.remove(chunk_path)

    # 返回合并结果
    return {
        'segments': segments,
        'language': language or 'en'
    }
```

### 支持流式转录

```python
def transcribe_streaming(
    audio_path: str,
    language: str = None,
    **kwargs
) -> dict:
    """流式转录音频"""
    import requests

    api_key = kwargs.get('api_key')
    endpoint = kwargs.get('endpoint', 'https://api.myasr.com/v1/transcribe')

    with open(audio_path, 'rb') as f:
        response = requests.post(
            f"{endpoint}/streaming",
            headers={'Authorization': f'Bearer {api_key}'},
            data={'language': language or 'auto'},
            files={'audio': f},
            stream=True,
            timeout=600
        )

    segments = []
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            # 处理流式返回的片段
            segments.append(chunk)

    return {
        'segments': segments,
        'language': language or 'en'
    }
```

### 支持多语言检测

```python
def detect_language(audio_path: str, api_key: str) -> str:
    """检测音频语言"""
    import requests

    with open(audio_path, 'rb') as f:
        response = requests.post(
            'https://api.myasr.com/v1/detect-language',
            headers={'Authorization': f'Bearer {api_key}'},
            files={'audio': f},
            timeout=60
        )
    response.raise_for_status()
    return response.json()['language']

def transcribe(audio_path: str, language: str = None, **kwargs) -> dict:
    """自动检测语言的转录"""
    if language is None:
        detected = detect_language(audio_path, kwargs.get('api_key'))
        print(f"Detected language: {detected}")
        language = detected

    return transcribe_with_language(audio_path, language, **kwargs)
```

## 测试

### 单元测试

```python
import pytest
from core.asr_backend.my_asr import transcribe

def test_my_asr_basic():
    """测试基本转录功能"""
    result = transcribe(
        audio_path="test_audio.wav",
        language="en",
        api_key="test-key"
    )
    assert 'segments' in result
    assert 'language' in result
    assert len(result['segments']) > 0

def test_my_asr_format():
    """测试返回格式"""
    result = transcribe(
        audio_path="test_audio.wav",
        language="en",
        api_key="test-key"
    )
    segment = result['segments'][0]

    assert 'start' in segment
    assert 'end' in segment
    assert 'text' in segment
    assert isinstance(segment['start'], (int, float))
    assert isinstance(segment['end'], (int, float))
    assert isinstance(segment['text'], str)
```

### 集成测试

```bash
# 1. 配置测试 API 密钥
update_key('whisper.runtime', 'my_asr')
update_key('my_asr.api_key', 'test-key')

# 2. 运行完整流程
python -m core._2_asr

# 3. 检查输出
cat output/log/asr_result.json | python -m json.tool
```

## 最佳实践

### 1. 错误处理

```python
def transcribe(audio_path: str, **kwargs) -> dict:
    try:
        # 转录逻辑
        pass
    except FileNotFoundError:
        raise Exception(f"Audio file not found: {audio_path}")
    except requests.Timeout:
        raise Exception("ASR request timeout")
    except requests.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            raise Exception("Invalid API key")
        elif status == 413:
            raise Exception("Audio file too large")
        else:
            raise Exception(f"ASR API error: {status}")
```

### 2. 音频验证

```python
def validate_audio(audio_path: str):
    """验证音频文件"""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # 检查文件大小
    file_size = os.path.getsize(audio_path)
    max_size = 500 * 1024 * 1024  # 500MB
    if file_size > max_size:
        raise ValueError(f"Audio file too large: {file_size / 1024 / 1024:.1f}MB")

    # 检查音频格式
    try:
        from pydub import AudioSegment
        AudioSegment.from_file(audio_path)
    except Exception as e:
        raise ValueError(f"Invalid audio file: {e}")
```

### 3. 进度回调

```python
def transcribe(
    audio_path: str,
    progress_callback=None,
    **kwargs
) -> dict:
    """支持进度回调的转录"""

    if progress_callback:
        progress_callback(0, "Starting transcription...")

    # ... 处理逻辑

    if progress_callback:
        progress_callback(0.5, "Processing...")

    # ... 更多处理

    if progress_callback:
        progress_callback(1.0, "Complete")

    return result
```

### 4. 结果缓存

```python
import hashlib
import json

def get_cache_key(audio_path: str, language: str, model: str) -> str:
    """生成缓存键"""
    # 使用文件路径、语言和模型的哈希
    key_str = f"{audio_path}:{language}:{model}"
    return hashlib.md5(key_str.encode()).hexdigest()

def transcribe_cached(audio_path: str, **kwargs) -> dict:
    """带缓存的转录"""
    cache_dir = "output/cache/asr"
    os.makedirs(cache_dir, exist_ok=True)

    cache_key = get_cache_key(
        audio_path,
        kwargs.get('language'),
        kwargs.get('model')
    )
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")

    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)

    # 执行转录
    result = transcribe(audio_path, **kwargs)

    # 保存缓存
    with open(cache_file, 'w') as f:
        json.dump(result, f)

    return result
```

## 示例：完整的自定义 ASR 后端

```python
# ------------
# Custom ASR Backend Example
# ------------
import os
import requests
import json
from pathlib import Path
from rich.console import Console

console = Console()

def transcribe(
    audio_path: str,
    language: str = None,
    model: str = "base",
    **kwargs
) -> dict:
    """
    Custom ASR Backend with streaming support

    配置参数：
        api_key: API 密钥（必需）
        endpoint: API 端点（可选）
        streaming: 是否使用流式转录（可选，默认 False）
        chunk_size: 流式分块大小（可选，默认 1024）
    """
    # 参数提取与验证
    api_key = kwargs.get('api_key')
    if not api_key:
        raise ValueError("api_key is required")

    endpoint = kwargs.get('endpoint', 'https://api.customasr.com/v1/transcribe')
    streaming = kwargs.get('streaming', False)

    # 验证音频文件
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    file_size = os.path.getsize(audio_path) / 1024 / 1024
    console.print(f"[cyan]Custom ASR:[/] Processing {audio_path} ({file_size:.1f}MB)")

    try:
        if streaming:
            return transcribe_streaming(audio_path, language, model, api_key, endpoint, kwargs)
        else:
            return transcribe_direct(audio_path, language, model, api_key, endpoint)

    except Exception as e:
        console.print(f"[red]Custom ASR error:[/] {e}")
        raise

def transcribe_direct(
    audio_path: str,
    language: str,
    model: str,
    api_key: str,
    endpoint: str
) -> dict:
    """直接转录模式"""
    with open(audio_path, 'rb') as f:
        files = {'audio': f}
        data = {'language': language or 'auto', 'model': model}
        headers = {'Authorization': f'Bearer {api_key}'}

        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            files=files,
            timeout=300
        )
        response.raise_for_status()
        api_result = response.json()

    return convert_to_standard_format(api_result)

def transcribe_streaming(
    audio_path: str,
    language: str,
    model: str,
    api_key: str,
    endpoint: str,
    kwargs: dict
) -> dict:
    """流式转录模式"""
    chunk_size = kwargs.get('chunk_size', 1024)

    with open(audio_path, 'rb') as f:
        files = {'audio': f}
        data = {'language': language or 'auto', 'model': model, 'stream': True}
        headers = {'Authorization': f'Bearer {api_key}'}

        response = requests.post(
            f"{endpoint}/stream",
            headers=headers,
            data=data,
            files=files,
            stream=True,
            timeout=600
        )

    segments = []
    for line in response.iter_lines(chunk_size=chunk_size):
        if line:
            chunk = json.loads(line)
            if 'segment' in chunk:
                segments.append(chunk['segment'])

    return {'segments': segments, 'language': language or 'en'}

def convert_to_standard_format(api_result: dict) -> dict:
    """将 API 结果转换为标准格式"""
    segments = []

    for seg in api_result.get('segments', []):
        segment = {
            'start': seg.get('start', 0),
            'end': seg.get('end', 0),
            'text': seg.get('text', ''),
            'words': []
        }

        if 'words' in seg:
            for word in seg['words']:
                segment['words'].append({
                    'word': word.get('text', ''),
                    'start': word.get('start', 0),
                    'end': word.get('end', 0),
                    'score': word.get('confidence', 1.0)
                })

        segments.append(segment)

    return {
        'segments': segments,
        'language': api_result.get('language', 'en')
    }

if __name__ == "__main__":
    # 测试
    result = transcribe(
        audio_path="test_audio.wav",
        language="en",
        model="base",
        api_key="your-api-key",
        streaming=True
    )
    print(f"Transcribed {len(result['segments'])} segments")
```

## 下一步

- 🔌 阅读 [TTS 后端扩展](tts-backend.md) 学习添加 TTS 引擎
- 📖 阅读 [API 参考](../api-reference.md) 了解其他接口
