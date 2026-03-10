# 配置模板集合

> 常见使用场景的配置模板

## 学习目标

完成本教程后，你将能够：
- 根据场景选择合适配置
- 快速部署不同环境
- 优化配置参数

## 本地开发配置

适合开发和测试，使用本地 GPU 和免费 TTS。

```yaml
# config.yaml - 本地开发配置

# 基础设置
display_language: "zh-CN"

# API 配置（本地 LLM）
api:
  key: 'not-needed'  # 本地 Ollama 不需要
  base_url: 'http://localhost:11434/v1'
  model: 'llama3'
  llm_support_json: false

max_workers: 1  # 本地模型通常不支持高并发

# 语言设置
target_language: '简体中文'

# Whisper 配置（本地）
whisper:
  model: 'large-v3-turbo'
  language: 'en'
  runtime: 'local'

# 字幕配置
burn_subtitles: true

# 配音配置（免费）
tts_method: 'edge_tts'

edge_tts:
  voice: 'zh-CN-XiaoxiaoNeural'
```

## 云端高质量配置

适合生产环境，使用云端 API 获得最佳质量。

```yaml
# config.yaml - 云端高质量配置

display_language: "zh-CN"

# API 配置
api:
  key: 'your-302-api-key'
  base_url: 'https://yunwu.ai'
  model: 'claude-3-5-sonnet-20241022'
  llm_support_json: false

max_workers: 6

target_language: '简体中文'

# Whisper 配置（云端）
demucs: true  # 启用人声分离
whisper:
  model: 'large-v3'
  language: 'en'
  runtime: 'cloud'
  whisperX_302_api_key: 'your-302-api-key'

# 字幕配置
burn_subtitles: true

# 配音配置（高质量）
tts_method: 'azure_tts'

azure_tts:
  api_key: 'your-302-api-key'
  voice: 'zh-CN-YunfengNeural'
```

## 快速批处理配置

优化速度，适合批量处理大量视频。

```yaml
# config.yaml - 快速批处理配置

display_language: "zh-CN"

# 使用快速模型
api:
  key: 'your-api-key'
  base_url: 'https://yunwu.ai'
  model: 'gpt-4.1-mini'
  llm_support_json: false

max_workers: 8  # 提高并发

# 减少上下文
summary_length: 4000
reflect_translate: false  # 跳过反思翻译

# 使用快速 Whisper 模型
demucs: false  # 跳过耗时的人声分离
whisper:
  model: 'large-v3-turbo'
  runtime: 'cloud'

# 字幕配置
burn_subtitles: false  # 跳过烧录节省时间

# 快速 TTS
tts_method: 'openai_tts'

openai_tts:
  api_key: 'your-302-api-key'
  voice: 'alloy'
```

## 一站式 302.ai 配置

使用 302.ai 提供的所有服务。

```yaml
# config.yaml - 302.ai 一站式配置

display_language: "zh-CN"

# 302.ai 同时支持 LLM、WhisperX、TTS
api:
  key: 'your-302-api-key'
  base_url: 'https://yunwu.ai'
  model: 'gpt-4.1-2025-04-14'

# WhisperX 使用 302.ai
whisper:
  model: 'large-v3-turbo'
  runtime: 'cloud'
  whisperX_302_api_key: 'your-302-api-key'

# TTS 使用 302.ai
tts_method: 'azure_tts'
azure_tts:
  api_key: 'your-302-api-key'

# 或使用 Fish TTS
# tts_method: 'fish_tts'
# fish_tts:
#   api_key: 'your-302-api-key'
```

## 英语视频汉化配置

专门用于英语视频翻译成中文。

```yaml
# config.yaml - 英语汉化配置

display_language: "zh-CN"

api:
  key: 'your-api-key'
  base_url: 'https://yunwu.ai'
  model: 'claude-3-5-sonnet-20241022'  # 翻译质量最高

max_workers: 4

target_language: '简体中文'

# 英语专用配置
demucs: true  # 英语视频通常有背景音乐
whisper:
  model: 'large-v3'
  language: 'en'
  runtime: 'local'

# 汉化术语表（可选）
# 创建 custom_terms.xlsx

# 中文字幕优化
subtitle:
  max_length: 65  # 中文字符更紧凑

# 中文 TTS
tts_method: 'azure_tts'
azure_tts:
  voice: 'zh-CN-YunfengNeural'
```

## 日本视频汉化配置

针对日本视频的优化配置。

