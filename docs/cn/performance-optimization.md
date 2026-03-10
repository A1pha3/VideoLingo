# 性能优化指南

> VideoLingo 性能调优与加速技巧

## 学习目标

完成本教程后，你将能够：
- 识别性能瓶颈
- 优化 GPU/CPU 利用率
- 加速处理流程
- 平衡质量与速度

## 性能分析

### 处理时间分解

```
┌─────────────────────────────────────────────────────────────┐
│                    视频处理时间分布                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  转录 (ASR)        ████████████░░░░░░░░ 40-50%              │
│  翻译 (LLM)        ██████████░░░░░░░░░░ 30-40%              │
│  配音 (TTS)        ████░░░░░░░░░░░░░░░░ 10-15%              │
│  视频合成          ██░░░░░░░░░░░░░░░░░░ 5-10%               │
│  其他              █░░░░░░░░░░░░░░░░░░░ 2-5%                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 性能监控

```python
# 监控 GPU 使用
import nvidia_ml_py3 as nmlp
import torch

# GPU 状态
handle = nmlp.nvmlDeviceGetHandleByIndex(0)
info = nmlp.nvmlDeviceGetMemoryInfo(handle)
print(f"GPU 内存使用: {info.used / 1024**3:.2f} GB / {info.total / 1024**3:.2f} GB")

# PyTorch GPU 状态
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"当前 GPU: {torch.cuda.current_device()}")
print(f"GPU 数量: {torch.cuda.device_count()}")
```

```bash
# 实时监控
watch -n 1 nvidia-smi

# 处理时间分析
time python -m core._2_asr
```

## GPU 优化

### WhisperX 转录加速

**使用 Turbo 模型**：

```yaml
# config.yaml
whisper:
  model: 'large-v3-turbo'  # 比 large-v3 快 2-3 倍
```

| 模型 | 速度 | 精度 | 显存 |
|------|------|------|------|
| large-v3-turbo | 最快 | 高 | ~6GB |
| large-v3 | 快 | 最高 | ~10GB |

**调整批处理大小**：

编辑 `core/asr_backend/whisperX_local.py`：

```python
# 减小批处理节省显存
batch_size = 8  # 默认，可改为 4 或 2

# 或增大批处理提速（有足够显存时）
batch_size = 16
```

**FP16 推理**：

```python
# 在 whisperX_local.py 中
model = whisperx.load_model(
    whisper_model,
    device="cuda",
    compute_type="float16"  # 使用 FP16 而非 FP32
)
```

### LLM 调用优化

**提高并发数**：

```yaml
# config.yaml
max_workers: 8  # 默认 4，根据 API 限制调整
```

**使用更快的模型**：

```yaml
api:
  model: 'gpt-4.1-mini'      # 比 gpt-4.1 快 2 倍
  # model: 'deepseek-v3'     # 性价比高
  # model: 'claude-3-5-sonnet'  # 质量最高但较慢
```

**减少上下文长度**：

```yaml
summary_length: 4000  # 默认 8000
```

**跳过反思翻译**：

```yaml
reflect_translate: false  # 跳过第二步翻译，速度提升 50%
```

### TTS 生成加速

**并行处理**：

已在 `core/_10_gen_audio.py` 中实现 `ThreadPoolExecutor`：

```python
# 调整并发数（根据 GPU 数量）
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    # 生成音频
    pass
```

**使用更快的 TTS**：

| TTS 引擎 | 速度 | 质量 |
|----------|------|------|
| edge_tts | 最快 | 中 |
| openai_tts | 快 | 高 |
| azure_tts | 快 | 高 |
| gpt_sovits | 慢 | 最高 |

## CPU 优化

### 多线程处理

```python
import concurrent.futures

# spaCy NLP 处理
def process_sentence(sentence):
    # NLP 处理逻辑
    pass

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_sentence, sentences)
```

### 音频处理加速

```bash
# 使用 FFmpeg GPU 加速
ffmpeg -hwaccel cuda -i input.mp4 output.mp4

# 或使用 NVIDIA 硬件编码
ffmpeg -i input.mp4 -c:v h264_nvenc output.mp4
```

```yaml
# config.yaml
ffmpeg_gpu: true  # 启用 GPU 加速
```

## 缓存策略

### LLM 响应缓存

VideoLingo 自动缓存 LLM 响应：

```python
# 缓存位置
output/gpt_log/
├── default.json      # 默认缓存
├── translate.json    # 翻译缓存
└── error.json        # 错误日志
```

**重用缓存**：

```bash
# 不要删除 output/gpt_log/
# 相同的 prompt 会直接返回缓存结果
```

### 模型缓存

```bash
# 预下载模型
_model_cache/
├── whisper/
│   ├── large-v3.pt
│   └── large-v3-turbo.pt
└── spacy/
    ├── en_core_web_md
    └── zh_core_web_md
```

```yaml
# config.yaml
model_dir: './_model_cache'  # 集中管理模型
```

## 配置优化

### 快速处理配置

```yaml
# config.yaml - 速度优先配置

