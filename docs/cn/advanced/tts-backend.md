# TTS 后端扩展

> 如何为 VideoLingo 添加自定义 TTS 引擎

## 学习目标

完成本教程后，你将能够：
- 理解 TTS 后端接口设计
- 实现自定义 TTS 引擎
- 集成到 VideoLingo 系统

## TTS 架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                     TTS 调用流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  _10_gen_audio.py                                            │
│       │                                                       │
│       ▼                                                       │
│  tts_main.py (统一调度)                                       │
│       │                                                       │
│       ├─→ 文本清理 (get_correct_text_prompt)                 │
│       │                                                       │
│       ├─→ 后端选择 (load_key("tts_method"))                   │
│       │                                                       │
│       └─→ 后端调用                                           │
│              │                                                │
│              ├─→ azure_tts.py                                │
│              ├─→ openai_tts.py                               │
│              ├─→ edge_tts.py                                 │
│              ├─→ gpt_sovits_tts.py                           │
│              ├─→ sf_fish_tts.py                              │
│              └─→ custom_tts.py  ← 你的实现                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## TTS 后端接口

### 标准接口定义

所有 TTS 后端必须实现以下接口：

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    """
    TTS 后端标准接口

    参数：
        text: 要合成的文本（已清理，仅保留基本标点）
        output_path: 输出 WAV 文件路径
        **kwargs: 额外参数，根据后端需求定义
            - voice: 声音名称（常用）
            - refer_wav: 参考音频路径（声音克隆类 TTS）

    返回：
        output_path（成功时）
        或抛出异常（失败时）

    异常：
        所有失败情况都应抛出异常，由 tts_main.py 处理
        会自动重试和错误日志记录
    """
```

## 实现步骤

### 步骤 1：创建后端文件

在 `core/tts_backend/` 创建新文件：

```bash
touch core/tts_backend/my_tts.py
```

### 步骤 2：实现 TTS 函数

```python
# ------------
# My TTS Backend
# ------------
import os
from pathlib import Path

def tts(text: str, output_path: str, **kwargs) -> str:
    """
    My Custom TTS Backend

    额外参数：
        voice: 声音名称（必需）
        api_key: API 密钥（必需）
        speed: 语速（可选，默认 1.0）
    """
    # 获取参数
    voice = kwargs.get('voice', 'default')
    api_key = kwargs.get('api_key')
    speed = kwargs.get('speed', 1.0)

    # 验证参数
    if not api_key:
        raise ValueError("api_key is required")

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 调用 TTS API
    try:
        # 示例：调用 HTTP API
        import requests

        response = requests.post(
            'https://api.mytts.com/generate',
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'text': text,
                'voice': voice,
                'speed': speed
            },
            timeout=60
        )
        response.raise_for_status()

        # 保存音频
        with open(output_path, 'wb') as f:
            f.write(response.content)

        return output_path

    except requests.RequestException as e:
        raise Exception(f"My TTS API error: {e}")

# ------------
# 本地测试
# ------------
if __name__ == "__main__":
    result = tts(
        text="Hello, world!",
        output_path="test_output.wav",
        voice="my-voice",
        api_key="your-api-key"
    )
    print(f"Generated: {result}")
```

### 步骤 3：添加配置

在 `config.yaml` 添加配置：

```yaml
tts_method: 'my_tts'

my_tts:
  api_key: 'your-api-key'
  voice: 'default-voice'
  speed: 1.0
```

### 步骤 4：集成到 tts_main.py

编辑 `core/tts_backend/tts_main.py`，添加路由：

```python
# 在后端路由部分添加
elif load_key("tts_method") == "my_tts":
    from core.tts_backend import my_tts
    result = my_tts.tts(cleaned_text, output_path,
                        voice=load_key("my_tts.voice"),
                        api_key=load_key("my_tts.api_key"),
                        speed=load_key("my_tts.speed"))
```

### 步骤 5：添加 Streamlit 配置

编辑 `core/st_utils/sidebar_setting.py`：

```python
# 在 TTS 配置区域添加
with st.expander("My TTS"):
    st.selectbox(
        "声音",
        ['voice-1', 'voice-2', 'voice-3'],
        key='my_tts.voice'
    )
    st.text_input(
        "API 密钥",
        type="password",
        key='my_tts.api_key'
    )
    st.slider(
        "语速",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        key='my_tts.speed'
    )
```

## 高级功能实现

### 支持参考音频（声音克隆）

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    refer_wav = kwargs.get('refer_wav')

    if refer_wav and not os.path.exists(refer_wav):
        raise FileNotFoundError(f"Refer audio not found: {refer_wav}")

    # 使用参考音频
    if refer_wav:
        # 调用支持声音克隆的 API
        with open(refer_wav, 'rb') as f:
            files = {'reference': f}
            # ... API 调用

    return output_path
```

### 支持流式输出

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    # 流式生成音频
    response = requests.get(
        'https://api.mytts.com/stream',
        params={'text': text},
        stream=True
    )

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return output_path
```

### 音频后处理

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    # 生成音频
    temp_path = output_path + ".temp.wav"
    generate_audio(text, temp_path)

    # 后处理：音量归一化
    from pydub import AudioSegment
    audio = AudioSegment.from_file(temp_path)
    audio = audio.normalize()

    # 后处理：去除静音
    audio = remove_silence(audio)

    audio.export(output_path, format="wav")
    os.remove(temp_path)

    return output_path
```

## 测试

### 单元测试

