# 字幕格式定制指南

> SRT 字幕格式与样式定制

## 学习目标

完成本教程后，你将能够：
- 理解 SRT 格式规范
- 定制字幕样式
- 创建多语言字幕
- 处理特殊字幕需求

## SRT 格式规范

### 基本格式

```srt
1
00:00:00,000 --> 00:00:02,500
Hello, world!

2
00:00:02,500 --> 00:00:05,000
How are you?
```

**格式说明**：
- 序号：从 1 开始
- 时间戳：`HH:MM:SS,mmm --> HH:MM:SS,mmm`
- 文本：字幕内容
- 空行：字幕之间必须有空行

### 时间戳规范

| 组件 | 格式 | 示例 |
|------|------|------|
| 小时 | 00-23 | 00, 01, ..., 23 |
| 分钟 | 00-59 | 00, 01, ..., 59 |
| 秒 | 00-59 | 00, 01, ..., 59 |
| 毫秒 | 000-999 | 000, 001, ..., 999 |

## 字幕样式

### Netflix 标准

VideoLingo 遵循 Netflix 字幕标准：

- **单行**：只显示一行字幕
- **长度限制**：每行最多 75 字符
- **时长限制**：每帧最少显示 1/6 秒
- **可读性**：使用简单清晰的字体

### 字幕位置

```
┌─────────────────────────────────────┐
│              视频画面                │
│                                      │
│         ┌───────────────┐            │
│         │ 字幕区域       │  底部 10%  │
│         │ (90% 宽度)     │            │
│         └───────────────┘            │
│                                      │
└─────────────────────────────────────┘
```

### 字幕对齐

- **左对齐**：中文、日文等
- **居中对齐**：英文、欧洲语言

## 定制字幕样式

### 字体颜色

编辑 `core/_7_sub_into_vid.py`：

```python
# FFmpeg 字幕样式
subtitle_style = {
    'FontSize': 24,
    'FontName': 'Arial',
    'PrimaryColour': '&HFFFFFF',  # 白色
    'BackColour': '&H000000',      # 黑色背景
    'Alignment': '2'               # 居中
}
```

### 字体大小

```yaml
# 字幕大小（像素）
subtitle:
  max_length: 75  # 字符数
```

在 `core/_6_gen_sub.py` 中调整字体大小。

### 背景样式

```python
# 添加背景
style = """ForceStyle='FontSize=24,PrimaryColour=&HFFFFFF,BackColour=&H80000000,BorderStyle=3'"""
```

## 双语字幕

### 并排显示

```srt
1
00:00:00,000 --> 00:00:02,500
Hello, world!

2
00:00:00,000 --> 00:00:02,500
你好，世界！
```

### 上下显示

VideoLingo 默认上下布局：

```
┌─────────────────────────────────────┐
│         Hello, world!              │  ← 上方字幕
│         你好，世界！                │  ← 下方字幕
└─────────────────────────────────────┘
```

## 特殊字符处理

### 文本清理

```python
import re

def clean_subtitle_text(text):
    """清理字幕文本"""
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空格
    text = text.strip()
    return text
```

### HTML 实体

```srt
<!-- 显示特殊字符 -->
&lt;     → <
&gt;     → >
&amp;    → &
&quot;   → "
&apos;   → '
```

### 换行符

```srt
<!-- 强制换行 -->
First line.{\a1}Second line.
```

## 字幕验证

### 格式验证

```python
def validate_srt(file_path):
    """验证 SRT 文件格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    errors = []
    i = 0
    while i < len(lines):
        # 检查序号
        if not lines[i].strip().isdigit():
            errors.append(f"行 {i+1}: 序号格式错误")

        # 检查时间戳
        timestamp = lines[i+1]
        if '-->' not in timestamp:
            errors.append(f"行 {i+2}: 时间戳格式错误")

        # 检查空行
        if i+2 < len(lines) and lines[i+2].strip() != '':
            errors.append(f"行 {i+3}: 缺少空行")

        i += 4

    return errors
```

### 长度检查

```python
def check_subtitle_length(file_path, max_length=75):
    """检查字幕长度"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    subtitles = content.split('\n\n')
    long_subs = []

    for i, sub in enumerate(subtitles):
        lines = [l for l in sub.split('\n') if '-->' not in l and l.strip()]
        for line in lines:
            if len(line) > max_length:
                long_subs.append((i+1, line, len(line)))

    return long_subs
```

## 高级定制

### 动态样式

根据内容调整样式：

```python
# 重要对话使用不同颜色
if is_important_dialogue(text):
    style = "PrimaryColour=&H00FFFF"  # 青色
else:
    style = "PrimaryColour=&HFFFFFF"  # 白色
```

### 说话人标识

```srt
1
00:00:00,000 --> 00:00:02,500
{\an8}John: Hello!
{\an8}Jane: Hi there!
```

### 歌词字幕

```srt
1
00:00:00,000 --> 00:00:05,000
♪ La la la, la la la ♪
```

## 最佳实践

1. **可读性优先**：字体大小适中，对比度高
2. **避免遮挡**：字幕位于底部，不遮挡关键内容
3. **同步准确**：时间戳精确到毫秒
4. **长度适中**：每行不超过 75 字符
5. **语言规范**：使用正确的标点和大小写

## 自测问题

完成字幕格式学习后，尝试回答以下问题：

1. **SRT 和 ASS 格式的主要区别是什么？**
   
   <details>
   <summary>点击查看答案</summary>
   SRT 是最简单的字幕格式，只包含时间轴和文本。ASS 支持丰富的样式（字体、颜色、位置、动画等），适合需要精细控制的场景。VideoLingo 默认生成 SRT，但可以通过 FFmpeg 参数使用 ASS 样式。
   </details>

2. **如何确保字幕与视频同步？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 使用 WhisperX 的词级对齐功能获取精确时间戳
   2. 检查 `output/log/asr_result.json` 确认转录准确
   3. 如果字幕提前或延后，可能是视频帧率问题
   4. 使用 FFmpeg 的 `setpts` 滤镜调整时间轴
   </details>

3. **字幕长度超过屏幕宽度怎么办？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 在配置中减小 `subtitle.max_length`（默认 75 字符）
   2. 启用自动换行（SRT 格式支持多行）
   3. 使用 LLM 裁剪功能缩短文本
   4. 调整字体大小以适应屏幕
   </details>

## 下一步

- 📖 阅读 [架构设计](architecture.md) 了解字幕生成流程
- 📖 阅读 [配置说明](configuration.md) 调整字幕参数
