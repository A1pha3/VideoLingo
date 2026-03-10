# 批处理指南

> 批量处理多个视频的完整指南

## 学习目标

完成本教程后，你将能够：
- 配置批处理任务
- 管理 Excel 任务列表
- 处理批量视频翻译
- 处理失败任务

## 批处理概述

批处理模式允许你一次性处理多个视频，无需在 Web UI 中手动操作。

```
┌─────────────────────────────────────────────────────────────┐
│                    批处理工作流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. 配置任务（batch/tasks_setting.xlsx）                     │
│       ├── 视频文件/URL                                       │
│       ├── 源语言                                              │
│       ├── 目标语言                                            │
│       └── 是否配音                                            │
│                                                               │
│  2. 准备输入文件                                              │
│       └── batch/input/ 目录                                   │
│                                                               │
│  3. 运行批处理                                                │
│       └── python -m batch.utils.batch_processor             │
│                                                               │
│  4. 获取结果                                                  │
│       └── batch/output/ 目录                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 步骤 1：准备视频文件

将视频文件放入 `batch/input/` 目录：

```bash
# 创建输入目录
mkdir -p batch/input

# 复制视频文件
cp video1.mp4 batch/input/
cp video2.mp4 batch/input/
```

### 步骤 2：配置任务

编辑 `batch/tasks_setting.xlsx`：

| Video File | Source Language | Target Language | Dubbing | Status |
|------------|-----------------|-----------------|---------|--------|
| video1.mp4 | en | 简体中文 | 0 | |
| video2.mp4 | en | 日本語 | 1 | |
| https://youtube.com/... | en | 简体中文 | 0 | |

**字段说明**：

- **Video File**：视频文件名（在 batch/input/ 中）或 YouTube URL
- **Source Language**：源语言 ISO 代码（en/zh/ja/ru/fr/de/es/it），留空使用配置默认值
- **Target Language**：目标语言（自然语言描述），留空使用配置默认值
- **Dubbing**：是否生成配音（0=否，1=是）
- **Status**：自动填充，表示处理状态

### 步骤 3：运行批处理

```bash
# 激活环境
conda activate videolingo

# 运行批处理
python -m batch.utils.batch_processor
```

### 步骤 4：查看结果

处理完成后，结果保存在 `batch/output/`：

```
batch/output/
├── video1/                    # 每个视频一个文件夹
│   ├── output_sub.mp4
│   ├── srt_files/
│   └── ...
├── video2/
│   ├── output_sub.mp4
│   ├── output_dub.mp4
│   └── ...
└── ERROR/                     # 失败的任务
```

## 高级配置

### 任务优先级

Excel 中行号决定处理顺序。要调整优先级：

1. 复制要优先处理的行
2. 粘贴到表格顶部
3. 删除原位置的行

### 错误重试

失败的任务会在 Status 列标记：

```
Error: transcribe - CUDA out of memory
Error: translate - API rate limit exceeded
```

**自动重试**：下次运行批处理时，失败的任务会自动重试

**手动重试**：
1. 修复问题（如 GPU 内存、API 配额）
2. 直接重新运行批处理
3. 系统会自动识别 Status 不为空的失败任务

### 部分处理

如果只想处理部分任务：

1. 在 Excel 中删除不需要处理的行
2. 或将 Status 设置为任意值（已完成任务会被跳过）

## 批处理模块详解

### settings_check.py

验证任务配置的有效性：

```python
from batch.utils.settings_check import check_settings

if check_settings():
    print("配置有效")
else:
    print("配置有误")
```

**检查项**：
- 文件是否存在（对于本地文件）
- URL 格式是否有效
- 语言代码是否支持
- 配置值是否在有效范围内

### video_processor.py

处理单个视频的核心逻辑：

```python
from batch.utils.video_processor import process_video

# 处理视频（包含配音）
status, error_step, error_msg = process_video(
    file="video1.mp4",
    dubbing=True,
    is_retry=False
)

if status:
    print("处理成功")
else:
    print(f"处理失败：{error_step} - {error_msg}")
