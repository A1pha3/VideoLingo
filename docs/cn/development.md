# 开发指南

> VideoLingo 开发环境搭建、代码规范与调试技巧

## 学习目标

完成本教程后，你将能够：
- 搭建 VideoLingo 开发环境
- 理解项目的代码规范
- 使用调试工具定位问题
- 编写符合规范的代码

## 开发环境搭建

### 前置要求

| 工具 | 版本 | 用途 |
|------|------|------|
| Python | 3.10 | 运行环境 |
| Git | 最新 | 版本控制 |
| VS Code / PyCharm | 任意 | 代码编辑器 |
| FFmpeg | 4.0+ | 音视频处理 |

### 环境配置

```bash
# 1. 克隆仓库
git clone https://github.com/Huanshere/VideoLingo.git
cd VideoLingo

# 2. 创建开发环境
conda create -n videolingo-dev python=3.10 -y
conda activate videolingo-dev

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装 pre-commit（可选）
pip install pre-commit
pre-commit install
```

### VS Code 配置

推荐的 VS Code 扩展：

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugger",
    "tamasfe.even-better-toml",
    "github.copilot",
    "eamodio.gitlens"
  ]
}
```

`.vscode/settings.json` 配置：

```json
{
  "python.defaultInterpreterPath": "~/anaconda3/envs/videolingo-dev/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "_model_cache": true,
    "output": true
  }
}
```

## 项目结构

```
VideoLingo/
├── core/                      # 核心处理模块
│   ├── __init__.py            # 模块导出
│   ├── _1_ytdlp.py            # 步骤 1：视频下载
│   ├── _2_asr.py              # 步骤 2：语音识别
│   ├── _3_1_split_nlp.py      # 步骤 3.1：NLP 分割
│   ├── _3_2_split_meaning.py  # 步骤 3.2：语义分割
│   ├── _4_1_summarize.py      # 步骤 4.1：摘要
│   ├── _4_2_translate.py      # 步骤 4.2：翻译
│   ├── _5_split_sub.py        # 步骤 5：字幕分割
│   ├── _6_gen_sub.py          # 步骤 6：生成字幕
│   ├── _7_sub_into_vid.py     # 步骤 7：烧录字幕
│   ├── _8_1_audio_task.py     # 步骤 8.1：音频任务
│   ├── _8_2_dub_chunks.py     # 步骤 8.2：配音分块
│   ├── _9_refer_audio.py      # 步骤 9：参考音频
│   ├── _10_gen_audio.py       # 步骤 10：生成音频
│   ├── _11_merge_audio.py     # 步骤 11：合并音频
│   ├── _12_dub_to_vid.py      # 步骤 12：合成视频
│   ├── asr_backend/           # ASR 后端
│   ├── spacy_utils/           # spaCy 工具
│   ├── st_utils/              # Streamlit 工具
│   ├── tts_backend/           # TTS 后端
│   ├── utils/                 # 工具函数
│   ├── prompts.py             # LLM Prompt
│   └── translate_lines.py     # 翻译逻辑
├── batch/                     # 批处理模块
│   └── utils/
├── docs/                      # 文档
├── translations/              # 国际化
├── config.yaml                # 配置文件
├── install.py                 # 安装脚本
├── setup.py                   # 包设置
├── st.py                      # Streamlit 主入口
└── requirements.txt           # 依赖列表
```

## 代码规范

### 文件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 处理步骤 | `_X_描述.py`（X 为步骤号） | `_1_ytdlp.py`, `_2_asr.py` |
| 工具模块 | `描述.py` | `config_utils.py` |
| 后端 | `引擎名_tts.py` | `azure_tts.py` |
| 测试 | `test_描述.py` | `test_asr.py` |

### 注释规范

使用块注释分隔代码区域：

```python
# ------------
# 导入依赖
# ------------
import os
import sys

# ------------
# 常量定义
# ------------
MAX_LENGTH = 75

# ------------
# 工具函数
# ------------
def process_text(text):
    """处理文本的函数。"""
    pass

# ------------
# 主流程
# ------------
def main():
    pass
```

### 函数定义

```python
def split_subtitle(
    text: str,
    max_length: int = 75,
    language: str = "en"
) -> list[str]:
    """
    分割字幕为多行。

    参数：
        text: 原始文本
        max_length: 每行最大字符数
        language: 语言代码

    返回：
        分割后的文本列表
    """
    pass
```

> ⚠️ **注意**：虽然文档中使用类型注解便于理解，但项目代码中**不使用**类型注解（按 .cursorrules 规定）。

### 导入顺序

```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
import yaml
from openai import OpenAI

# 本地模块
from core.utils import load_key
from core.utils.config_utils import update_key
```

### 字符串格式化

```python
# 推荐：f-string
text = f"处理 {filename}，进度 {progress}%"

# 不推荐
text = "处理 {}，进度 {}%".format(filename, progress)
text = "处理 " + filename + "，进度 " + str(progress) + "%"
```

## 调试技巧

### 使用 Rich 输出

```python
from rich.console import Console
from rich.panel import Panel

console = Console()

# 打印带样式的消息
console.print("[green]成功！[/]")

# 打印面板
console.print(Panel("错误信息", style="red"))

# 打印进度
with console.status("[bold green]处理中..."):
    # 长时间操作
    pass
```

### 日志记录

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 使用日志
logger.info("开始处理")
logger.error(f"处理失败：{error}")
```

### LLM 调用调试

LLM 调用结果自动缓存在 `output/gpt_log/`：

```bash
# 查看最近的 LLM 调用
cat output/gpt_log/default.json

# 查看错误日志
cat output/gpt_log/error.json
```