```python
import pytest
from core.tts_backend.my_tts import tts

def test_my_tts_basic():
    """测试基本功能"""
    result = tts(
        text="Test",
        output_path="/tmp/test.wav",
        voice="default",
        api_key="test-key"
    )
    assert os.path.exists(result)
    assert result.endswith(".wav")

def test_my_tts_no_api_key():
    """测试缺少 API 密钥"""
    with pytest.raises(ValueError, match="api_key is required"):
        tts(
            text="Test",
            output_path="/tmp/test.wav"
        )
```

### 集成测试

```bash
# 1. 配置测试 API 密钥
update_key('tts_method', 'my_tts')
update_key('my_tts.api_key', 'test-key')

# 2. 运行完整流程
python -m core._10_gen_audio

# 3. 检查输出
ls output/audio_segments/
```

## 最佳实践

### 1. 错误处理

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    try:
        # TTS 逻辑
        pass
    except requests.Timeout:
        raise Exception("TTS request timeout")
    except requests.HTTPError as e:
        raise Exception(f"TTS API error: {e.response.status_code}")
    except IOError as e:
        raise Exception(f"Failed to save audio: {e}")
```

### 2. 参数验证

```python
def tts(text: str, output_path: str, **kwargs) -> str:
    # 验证输入
    if not text or not text.strip():
        raise ValueError("Text is empty")

    if not output_path or not output_path.endswith('.wav'):
        raise ValueError("Output path must be a .wav file")

    # 验证必需参数
    required = ['voice', 'api_key']
    for param in required:
        if param not in kwargs or not kwargs[param]:
            raise ValueError(f"{param} is required")

    # ... TTS 逻辑
```

### 3. 日志记录

```python
from rich.console import Console

console = Console()

def tts(text: str, output_path: str, **kwargs) -> str:
    console.print(f"[cyan]My TTS:[/] Processing {len(text)} chars")

    # ... TTS 逻辑

    console.print(f"[green]My TTS:[/] Generated {output_path}")
    return output_path
```

### 4. 缓存支持

```python
import hashlib
import os

def tts(text: str, output_path: str, **kwargs) -> str:
    # 生成缓存键
    cache_key = hashlib.md5(
        f"{text}{kwargs.get('voice')}".encode()
    ).hexdigest()
    cache_path = f"_model_cache/tts/{cache_key}.wav"

    # 检查缓存
    if os.path.exists(cache_path):
        import shutil
        shutil.copy(cache_path, output_path)
        return output_path

    # 生成音频
    generate_audio(text, output_path)

    # 保存到缓存
    os.makedirs("_model_cache/tts", exist_ok=True)
    shutil.copy(output_path, cache_path)

    return output_path
```

## 示例：完整的自定义 TTS 后端

```python
# ------------
# Custom TTS Backend Example
# ------------
import os
import requests
from pathlib import Path
from rich.console import Console

console = Console()

def tts(text: str, output_path: str, **kwargs) -> str:
    """
    Custom TTS Backend with voice cloning support

    配置参数：
        api_key: API 密钥（必需）
        voice: 声音 ID 或名称（必需）
        refer_wav: 参考音频路径（可选，用于声音克隆）
        speed: 语速 0.5-2.0（可选，默认 1.0）
        stability: 稳定性 0-1（可选，默认 0.5）
    """
    # 参数提取与验证
    api_key = kwargs.get('api_key')
    voice = kwargs.get('voice')

    if not api_key:
        raise ValueError("api_key is required")
    if not voice:
        raise ValueError("voice is required")

    speed = kwargs.get('speed', 1.0)
    stability = kwargs.get('stability', 0.5)
    refer_wav = kwargs.get('refer_wav')

    # 验证参考音频
    if refer_wav and not os.path.exists(refer_wav):
        raise FileNotFoundError(f"Refer audio not found: {refer_wav}")

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # 准备 API 请求
    url = "https://api.customtts.com/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice": voice,
        "speed": speed,
        "stability": stability
    }

    console.print(f"[cyan]Custom TTS:[/] Generating audio for {len(text)} chars")

    try:
        # 有参考音频：使用声音克隆
        if refer_wav:
            with open(refer_wav, 'rb') as f:
                files = {'reference': f}
                data = {k: v for k, v in payload.items() if k != 'voice'}

                response = requests.post(
                    f"{url}/clone",
                    headers={"Authorization": f"Bearer {api_key}"},
                    data=data,
                    files=files,
                    timeout=120
                )
        # 无参考音频：使用预设声音
        else:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )

        response.raise_for_status()

        # 保存音频
        with open(output_path, 'wb') as f:
            f.write(response.content)

        console.print(f"[green]Custom TTS:[/] Generated {output_path}")
        return output_path

    except requests.Timeout:
        raise Exception("TTS request timeout ( >120s )")
    except requests.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            raise Exception("Invalid API key")
        elif status == 429:
            raise Exception("Rate limit exceeded")
        else:
            raise Exception(f"TTS API error: {status}")
    except Exception as e:
        raise Exception(f"TTS failed: {str(e)}")


if __name__ == "__main__":
    # 测试
    result = tts(
        text="Hello, this is a test.",
        output_path="test_output.wav",
        api_key="your-api-key",
        voice="default",
        speed=1.0
    )
    print(f"Generated: {result}")
```

## 下一步

- 🔌 阅读 [ASR 后端扩展](asr-backend.md) 学习添加 ASR 引擎
- 📖 阅读 [API 参考](../api-reference.md) 了解其他接口
