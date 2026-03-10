# 安装指南

> 详细安装说明，包含各种系统配置和依赖管理

## 学习目标

完成本教程后，你将能够：
- 在各种操作系统上安装 VideoLingo
- 理解各个依赖的作用
- 解决常见的安装问题

## 系统要求

### 最低配置

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows 10+ / macOS 10.15+ / Linux (Ubuntu 20.04+) |
| Python | 3.10（强烈建议使用 Conda 管理） |
| 内存 | 8 GB RAM（推荐 16 GB） |
| 硬盘 | 10 GB 可用空间（用于模型缓存） |
| FFmpeg | 4.0+ |

### GPU 加速（推荐）

| 组件 | 要求 |
|------|------|
| GPU | NVIDIA GPU（计算能力 7.0+） |
| CUDA | 12.4+ |
| 驱动 | 550+ |

> 💡 **为什么需要 GPU**：WhisperX 转录在有 GPU 的情况下速度可提升 10-20 倍。TTS 音频生成也会受益于 GPU 加速。

## 安装方法

### 方法一：自动安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/Huanshere/VideoLingo.git
cd VideoLingo

# 运行安装脚本
python install.py
```

安装脚本会引导你完成：

1. **语言选择**：选择界面显示语言
2. **PyPI 镜像配置**（可选）：国内用户建议配置
3. **环境检测**：自动检测 GPU 并选择合适的 PyTorch
4. **依赖安装**：安装所有 Python 包
5. **FFmpeg 验证**：检查并提示 FFmpeg 安装

### 方法二：手动安装

如果自动安装失败，可以手动分步安装：

#### 步骤 1：创建 Conda 环境

```bash
conda create -n videolingo python=3.10 -y
conda activate videolingo
```

#### 步骤 2：安装 PyTorch

**有 NVIDIA GPU：**

```bash
# CUDA 12.6（推荐）
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu126

# CUDA 12.8（RTX 50 系列 / Blackwell）
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128

# CUDA 12.9（最新）
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu129
```

**无 GPU / macOS：**

```bash
pip install torch==2.8.0 torchaudio==2.8.0
```

> ⚠️ **重要**：RTX 50 系列（Blackwell 架构）需要 PyTorch 编译时包含 CUDA 12.8+ 和 sm_100 内核，请使用 cu129 索引。

#### 步骤 3：安装 Demucs

```bash
# 单独安装以避免 torchaudio 版本冲突
pip install --no-deps demucs[dev]@git+https://github.com/adefossez/demucs
pip install dora-search openunmix lameenc
```

#### 步骤 4：安装项目依赖

```bash
pip install -e .
```

### 方法三：Docker 安装

适合服务器环境和需要隔离部署的场景。

```bash
# 构建镜像
docker build -t videolingo .

# 运行容器（暴露 8501 端口）
docker run -d -p 8501:8501 --gpus all videolingo
```

> 📖 详细 Docker 文档请参考 [Docker 指南](../pages/docs/docker.zh-CN.md)

## FFmpeg 安装

FFmpeg 是必需依赖，用于视频和音频处理。

### Windows

```bash
# 使用 Chocolatey
choco install ffmpeg

# 或下载 Windows 构建版本
# https://www.gyan.dev/ffmpeg/builds/
```

> ⚠️ **Windows GPU 用户**：CUDA Toolkit 12.6 和 CUDNN 9.3.0 需要在安装 VideoLingo 前手动安装。

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg

# 可选：安装 Noto 字体（字幕显示）
sudo apt install fonts-noto
```

### 验证安装

```bash
ffmpeg -version

# 检查 MP3 编码器支持
ffmpeg -encoders | grep libmp3lame
```

如果缺少 `libmp3lame`，VideoLingo 会自动回退到 WAV 编码。

## 依赖说明

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| torch | 2.8.0 | 深度学习框架 |
| torchaudio | 2.8.0 | 音频处理 |
| whisperx | ≥3.8.1 | 语音识别与对齐 |
| demucs | latest | 音频分离 |
| spacy | 3.8.11 | NLP 句子分割 |
| streamlit | 1.49.1 | Web 界面 |
| transformers | ≥4.48.0 | LLM 接口 |
| openai | ≥1.55.3,<2 | API 客户端 |

### 可选依赖

| 包名 | 用途 |
|------|------|
| edge-tts | 免费 TTS 引擎 |
| nvidia-ml-py | GPU 状态监控 |

## spaCy 模型

VideoLingo 会根据源语言自动下载对应的 spaCy 模型：