### 断点调试

在 VS Code 中：

1. 在代码行号左侧点击设置断点
2. 按 `F5` 启动调试
3. 选择 `Python File` 或 `Streamlit` 调试配置

`.vscode/launch.json` 配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Streamlit",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "st.py"],
      "console": "integratedTerminal"
    }
  ]
}
```

### 单步执行处理流程

```python
# 在 Python REPL 中
from core import _2_asr

# 只执行转录
_2_asr.transcribe()

# 检查结果
import json
with open('output/log/asr_result.json') as f:
    data = json.load(f)
    print(data['segments'][:3])  # 查看前 3 个片段
```

## 常见开发任务

### 添加新的配置项

1. 在 `config.yaml` 添加配置

```yaml
my_feature:
  enabled: true
  option: "value"
```

2. 在代码中使用

```python
from core.utils.config_utils import load_key, update_key

# 读取
enabled = load_key('my_feature.enabled')

# 更新
update_key('my_feature.option', 'new_value')
```

### 添加新的处理步骤

1. 创建新文件 `core/_13_new_step.py`

2. 实现处理函数

```python
# ------------
# 新步骤描述
# ------------
from core.utils.models import INPUT_FILE

def process_new_step():
    """处理新步骤的逻辑。"""
    # 你的代码
    pass

if __name__ == "__main__":
    process_new_step()
```

3. 在 `core/__init__.py` 中导出

```python
from . import _13_new_step
```

4. 在处理流程中调用

```python
from core import _13_new_step
_13_new_step.process_new_step()
```

### 添加新的 Prompt

在 `core/prompts.py` 中添加：

```python
# ------------
# 新功能的 Prompt
# ------------
def get_my_feature_prompt(input_data, context=""):
    prompt = f"""
## Role
你是...

## Task
...

## INPUT
{input_data}

## Output in only JSON format and no other text
```json
{{
    "result": "..."
}}
```
"""
    return prompt.strip()
```

### 修改 Web 界面

在 `core/st_utils/` 中修改对应的组件：

```python
# core/st_utils/my_section.py
import streamlit as st

def my_section():
    st.header("我的新功能")
    value = st.text_input("输入值")
    if st.button("执行"):
        # 处理逻辑
        pass
```

在 `st.py` 中调用：

```python
from core.st_utils.my_section import my_section

def main():
    # ...
    my_section()
```

## 测试

### 手动测试

```bash
# 测试单个模块
python -m core._2_asr

# 测试批处理
python -m batch.utils.batch_processor
```

### 测试数据

将测试视频放在 `test/videos/` 目录：

```
test/
├── videos/
│   ├── short_1min.mp4       # 1 分钟测试视频
│   ├── medium_5min.mp4      # 5 分钟测试视频
│   └── long_20min.mp4       # 20 分钟测试视频
└── expected/
    ├── output_sub.mp4       # 预期输出
    └── srt_files/
        └── zh-CN.srt
```

## 性能优化

### GPU 利用率

```python
import torch

# 检查 GPU 可用性
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

# 监控 GPU 内存
print(f"Memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
```

### 并发处理

```python
from concurrent.futures import ThreadPoolExecutor

# 调整并发数
update_key('max_workers', 8)  # 根据你的硬件调整
```

### 缓存清理

```bash
# 清理模型缓存
rm -rf _model_cache/

# 清理输出缓存
rm -rf output/

# 清理 LLM 缓存
rm -rf output/gpt_log/
```

## 常见问题

### Q: 修改代码后没有生效？

Streamlit 有自动重载，但有时需要手动重启：

```bash
# Ctrl+C 停止，然后重新运行
streamlit run st.py
```

### Q: 导入错误 `Module not found`？

```bash
# 确保以可编辑模式安装
pip install -e .

# 或重新安装
pip install --no-cache-dir -e .
```

### Q: LLM 响应格式错误？

检查 `output/gpt_log/error.json` 了解详情，可能需要：
1. 更换更强的模型
2. 调整 Prompt
3. 启用 JSON 模式（`llm_support_json: true`）

## 贡献流程

1. **Fork 仓库**并创建分支

```bash
git checkout -b feature/my-feature
```

2. **编写代码**遵循规范

3. **测试**确保功能正常

4. **提交**使用清晰的提交信息

```bash
git commit -m "feat: 添加新的 TTS 后端支持"
```

5. **推送**到你的 Fork

```bash
git push origin feature/my-feature
```

6. **创建 PR**描述你的更改

## 自测问题

完成开发环境搭建后，尝试回答以下问题：

1. **为什么推荐使用 `pip install -e .` 安装？**
   
   <details>
   <summary>点击查看答案</summary>
   `-e` 参数表示「可编辑模式」，代码修改后立即生效，无需重新安装。这对于开发调试非常重要。
   </details>

2. **如何单独测试某个处理步骤？**
   
   <details>
   <summary>点击查看答案</summary>
   每个步骤文件都可以直接运行：`python -m core._2_asr`。也可以在 Python REPL 中导入并调用对应函数。
   </details>

3. **断点续传机制如何帮助调试？**
   
   <details>
   <summary>点击查看答案</summary>
   已完成的步骤会保存中间结果，下次运行时自动跳过。调试时可以手动删除特定步骤的输出文件，只重新运行该步骤。
   </details>

## 下一步

- 🔌 阅读 [TTS 后端扩展](advanced/tts-backend.md) 学习添加新引擎
- 🔌 阅读 [ASR 后端扩展](advanced/asr-backend.md) 学习添加 ASR 引擎
- 📖 阅读 [翻译原理](advanced/translation.md) 深入了解翻译系统