```yaml
# config.yaml - 日语汉化配置

display_language: "zh-CN"

api:
  key: 'your-api-key'
  base_url: 'https://yunwu.ai'
  model: 'claude-3-5-sonnet-20241022'

max_workers: 4

target_language: '简体中文'

# 日语视频处理
demucs: true  # 动漫通常有背景音乐
whisper:
  model: 'large-v3'  # 日语识别需要更好的模型
  language: 'ja'
  runtime: 'local'

# 日语术语
# 创建 custom_terms.xlsx 添加动漫术语

# 配音
tts_method: 'azure_tts'
azure_tts:
  voice: 'zh-CN-XiaoxiaoNeural'
```

## 极限性能配置

追求最快速度，牺牲一些质量。

```yaml
# config.yaml - 极限性能配置

display_language: "zh-CN"

# 最快 LLM
api:
  key: 'your-api-key'
  base_url: 'https://yunwu.ai'
  model: 'gpt-4.1-mini'
  llm_support_json: true  # 加速 JSON 解析

max_workers: 12  # 最大并发

# 最小上下文
summary_length: 2000
reflect_translate: false

# 跳过所有耗时操作
demucs: false
whisper:
  model: 'large-v3-turbo'
  runtime: 'cloud'

# 跳过烧录
burn_subtitles: false

# 最快 TTS（如果需要配音）
tts_method: 'edge_tts'
```

## 最佳质量配置

追求最高翻译和配音质量。

```yaml
# config.yaml - 最佳质量配置

display_language: "zh-CN"

# 最佳 LLM
api:
  key: 'your-api-key'
  base_url: 'https://yunwu.ai'
  model: 'claude-3-5-sonnet-20241022'

max_workers: 4  # 稳定的并发

# 完整上下文
summary_length: 12000
reflect_translate: true  # 启用反思翻译
pause_before_translate: true  # 允许手动编辑术语

# 最佳 Whisper
demucs: true
whisper:
  model: 'large-v3'  # 最准确
  runtime: 'cloud'

# 最佳字幕
subtitle:
  max_length: 75

# 最佳 TTS
tts_method: 'azure_tts'  # 或 gpt_sovits（克隆声音）
```

## 离线配置

完全离线，不依赖任何外部服务。

```yaml
# config.yaml - 离线配置

display_language: "zh-CN"

# 本地 LLM (Ollama)
api:
  key: 'not-needed'
  base_url: 'http://localhost:11434/v1'
  model: 'llama3'
  llm_support_json: false

max_workers: 1

target_language: '简体中文'

# 本地 Whisper
whisper:
  model: 'large-v3-turbo'
  runtime: 'local'

# 免费 TTS
tts_method: 'edge_tts'
edge_tts:
  voice: 'zh-CN-XiaoxiaoNeural'

# 其他
burn_subtitles: true
```

## 配置切换

### 使用脚本切换

```bash
#!/bin/bash
# switch-config.sh

CONFIG_NAME=$1
cp "configs/${CONFIG_NAME}.yaml" config.yaml
echo "已切换到 ${CONFIG_NAME} 配置"

# 使用
# ./switch-config.sh production
```

### 配置文件管理

```
configs/
├── development.yaml   # 开发环境
├── production.yaml    # 生产环境
├── batch.yaml         # 批处理
├── offline.yaml       # 离线模式
└── templates/
    ├── cn-en.yaml     # 中英互译
    ├── ja-zh.yaml     # 日中翻译
    └── ...
```

## 自测问题

选择配置模板时，尝试回答以下问题：

1. **如何根据视频类型选择合适的配置？**
   
   <details>
   <summary>点击查看答案</summary>
   - 技术教程：使用质量优先配置，确保术语准确
   - 动漫/日剧：启用 Demucs 分离背景音乐，使用 large-v3 模型
   - 快速预览：使用极限性能配置，快速生成字幕
   - 正式发布：使用最佳质量配置，确保翻译和配音质量
   </details>

2. **离线配置有什么限制？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 需要本地运行 Ollama 等 LLM 服务
   2. 本地 Whisper 模型需要 GPU 支持
   3. Edge TTS 仍需要网络连接（虽然免费）
   4. 翻译质量可能不如云端模型
   </details>

3. **如何快速切换不同配置？**
   
   <details>
   <summary>点击查看答案</summary>
   创建多个配置文件（如 `configs/production.yaml`），使用脚本或软链接切换。也可以通过环境变量覆盖配置值。
   </details>

## 下一步

- 📖 阅读 [配置说明](configuration.md) 了解详细配置
- 📖 阅读 [性能优化](performance-optimization.md) 优化性能
