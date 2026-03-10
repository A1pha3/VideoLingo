# NLP 工具深入解析

> spaCy 句子分割系统详解

## 学习目标

完成本教程后，你将能够：
- 理解 spaCy 分割系统架构
- 配置不同语言的分割规则
- 自定义分割行为
- 解决分割相关问题

## 系统架构

```
core/_3_1_split_nlp.py (主流程)
    ├── load_nlp_model.py      # 模型加载
    ├── split_by_mark.py       # 标点符号分割
    ├── split_by_comma.py      # 逗号分割
    ├── split_by_connector.py  # 连接词分割
    └── split_long_by_root.py  # 长句分割
```

## 分割流程

```
┌─────────────────────────────────────────────────────────────┐
│                      NLP 分割流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. 加载 spaCy 模型 (load_nlp_model.py)                      │
│     └── 根据语言自动选择模型                                  │
│                                                               │
│  2. 标点分割 (split_by_mark.py)                              │
│     └── 按 。!? 等标点分割                                    │
│                                                               │
│  3. 逗号分割 (split_by_comma.py)                             │
│     └── 按逗号分割，验证语法有效性                            │
│                                                               │
│  4. 连接词分割 (split_by_connector.py)                       │
│     └── 按连接词分割                                          │
│                                                               │
│  5. 长句分割 (split_long_by_root.py)                         │
│     └── 分割过长的句子                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 语言模型

### 支持的语言

| 语言 | 模型 | 大小 |
|------|------|------|
| 英语 | en_core_web_md | 43 MB |
| 中文 | zh_core_web_md | 47 MB |
| 日语 | ja_core_news_md | 26 MB |
| 俄语 | ru_core_news_md | 37 MB |
| 法语 | fr_core_news_md | 37 MB |
| 德语 | de_core_news_md | 38 MB |
| 西班牙语 | es_core_news_md | 37 MB |
| 意大利语 | it_core_news_md | 38 MB |

### 模型加载

```python
from core.spacy_utils.load_nlp_model import load_nlp_model

# 自动加载
nlp = load_nlp_model(language="en")

# 手动指定
nlp = spacy.load("en_core_web_md")
```

### 模型缓存

模型首次使用时自动下载到：

```
_model_cache/spacy/
├── en_core_web_md/
├── zh_core_web_md/
└── ...
```

## 分割规则

### 标点分割

处理句号、问号、感叹号等：

```python
# 分割示例
输入: "Hello world. How are you?"
输出: ["Hello world.", "How are you?"]
```

**特殊情况处理**：
- 省略号 (...)：不分割
- 小数点（1.5）：不分割
- 缩写点（Dr.）：不分割

### 逗号分割

在标点分割基础上，按逗号进一步分割：

```python
# 验证语法有效性
"Hello, world, how are you?" → 可分割
"The quick brown fox jumps over the lazy dog" → 逗号处可分割
```

### 连接词分割

按连接词分割：

```python
# 英语连接词
and, or, but, because, although, while

# 中文连接词
和、或、但是、因为、虽然

# 日语连接词
て、そして、しかし
```

### 长句分割

对于仍然过长的句子，使用 LLM 进行语义分割：

```python
# 调用 LLM 分割
from core.prompts import get_split_prompt

prompt = get_split_prompt(
    sentence="这是一个很长的句子...",
    num_parts=2,
    word_limit=20
)

result = ask_gpt(prompt, resp_type="json")
```

## 配置选项

### 最大词数

```yaml
# config.yaml
max_split_length: 20  # 首次分割最大词数
```

### 分割策略

```python
# 修改分割行为
from core.spacy_utils import split_by_comma_main

# 调整：更细的分割
split_by_comma_main(
    text,
    max_comma_count=2,  # 降低逗号阈值
    min_length=3        # 最小分段长度
)
```

## 常见问题

### Q: 分割过于细碎？

**原因**：`max_split_length` 设置过低

**解决**：
```yaml
max_split_length: 25  # 增加到 25
```

### Q: 分割不够细？

**原因**：句子复杂，spaCy 未能识别

**解决**：依赖 LLM 语义分割（_3_2_split_meaning.py）

### Q: 模型下载失败？

**解决**：
```bash
# 手动下载
python -m spacy download en_core_web_md

# 或使用镜像
export HF_ENDPOINT=https://hf-mirror.com
```

## API 参考

### split_by_comma_main

```python
def split_by_comma_main(
    text: str,
    nlp,
    max_comma_count: int = 3,
    min_length: int = 3
) -> list:
    """按逗号分割句子"""
```

### split_sentences_main

```python
def split_sentences_main(
    text: str,
    nlp,
    connectors: list
) -> list:
    """按连接词分割句子"""
```

### split_long_by_root_main

```python
def split_long_by_root_main(
    segments: list,
    nlp,
    max_length: int = 20
) -> list:
    """分割过长句子"""
```

## 自测问题

使用 NLP 工具时，尝试回答以下问题：

1. **spaCy 在 VideoLingo 中的主要作用是什么？**
   
   <details>
   <summary>点击查看答案</summary>
   spaCy 主要用于句子分割（按标点符号和语义边界分割长句）。它比简单的正则表达式分割更智能，可以识别缩写、引号等特殊情况，避免错误的分割点。
   </details>

2. **为什么需要为不同语言加载不同的 spaCy 模型？**
   
   <details>
   <summary>点击查看答案</summary>
   不同语言有不同的语法结构和分词规则。例如，中文需要分词（将连续字序列切分为词），而英文已经有空格分隔。使用对应语言的模型可以获得最佳的分词和分割效果。
   </details>

3. **如何添加对新语言的 NLP 支持？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 在 `spacy_model_map` 中添加语言代码到 spaCy 模型的映射
   2. 下载对应的 spaCy 模型
   3. 测试分割效果，必要时调整参数
   4. 如果 spaCy 不支持该语言，可以考虑使用其他 NLP 库
   </details>

## 下一步

- 📖 阅读 [翻译原理](advanced/translation.md) 了解翻译系统
- 📖 阅读 [开发指南](development.md) 了解代码定制
