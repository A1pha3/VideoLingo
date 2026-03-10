# 音频处理深入解析

> 音频分离、预处理与后处理系统

## 学习目标

完成本教程后，你将能够：
- 理解音频处理流程
- 配置 Demucs 人声分离
- 优化音频质量
- 解决音频相关问题

## 音频处理架构

```
┌─────────────────────────────────────────────────────────────┐
│                    音频处理流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. 音频提取 (audio_preprocess.py)                           │
│     └── 从视频中提取音频 (ffmpeg)                             │
│                                                               │
│  2. 可选：Demucs 分离 (demucs_vl.py)                         │
│     ├── 人声 → vocal.wav                                     │
│     └── 背景音乐 → background.mp3                            │
│                                                               │
│  3. 音频预处理 (audio_preprocess.py)                          │
│     ├── 音量归一化                                            │
│     ├── 静音检测                                              │
│     └── 分段处理                                              │
│                                                               │
│  4. WhisperX 转录 (whisperX_local.py)                         │
│     └── 使用人声进行转录                                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 音频提取

### 基本提取

```python
from core.asr_backend.audio_preprocess import extract_audio

# 从视频提取音频
audio_path = extract_audio(
    video_path="input.mp4",
    output_path="output/audio.wav"
)
```

### FFmpeg 参数

```bash
# 提取为 WAV（无损）
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav

# 提取为 MP3（有损）
ffmpeg -i input.mp4 -vn -acodec libmp3lame -ar 16000 -ac 1 output.mp3
```

**参数说明**：
- `-vn`：不包含视频
- `-acodec`：音频编码器
- `-ar`：采样率（16kHz 适合语音识别）
- `-ac 1`：单声道

## Demucs 人声分离

### 为什么需要人声分离？

```
原始音频:
├── 人声
└── 背景音乐/噪音

WhisperX 对人声识别效果更好：
├── 有背景音乐 → 准确率 70-80%
└── 仅人声 → 准确率 95%+
```

### 配置 Demucs

```yaml
# config.yaml
demucs: true  # 启用人声分离
```

### 分离模型

VideoLingo 使用 **HTDemucs** 模型：

```python
# core/asr_backend/demucs_vl.py
from demucs import pretrained
from demucs.apply import apply_model

# 加载模型
model = pretrained.get_model('htdemucs')
model = pretrained.ModelLoadingStrategy.LOCAL_ONLY

# 分离音频
sources = apply_model(
    model,
    audio,
    device="cuda"
)
```

**输出**：
- `vocals.wav`：人声
- `no_vocals.wav`：背景音乐和噪音

### 分离质量

| 音频类型 | 分离效果 | 建议 |
|----------|----------|------|
| 对话为主 | 优秀 | 建议启用 |
| 背景音乐强 | 良好 | 建议启用 |
| 纯音乐 | 差 | 不适用 |
| 噪音大 | 中等 | 视情况启用 |

## 音频预处理

### 音量归一化

```python
from pydub import AudioSegment
from pydub.effects import normalize

audio = AudioSegment.from_file("input.wav")
normalized = normalize(audio, headroom=0.1)
normalized.export("output.wav", format="wav")
```

### 静音检测

```python
from pydub.silence import detect_nonsilent

# 检测非静音片段
nonsilent = detect_nonsilent(
    audio,
    min_silence_len=500,  # 最小静音长度 (ms)
    silence_thresh=-40,   # 静音阈值 (dB)
    seek_step=100         # 搜索步长 (ms)
)
```

### 分段处理

```python
def split_audio(
    audio_path: str,
    max_duration: int = 1800
) -> list:
    """将长音频分段

    Args:
        audio_path: 音频文件路径
        max_duration: 每段最大时长（秒），默认 30 分钟

    Returns:
        分段文件路径列表
    """
```

## 音频格式

### 支持的输入格式

```
视频: mp4, mov, avi, mkv, flv, wmv, webm
音频: wav, mp3, flac, m4a, ogg
```

### 推荐的输出格式

```
WhisperX 转录: WAV (16kHz, 单声道, PCM)
TTS 生成: WAV (多种采样率)
最终视频: AAC (压缩)
```

## FFmpeg 技巧

### GPU 加速

```bash
# 使用 NVIDIA GPU 加速
ffmpeg -hwaccel cuda -i input.mp4 -acodec pcm_s16le output.wav

# NVENC 编码
ffmpeg -i input.mp4 -c:v h264_nvenc -c:a aac output.mp4
```

### 批处理

```bash
# 批量提取音频
for file in *.mp4; do
    ffmpeg -i "$file" -vn -acodec pcm_s16le -ar 16000 -ac 1 "${file%.mp4}.wav"
done
```

### 音频分析

```bash
# 获取音频信息
ffprobe -i audio.wav -show_streams -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration

# 检测静音
ffmpeg -i audio.wav -af silencedetect=noise=-30dB:duration=1 -f null -
```

## 常见问题

### Q: Demucs 处理太慢？

**原因**：CPU 模式或音频太长

**解决方案**：
```bash
# 使用 GPU
CUDA_VISIBLE_DEVICES=0 python -m core._2_asr

# 或跳过 Demucs
demucs: false
```

### Q: 音频质量差？

**检查**：
```bash
# 查看音频信息
ffprobe input.wav

# 重新提取更高码率
ffmpeg -i input.mp4 -vn -acodec pcm_s24le -ar 48000 output.wav
```

### Q: 分离后人声有残留音乐？

**原因**：Demucs 限制

**解决方案**：
1. 使用更好的分离模型（如 MDX-Net）
2. 或手动使用专业工具（如 Adobe Audition）

## API 参考

### extract_audio

```python
def extract_audio(
    video_path: str,
    output_path: str = None
) -> str:
    """从视频提取音频"""
```

### normalize_audio

```python
def normalize_audio(
    audio_path: str,
    output_path: str = None,
    headroom: float = 0.1
) -> str:
    """音频音量归一化"""
```

### split_audio

```python
def split_audio(
    audio_path: str,
    max_duration: int = 1800
) -> list:
    """分段长音频"""
```

## 下一步

- 📖 阅读 [架构设计](architecture.md) 了解整体流程
- 📖 阅读 [ASR 后端扩展](advanced/asr-backend.md) 了解 ASR 定制
