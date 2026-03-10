# 故障排除

> 常见问题及解决方案

## 目录

- [安装问题](#安装问题)
- [配置问题](#配置问题)
- [转录问题](#转录问题)
- [翻译问题](#翻译问题)
- [字幕问题](#字幕问题)
- [配音问题](#配音问题)
- [性能问题](#性能问题)
- [错误码参考](#错误码参考)

---

## 安装问题

### FFmpeg 未找到

**症状**：

```
FileNotFoundError: ffmpeg not found
```

**解决方案**：

1. 确认 FFmpeg 已安装：

```bash
ffmpeg -version
```

2. 将 FFmpeg 添加到系统 PATH：

**Windows**：
```
# 将 FFmpeg 路径添加到系统环境变量
# 例如：C:\ffmpeg\bin
```

**macOS/Linux**：
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export PATH="/path/to/ffmpeg/bin:$PATH"
```

### PyTorch CUDA 版本不匹配

**症状**：

```
RuntimeError: CUDA version mismatch
```

**解决方案**：

```bash
# 查看当前 CUDA 版本
nvidia-smi

# 卸载现有 PyTorch
pip uninstall torch torchaudio

# 重新安装匹配的版本
# CUDA 12.6
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu126

# CUDA 12.8（RTX 50 系列）
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
```

### 依赖安装失败

**症状**：

```
ERROR: Could not build wheels for XXX
```

**解决方案**：

```bash
# 1. 更新 pip
pip install --upgrade pip

# 2. 使用国内镜像
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 或配置永久镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### demucs torchaudio 冲突

**症状**：

```
ERROR: torchaudio's dependency conflict
```

**解决方案**：按照手动安装步骤，使用 `--no-deps` 安装 demucs：

```bash
pip install --no-deps demucs[dev]@git+https://github.com/adefossez/demucs
pip install dora-search openunmix lameenc
```

---

## 配置问题

### API 密钥无效

**症状**：

```
ValueError: API key is not set
```

**解决方案**：

1. 检查 `config.yaml`：

```yaml
api:
  key: 'your-actual-api-key'  # 替换为真实密钥
```

2. 或在 Streamlit 设置面板中配置

3. 验证密钥：

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer your-api-key"
```

### 配置未生效

**症状**：修改配置后没有变化

**解决方案**：

```bash
# 1. 重启 Streamlit
# Ctrl+C 停止，然后重新运行
streamlit run st.py

# 2. 检查配置是否正确保存
cat config.yaml

# 3. 清理缓存（有时会读取旧配置）
rm -rf output/
```

---

## 转录问题

### CUDA 内存不足

**症状**：

```
CUDA out of memory
```

**解决方案**：

1. **减小批处理大小**（修改 `core/asr_backend/whisperX_local.py`）：

```python
# 找到 batch_size 参数，改小
batch_size = 8  # 默认值，改为 4 或更低
```

2. **使用 CPU 模式**：

```yaml
# config.yaml
whisper:
  runtime: 'cloud'  # 使用云端 API
```

3. **使用更小的模型**：

```yaml
whisper:
  model: 'large-v3-turbo'  # 比 large-v3 更省内存
```

### WhisperX 下载失败

**症状**：

```
ERROR: Model download failed
```

**解决方案**：

```bash
# 1. 设置国内镜像
export HF_ENDPOINT=https://hf-mirror.com

# 2. 使用代理
export https_proxy=http://127.0.0.1:7890

# 3. 手动下载模型到 _model_cache/whisper/
# 从 https://huggingface.co/ggerganov/whisper.cpp 下载
```

### 转录结果为空

**症状**：

```
WARNING: No speech detected
```

**可能原因**：

1. 音频没有语音 → 检查输入文件
2. 语言设置错误 → 检查 `whisper.language`
3. 背景音乐太响 → 启用 `demucs: true`

**解决方案**：

```yaml
# config.yaml
demucs: true  # 启用人声分离
whisper:
  language: 'auto'  # 自动检测语言
```

### 数字被截断

**症状**：字幕中的数字被省略

**原因**：WhisperX 的 wav2vec 模型无法将数字映射到发音

**解决方案**：这是已知限制，暂时无法完全解决

---

## 翻译问题

### LLM 响应格式错误

**症状**：

```
ValueError: ❎ API response error: ...
```

**解决方案**：

1. **检查错误日志**：

```bash
cat output/gpt_log/error.json | python -m json.tool
```

2. **使用更强的模型**：

```yaml
api:
  model: 'claude-3-5-sonnet'  # 或 'gpt-4.1'
```

3. **启用 JSON 模式**（如果模型支持）：

```yaml
api:
  llm_support_json: true
```

4. **删除缓存重试**：

```bash
rm -rf output/gpt_log/
rm -rf output/
```

### 翻译质量差

**可能原因**：

| 原因 | 解决方案 |
|------|----------|
| 模型能力不足 | 使用 Claude/GPT-4 而非 mini 模型 |
| 缺少上下文 | 增加 `summary_length` |
| 术语不一致 | 添加 `custom_terms.xlsx` |
| 未启用反思翻译 | 设置 `reflect_translate: true` |

### 翻译遗漏内容

**症状**：翻译后的行数少于原文

**原因**：LLM 输出格式问题

**解决方案**：

```bash
# 1. 删除输出重试
rm -rf output/

# 2. 使用支持 JSON 模式的模型
api:
  llm_support_json: true
  model: 'gpt-4.1'  # 不是所有模型都支持
```

### API 调用超时

**症状**：

```
Timeout error
```

**解决方案**：

```yaml
# 降低并发
max_workers: 2  # 默认 4

# 使用更快的模型
api:
  model: 'deepseek-v3'  # 或 'gpt-4.1-mini'
```

---

## 字幕问题

### 字幕时间轴不对齐

**症状**：字幕与视频不同步

**解决方案**：

1. **检查 ASR 结果**：

```bash
cat output/log/asr_result.json | python -m json.tool
```

2. **重新对齐**：

```bash
# 删除字幕相关输出
rm output/log/split_for_sub.json
rm output/srt_files/*

# 重新生成字幕
python -m core._6_gen_sub
```

### 字幕过长

**症状**：单行字幕超过屏幕宽度

**解决方案**：

```yaml
# 调整最大长度
subtitle:
  max_length: 50  # 默认 75

# 调整长度系数
subtitle:
  target_multiplier: 1.0  # 默认 1.2
```

### 字幕显示乱码

**症状**：字幕显示为方块或乱码

**原因**：缺少字体

**解决方案**：

```bash
# Linux
sudo apt install fonts-noto

# 或在视频中嵌入字体
# 修改 ffmpeg 命令指定字体
```

---

## 配音问题

### TTS 音频没有声音

**症状**：生成的 WAV 文件没有声音

**可能原因**：

1. API 密钥无效
2. 语音名称错误
3. TTS 服务故障

**解决方案**：

```bash
# 1. 测试 TTS API
curl -X POST https://api.openAI.com/v1/audio/speech \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"tts-1","voice":"alloy","input":"Hello"}' \
  --output test.mp3

# 2. 检查配置
cat config.yaml | grep -A 5 tts_method

# 3. 查看错误日志
cat output/log/tts_errors.log
```

### 配音速度不匹配

**症状**：配音与字幕不同步

**原因**：TTS 生成时长与目标时长差异过大

**解决方案**：

```yaml
# 调整速度参数
speed_factor:
  min: 0.9      # 允许减速
  accept: 1.3   # 提高可接受速度
  max: 1.6      # 提高最大速度
```

### GPT-SoVITS 无法启动

**症状**：

```
ERROR: GPT-SoVITS server not responding
```

**解决方案**：

1. **检查服务是否运行**：

```bash
# 检查端口（默认 9880）
curl http://localhost:9880

# 手动启动 GPT-SoVITS
cd /path/to/GPT-SoVITS
python api.py
```

2. **检查防火墙**：

```bash
# 允许端口
sudo ufw allow 9880
```

3. **检查配置**：

```yaml
gpt_sovits:
  refer_mode: 3  # 确认模式正确
```

---

## 性能问题

### 处理速度慢

**优化方案**：

```yaml
# 1. 提高 LLM 并发
max_workers: 8

# 2. 使用更快的模型
whisper:
  model: 'large-v3-turbo'  # 比 large-v3 快 2-3 倍

# 3. 跳过反思翻译
reflect_translate: false

# 4. 减少上下文
summary_length: 4000
```

### GPU 利用率低

**检查**：

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```

**解决方案**：

1. 确认安装了 GPU 版本的 PyTorch
2. 检查 CUDA 版本匹配
3. 关闭其他占用 GPU 的程序

### 磁盘空间不足

**症状**：

```
OSError: No space left on device
```

**解决方案**：

```bash
# 1. 清理模型缓存
rm -rf _model_cache/

# 2. 清理输出
rm -rf output/

# 3. 归档历史
mv history/ /path/to/external/drive/

# 4. 启用自动归档
# 处理完成后点击"归档到 history"按钮
```

---

## 错误码参考

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `API key is not set` | API 密钥未配置 | 配置 `api.key` |
| `CUDA out of memory` | GPU 内存不足 | 减小批处理或使用 CPU |
| `File not found` | 文件不存在 | 检查文件路径 |
| `Invalid response format` | LLM 响应错误 | 重试或更换模型 |
| `Model download failed` | 模型下载失败 | 检查网络或使用镜像 |
| `TTS request timeout` | TTS 超时 | 检查 API 或更换引擎 |
| `Audio file too large` | 音频文件过大 | 分段处理 |
| `Language not supported` | 语言不支持 | 检查 `spacy_model_map` |

---

## 获取帮助

如果以上方案都无法解决问题：

1. **查看日志**：

```bash
# LLM 调用日志
cat output/gpt_log/default.json

# 错误日志
cat output/gpt_log/error.json

# Streamlit 日志
# 查看终端输出
```

2. **在线 AI 助手**：

https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh

3. **提交 Issue**：

https://github.com/Huanshere/VideoLingo/issues

提交时请包含：
- 错误信息（完整截图）
- `config.yaml`（隐藏敏感信息）
- 系统信息（OS、GPU、Python 版本）
- 复现步骤

---

## 下一步

- 📖 阅读 [配置说明](configuration.md) 优化配置
- 🔧 阅读 [开发指南](development.md) 了解调试技巧
