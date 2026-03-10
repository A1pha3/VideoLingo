# 常见问题解答

> VideoLingo 使用中的常见问题

## 安装相关

### Q1: 安装时 PyTorch 版本冲突？

**A**: 使用 `install.py` 会自动检测 GPU 并选择合适版本。如果手动安装：

```bash
# RTX 50 系列 (Blackwell)
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu129

# 其他 GPU
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu126
```

### Q2: FFmpeg 安装后仍报错？

**A**: 检查 FFmpeg 是否在 PATH 中：

```bash
which ffmpeg
ffmpeg -version

# Windows: 检查环境变量
echo %PATH%
```

### Q3: 内存不足无法安装？

**A**: 使用轻量级安装：

```bash
# 只安装必需包
pip install streamlit openai requests pyyaml ruamel.yaml
```

## 配置相关

### Q4: API 密钥如何配置？

**A**: 三种方式：

1. **配置文件**（不推荐）：
```yaml
api:
  key: 'your-api-key'
```

2. **环境变量**（推荐）：
```bash
export OPENAI_API_KEY="your-api-key"
```

3. **Web UI**：在侧边栏输入

### Q5: 如何使用本地 LLM？

**A**:

```yaml
api:
  base_url: 'http://localhost:11434/v1'  # Ollama
  model: 'llama3'
  llm_support_json: false
max_workers: 1
```

### Q6: 翻译质量如何提高？

**A**:

```yaml
# 使用更强模型
api:
  model: 'claude-3-5-sonnet'

# 启用反思翻译
reflect_translate: true

# 增加上下文
summary_length: 12000

# 添加自定义术语
# 创建 custom_terms.xlsx
```

## 处理相关

### Q7: 转录识别率低？

**A**:

1. **启用 Demucs 人声分离**：
```yaml
demucs: true
```

2. **使用更大的模型**：
```yaml
whisper:
  model: 'large-v3'  # 而非 large-v3-turbo
```

3. **检查语言设置**：
```yaml
whisper:
  language: 'auto'  # 自动检测
```

### Q8: 字幕时间轴不对齐？

**A**:

1. 检查 ASR 结果：`cat output/log/asr_result.json`
2. 删除字幕缓存重试：`rm -rf output/srt_files/`
3. 使用云端 ASR（更准确）：
```yaml
whisper:
  runtime: 'cloud'
```

### Q9: 配音速度不匹配？

**A**:

```yaml
# 调整速度参数
speed_factor:
  min: 0.9      # 允许减速
  accept: 1.4   # 提高可接受速度
  max: 1.7      # 提高最大速度
```

### Q10: 视频烧录字幕失败？

**A**:

1. **检查 FFmpeg 编码器**：
```bash
ffmpeg -encoders | grep h264
```

2. **使用 CPU 编码**：
```yaml
ffmpeg_gpu: false
```

3. **检查字体**：
```bash
# Linux
sudo apt install fonts-noto
```

## 性能相关

### Q11: 处理速度慢？

**A**:

```yaml
# 快速配置
whisper:
  model: 'large-v3-turbo'
api:
  model: 'gpt-4.1-mini'
max_workers: 8
reflect_translate: false
```

### Q12: GPU 利用率低？

**A**:

1. 检查 GPU 使用：`nvidia-smi`
2. 增加批处理大小（修改代码）
3. 减少数据加载瓶颈

### Q13: 内存溢出？

**A**:

```bash
# 清理 GPU 内存
torch.cuda.empty_cache()

# 减小 WhisperX 批处理
# 修改 core/asr_backend/whisperX_local.py
batch_size = 4  # 默认 8
```

## 输出相关

### Q14: 如何只生成字幕不配音？

**A**: 只运行文本处理部分，跳过音频处理。

### Q15: 如何导出特定格式字幕？

**A**:

```python
# output/srt_files/ 包含：
# - en.srt (英文)
# - zh-CN.srt (中文)
# - bilingual.srt (双语)

# 只需复制需要的文件
cp output/srt_files/zh-CN.srt ./subs.srt
```

### Q16: 字幕样式如何修改？

**A**: 编辑 `core/_7_sub_into_vid.py` 中的 FFmpeg 字体参数。

## 批处理相关

### Q17: 如何批量处理？

**A**: 参考 [批处理指南](batch-processing.md)

### Q18: 批处理失败如何恢复？

**A**: 直接重新运行，失败任务会自动重试：

```bash
python -m batch.utils.batch_processor
```

## Docker 相关

### Q19: Docker GPU 不可用？

**A**:

```bash
# 检查 NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu20.04 nvidia-smi

# 重新安装
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Q20: Docker 镜像太大？

**A**:

```dockerfile
# 使用多阶段构建
FROM python:3.10-slim as builder
# ... 构建阶段

FROM python:3.10-slim
COPY --from=builder /app /app
```

## 其他

### Q21: 如何离线使用？

**A**:

1. 预下载模型到 `_model_cache/`
2. 使用本地 LLM（Ollama）
3. 使用 Edge TTS（免费）

### Q22: 支持哪些视频格式？

**A**:

```
输入: mp4, mov, avi, mkv, flv, wmv, webm
音频: wav, mp3, flac, m4a, ogg
```

### Q23: 如何处理 4K 视频？

**A**: 先降分辨率处理：

```bash
# 使用 ffmpeg 降分辨率
ffmpeg -i input_4k.mp4 -s 1920x1080 output_1080p.mp4
```

### Q24: 字幕显示乱码？

**A**:

```bash
# 安装字体
# Linux
sudo apt install fonts-noto

# 或在视频中嵌入字体
```

### Q25: 如何添加新的 TTS 引擎？

**A**: 参考 [TTS 后端扩展](advanced/tts-backend.md)

### Q26: 如何使用 302.ai 一站式服务？

**A**:

```yaml
# LLM
api:
  key: '302-api-key'
  base_url: 'https://yunwu.ai'

# Whisper
whisper:
  runtime: 'cloud'
  whisperX_302_api_key: '302-api-key'

# TTS
azure_tts:
  api_key: '302-api-key'
```

### Q27: YouTube 下载失败？

**A**:

1. 更新 yt-dlp：`pip install --upgrade yt-dlp`
2. 使用 cookies：`cookiesfrombrowser: chrome`
3. 检查网络连接

### Q28: 如何合并多个翻译结果？

**A**: `output/log/translation_result.xlsx` 包含所有翻译结果。

### Q29: 清理缓存释放空间？

**A**:

```bash
# 清理模型缓存
rm -rf _model_cache/

# 清理输出
rm -rf output/

# 清理 LLM 缓存
rm -rf output/gpt_log/
```

### Q30: 获取技术支持？

**A**:

- 📖 [故障排除](troubleshooting.md)
- 💬 [在线 AI 助手](https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh)
- 🌐 [在线体验](https://videolingo.io)
- 📧 team@videolingo.io