```

**处理流程**：

```
┌─────────────────────────────────────────────────────────────┐
│ process_video()                                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. prepare_output_folder()   # 准备输出目录                 │
│  2. process_input_file()       # 下载/复制视频               │
│  3. 文本处理步骤：                                          │
│     • _2_asr.transcribe()      # 转录                        │
│     • split_sentences()        # 分割                        │
│     • summarize_and_translate() # 翻译                       │
│     • process_and_align_subtitles() # 字幕                  │
│     • _7_sub_into_vid()        # 烧录字幕                    │
│  4. 音频处理步骤（如果 dubbing=True）：                       │
│     • gen_audio_tasks()        # 音频任务                    │
│     • _9_refer_audio()         # 参考音频                    │
│     • _10_gen_audio()          # 生成音频                    │
│     • _11_merge_audio()        # 合并音频                    │
│     • _12_dub_to_vid()         # 合成视频                    │
│  5. cleanup()                  # 归档结果                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### batch_processor.py

主批处理控制器：

```python
from batch.utils.batch_processor import process_batch

process_batch()
```

**功能**：
- 读取 Excel 任务列表
- 跳过已完成任务
- 识别并重试失败任务
- 动态切换语言配置
- 更新任务状态
- 错误处理与恢复

## 常见场景

### 场景 1：批量下载 YouTube 视频

```excel
| Video File | Source Language | Target Language | Dubbing |
|------------|-----------------|-----------------|---------|
| https://youtube.com/abc123 | en | 简体中文 | 0 |
| https://youtube.com/def456 | en | 简体中文 | 0 |
```

### 场景 2：多语言翻译

```excel
| Video File | Source Language | Target Language | Dubbing |
|------------|-----------------|-----------------|---------|
| video.mp4 | en | 简体中文 | 0 |
| video.mp4 | en | 日本語 | 0 |
| video.mp4 | en | Español | 0 |
```

**注意**：需要先将视频复制到 input 目录，或使用 URL

### 场景 3：字幕 + 配音

```excel
| Video File | Source Language | Target Language | Dubbing |
|------------|-----------------|-----------------|---------|
| video1.mp4 | en | 简体中文 | 1 |
| video2.mp4 | en | 简体中文 | 1 |
```

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `File not found` | 视频文件不在 input 目录 | 检查文件名和路径 |
| `CUDA out of memory` | GPU 内存不足 | 关闭其他程序或使用云 API |
| `API rate limit` | API 配额用尽 | 等待或切换 API 密钥 |
| `Invalid language` | 语言代码错误 | 使用有效的 ISO 639-1 代码 |

### 错误恢复

失败的任务会保存到 `batch/output/ERROR/视频名/`：

```bash
# 错误输出目录结构
batch/output/ERROR/video1/
├── output/          # 失败时的中间结果
├── log/             # 日志文件
└── config.yaml      # 使用的配置
```

下次运行时会自动恢复并重试。

## 性能优化

### 并发处理

批处理默认串行处理。要实现并发，修改 `batch_processor.py`：

```python
# 示例：2 个并发任务
from concurrent.futures import ThreadPoolExecutor

def process_single_task(row):
    # 处理单个任务的逻辑
    pass

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = []
    for index, row in df.iterrows():
        future = executor.submit(process_single_task, row)
        futures.append((future, index))
```

### GPU 内存管理

处理多个视频时 GPU 内存可能累积：

```bash
# 每处理完一个视频后清理
nvidia-smi --gpu-reset

# 或在代码中添加
import torch
torch.cuda.empty_cache()
```

## 监控与日志

### 实时进度

批处理会在终端显示进度：

```
┌──────────────────────────────────────────┐
│ Now processing task: video1.mp4         │
│ Task 1/5                                │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ [bold green]🎙️ Transcribing with Whisper[/] │
└──────────────────────────────────────────┘
```

### 日志文件

详细日志保存在：

```bash
# LLM 调用日志
output/gpt_log/

# 错误日志
batch/output/ERROR/*/log/
```

## 最佳实践

1. **先测试单个视频**：在批处理前先用 Web UI 处理一个视频
2. **使用相对较小的文件**：首次运行使用短视频测试配置
3. **监控 API 使用量**：大量视频会消耗大量 API 配额
4. **定期备份任务文件**：保存 tasks_setting.xlsx 的副本
5. **检查输出质量**：处理完成后检查几个输出确认质量

## 下一步

- 📖 阅读 [配置说明](configuration.md) 了解详细配置
- 🐛 阅读 [故障排除](troubleshooting.md) 解决常见问题
