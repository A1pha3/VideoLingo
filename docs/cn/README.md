# VideoLingo 中文文档

> 连接世界，逐帧传递 —— 全能视频翻译、本地化与配音工具

[![English](https://img.shields.io/badge/lang-English-blue.svg)](../README.md)
[![中文](https://img.shields.io/badge/lang-中文-red.svg)](README.md)

## 文档导航

### 新手入门

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [快速开始](quick-start.md) | 5 分钟上手，体验完整翻译流程 | 5 分钟 |
| [安装指南](installation.md) | 详细安装步骤，包含依赖说明 | 10 分钟 |
| [项目内 Conda 前缀环境](project-conda-prefix-env.md) | 把环境和缓存放到项目目录，减少系统盘占用 | 8 分钟 |
| [配置说明](configuration.md) | config.yaml 完整配置项说明 | 15 分钟 |

### 核心概念

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [架构设计](architecture.md) | 系统架构、处理流程、模块说明 | 30 分钟 |
| [翻译原理](advanced/translation.md) | 三步翻译流程深度解析 | 20 分钟 |

### 开发指南

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [开发指南](development.md) | 开发环境搭建、代码规范、调试技巧 | 25 分钟 |
| [API 参考](api-reference.md) | 核心模块 API 文档 | 40 分钟 |

### 高级主题

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [TTS 后端扩展](advanced/tts-backend.md) | 自定义 TTS 引擎开发 | 30 分钟 |
| [ASR 后端扩展](advanced/asr-backend.md) | 自定义 ASR 引擎开发 | 25 分钟 |

### 运维支持

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [批处理指南](batch-processing.md) | 批量处理多个视频 | 15 分钟 |
| [Docker 部署](docker-deployment.md) | 容器化部署指南 | 20 分钟 |
| [性能优化](performance-optimization.md) | 性能调优与加速 | 25 分钟 |
| [安全实践](security-best-practices.md) | 安全配置与数据保护 | 20 分钟 |
| [故障排除](troubleshooting.md) | 常见问题及解决方案 | 15 分钟 |
| [贡献指南](contributing.md) | 如何参与项目贡献 | 10 分钟 |

### 开发专题

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [UI 定制](ui-customization.md) | Streamlit 界面定制 | 20 分钟 |
| [国际化指南](i18n-guide.md) | 多语言支持开发 | 15 分钟 |
| [NLP 工具](nlp-tools.md) | spaCy 分割系统 | 20 分钟 |
| [音频处理](audio-processing.md) | 音频分离与预处理 | 20 分钟 |
| [Prompt 工程](prompt-engineering.md) | LLM Prompt 优化 | 25 分钟 |

### 参考资料

| 文档 | 描述 | 预计阅读时间 |
|------|------|--------------|
| [视频源管理](video-source-guide.md) | YouTube 下载与视频处理 | 15 分钟 |
| [字幕格式定制](subtitle-format.md) | SRT 格式与样式定制 | 15 分钟 |
| [配置模板](config-templates.md) | 常见场景配置模板 | 20 分钟 |
| [集成示例](integration-examples.md) | API 集成与工作流 | 25 分钟 |
| [常见问题](faq.md) | 30 个常见问题解答 | 20 分钟 |

## 学习路径

### 路径一：用户

适合只需要使用 VideoLingo 进行视频翻译的用户。

```
快速开始 → 安装指南 → 项目内 Conda 前缀环境（可选）→ 配置说明 → 故障排除
```

### 路径二：开发者

适合需要修改或扩展 VideoLingo 功能的开发者。

```
快速开始 → 架构设计 → 开发指南 → API 参考 → 高级主题
```

### 路径三：贡献者

适合希望向项目贡献代码的社区开发者。

```
用户路径 → 开发者路径 → 贡献指南
```

## 核心特性

- **Netflix 级字幕**：强制单行字幕，自动分段，符合行业标准
- **词级对齐**：WhisperX 提供毫秒级精确时间戳
- **智能翻译**：忠实翻译 → 反思优化 → 自由改编三步流程
- **高质量配音**：支持 GPT-SoVITS、Azure、OpenAI、Fish TTS 等多种引擎
- **一键处理**：Streamlit 交互界面，全程可视化
- **批处理支持**：Excel 配置，批量处理多个视频

## 技术栈

```
前端界面：  Streamlit
ASR 引擎：  WhisperX (本地/302.ai/ElevenLabs)
NLP 处理：  spaCy
LLM 接口：  OpenAI 兼容 API
TTS 引擎：  Azure/OpenAI/GPT-SoVITS/Fish/Edge-TTS
视频处理：  FFmpeg
音频分离：  Demucs
```

## 快速命令

```bash
# 默认安装
python install.py

# 如果你使用项目内 Conda 前缀环境
source scripts/activate_project_conda_env.zsh
python install.py

# 启动 Web UI
streamlit run st.py

# 批处理模式
python -m batch.utils.batch_processor
```

## 获取帮助

- 📖 [问题排查](troubleshooting.md)
- 💬 [在线 AI 助手](https://share.fastgpt.in/chat/share?shareId=066w11n3r9aq6879r4z0v9rh)
- 🌐 [在线体验](https://videolingo.io)
- 📧 邮件：team@videolingo.io

## 许可证

Apache License 2.0