| 语言 | 模型名称 | 大小 |
|------|----------|------|
| 英语 | en_core_web_md | 43 MB |
| 中文 | zh_core_web_md | 47 MB |
| 日语 | ja_core_news_md | 26 MB |
| 俄语 | ru_core_news_md | 37 MB |
| 法语 | fr_core_news_md | 37 MB |
| 德语 | de_core_news_md | 38 MB |
| 西班牙语 | es_core_news_md | 37 MB |
| 意大利语 | it_core_news_md | 38 MB |

模型会在首次使用时自动下载到 `_model_cache/` 目录。

## WhisperX 模型

首次运行时，WhisperX 会自动下载模型：

| 模型 | 大小 | 速度 | 精度 |
|------|------|------|------|
| large-v3-turbo | ~3 GB | 最快 | 高 |
| large-v3 | ~3 GB | 快 | 最高 |

模型会缓存到 `_model_cache/whisper/` 目录。

## 常见安装问题

### 问题 1：PyTorch CUDA 版本不匹配

**症状**：`RuntimeError: CUDA version mismatch`

**解决方案**：

```bash
# 卸载现有版本
pip uninstall torch torchaudio

# 重新安装匹配的版本
pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu126
```

### 问题 2：demucs torchaudio 冲突

**症状**：安装时出现 torchaudio 版本冲突

**解决方案**：按照手动安装步骤，使用 `--no-deps` 安装 demucs。

### 问题 3：FFmpeg 未找到

**症状**：`FileNotFoundError: ffmpeg not found`

**解决方案**：

1. 确认 FFmpeg 已安装
2. 将 FFmpeg 添加到系统 PATH
3. 重启终端/重新加载环境变量

### 问题 4：CUDA 内存不足

**症状**：`CUDA out of memory`

**解决方案**：

1. 减小 WhisperX 批处理大小（修改 config.yaml）
2. 使用 CPU 模式进行转录
3. 关闭其他占用 GPU 的程序

### 问题 5：网络下载失败

**症状**：模型下载超时或失败

**解决方案**：

```bash
# 设置国内镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或使用代理
export https_proxy=http://127.0.0.1:7890
```

## 验证安装

运行以下命令验证安装是否成功：

```bash
# 激活环境
conda activate videolingo

# 启动 Web 界面
streamlit run st.py
```

如果浏览器自动打开并显示 VideoLingo 界面，说明安装成功！

## 卸载

```bash
# 停止所有 VideoLingo 进程
pkill -f streamlit

# 卸载 Python 包
pip uninstall videolingo

# （可选）删除模型缓存
rm -rf _model_cache/

# （可选）删除 Conda 环境
conda deactivate
conda env remove -n videolingo
```

## 验证安装

运行以下命令验证安装是否成功：

```bash
# 激活环境
conda activate videolingo

# 启动 Web 界面
streamlit run st.py
```

如果浏览器自动打开并显示 VideoLingo 界面，说明安装成功！

## 自测问题

完成安装后，尝试回答以下问题：

1. **为什么推荐使用 Conda 管理 Python 环境？**
   
   <details>
   <summary>点击查看答案</summary>
   Conda 可以隔离项目依赖，避免不同项目之间的版本冲突。VideoLingo 需要特定版本的 PyTorch 和 CUDA，Conda 可以确保这些依赖正确安装。
   </details>

2. **RTX 50 系列显卡需要使用哪个 CUDA 版本的 PyTorch？**
   
   <details>
   <summary>点击查看答案</summary>
   RTX 50 系列（Blackwell 架构）需要 PyTorch 编译时包含 CUDA 12.8+ 和 sm_100 内核，应使用 cu129 索引安装。
   </details>

3. **FFmpeg 的作用是什么？为什么必须安装？**
   
   <details>
   <summary>点击查看答案</summary>
   FFmpeg 用于视频和音频处理，包括格式转换、音频提取、字幕烧录等。VideoLingo 的核心功能依赖 FFmpeg，没有它无法正常工作。
   </details>

## 卸载

```bash
# 停止所有 VideoLingo 进程
pkill -f streamlit

# 卸载 Python 包
pip uninstall videolingo

# （可选）删除模型缓存
rm -rf _model_cache/

# （可选）删除 Conda 环境
conda deactivate
conda env remove -n videolingo
```

## 下一步

- ⚙️ 阅读 [配置说明](configuration.md) 了解如何配置 API 密钥和其他设置
- 🚀 阅读 [快速开始](quick-start.md) 开始使用 VideoLingo