# Whisper 配置
whisper:
  model: 'large-v3-turbo'
  runtime: 'local'

# LLM 配置
api:
  model: 'gpt-4.1-mini'
max_workers: 8
reflect_translate: false
summary_length: 4000

# 字幕配置
subtitle:
  max_length: 50  # 减少处理
burn_subtitles: false  # 跳过烧录

# 配音配置（如果需要）
tts_method: 'edge_tts'  # 最快的 TTS
```

### 质量优先配置

```yaml
# config.yaml - 质量优先配置

whisper:
  model: 'large-v3'

api:
  model: 'claude-3-5-sonnet'
max_workers: 4
reflect_translate: true
summary_length: 12000

subtitle:
  max_length: 75

tts_method: 'azure_tts'
```

### 平衡配置（推荐）

```yaml
# config.yaml - 平衡配置

whisper:
  model: 'large-v3-turbo'

api:
  model: 'gpt-4.1-2025-04-14'
max_workers: 6
reflect_translate: true
summary_length: 6000

subtitle:
  max_length: 65

tts_method: 'openai_tts'
```

## 批处理优化

### 并行处理多个视频

```python
# 修改 batch_processor.py
from concurrent.futures import ProcessPoolExecutor

def process_video_wrapper(args):
    file, dubbing = args
    return process_video(file, dubbing)

# 使用进程池并行处理
with ProcessPoolExecutor(max_workers=2) as executor:
    futures = []
    for _, row in df.iterrows():
        args = (row['Video File'], row.get('Dubbing', 0))
        future = executor.submit(process_video_wrapper, args)
        futures.append(future)
```

### GPU 分配策略

多 GPU 时分配任务：

```bash
# GPU 0 处理视频 1-5
CUDA_VISIBLE_DEVICES=0 python -m batch.utils.batch_processor

# GPU 1 处理视频 6-10
CUDA_VISIBLE_DEVICES=1 python -m batch.utils.batch_processor
```

## 网络优化

### API 请求优化

```python
# 使用连接池
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry, pool_connections=10)
session.mount('https://', adapter)
```

### 减少延迟

```yaml
# 选择最近的 API 端点
api:
  base_url: 'https://api.openai.com'  # 美国西海岸延迟最低
  # base_url: 'https://yunwu.ai'     # 国内优化
```

## 存储优化

### SSD vs HDD

```
组件          HDD   SSD   提升
─────────────────────────────────
模型加载      慢    快    5-10x
音频写入      慢    快    3-5x
视频合成      慢    快    2-3x
```

**建议**：将 `output/` 和 `_model_cache/` 放在 SSD 上。

### 内存优化

```bash
# 增加系统交换空间
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

```python
# 及时清理 GPU 内存
import torch
torch.cuda.empty_cache()

import gc
gc.collect()
```

## 性能基准

### 典型处理时间

| 视频时长 | 配置 | 字幕处理 | 配音处理 | 总计 |
|----------|------|----------|----------|------|
| 5 分钟 | 快速 | 2-3 分钟 | 3-5 分钟 | 5-8 分钟 |
| 5 分钟 | 平衡 | 3-5 分钟 | 5-8 分钟 | 8-13 分钟 |
| 5 分钟 | 质量 | 5-8 分钟 | 8-12 分钟 | 13-20 分钟 |
| 30 分钟 | 平衡 | 15-20 分钟 | 30-40 分钟 | 45-60 分钟 |

### 吞吐量对比

| 配置 | GPU | 每小时视频处理时间 |
|------|-----|-------------------|
| 快速 | RTX 4090 | ~0.8x |
| 平衡 | RTX 4090 | ~1.5x |
| 质量 | RTX 4090 | ~2.0x |
| 快速 | RTX 3060 | ~1.5x |
| 平衡 | RTX 3060 | ~2.5x |

## 故障排除

### GPU 利用率低

```bash
# 检查 GPU 使用率
nvidia-smi dmon -s u

# 如果 GPU 利用率 < 50%：
# 1. 检查是否使用了 CPU 模式
# 2. 增加 batch_size
# 3. 减少数据加载瓶颈
```

### 内存不足

```bash
# 监控内存
free -h

# 清理缓存
echo 3 > /proc/sys/vm/drop_caches

# 增加 swap
sudo swapon --show
```

### 处理卡住

```bash
# 检查进程状态
ps aux | grep python

# 检查网络
curl -I https://api.openai.com

# 重启处理
# 删除 output/ 重新开始
```

## 最佳实践

1. **首次运行使用快速配置**：验证流程正常
2. **生产使用平衡配置**：兼顾质量和速度
3. **批量处理使用多 GPU**：分配不同任务
4. **定期清理缓存**：避免磁盘占满
5. **监控资源使用**：及时发现瓶颈

## 下一步

- 📖 阅读 [配置说明](configuration.md) 了解详细配置
- 📖 阅读 [批处理指南](batch-processing.md) 进行批量处理
