# 翻译系统深度解析

> VideoLingo 三步翻译流程原理与实现

## 学习目标

完成本教程后，你将能够：
- 理解 VideoLingo 翻译系统的设计理念
- 掌握三步翻译流程的实现细节
- 了解术语管理和上下文处理机制
- 优化翻译质量和效率

## 翻译系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                   VideoLingo 翻译流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 阶段 1：准备                                          │   │
│  │   • 术语提取 (_4_1_summarize.py)                     │   │
│  │   • 上下文摘要                                        │   │
│  │   • 自定义术语合并                                    │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                           │
│                   ▼                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 阶段 2：翻译 (_4_2_translate.py + translate_lines.py) │   │
│  │                                                        │   │
│  │  Step 1: Faithfulness (忠实翻译)                      │   │
│  │   • 准确传达原文含义                                   │   │
│  │   • 保持术语一致性                                     │   │
│  │   • 考虑上下文关系                                     │   │
│  │                                                        │   │
│  │  Step 2: Expressiveness (表达优化) [可选]            │   │
│  │   • 分析直译问题                                       │   │
│  │   • 优化语言流畅度                                     │   │
│  │   • 适配目标语言文化                                   │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                           │
│                   ▼                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 阶段 3：后处理                                        │   │
│  │   • 时间戳对齐                                        │   │
│  │   • 质量检查                                          │   │
│  │   • 结果保存                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 核心设计理念

### 为什么需要三步翻译？

传统机器翻译的问题：
- ❌ 缺乏上下文，逐句翻译导致不连贯
- ❌ 术语不统一，专业词汇翻译混乱
- ❌ 直译生硬，不符合目标语言表达习惯
- ❌ 文化差异导致理解偏差

VideoLingo 的解决方案：
- ✅ **上下文感知**：前后文 + 摘要 + 术语表
- ✅ **术语一致性**：AI 提取 + 用户自定义
- ✅ **两步优化**：忠实 → 反思 → 改编
- ✅ **Netflix 标准**：单行字幕，专业级质量

## 阶段 1：术语提取与上下文准备

### _4_1_summarize.py

**目标**：提取视频中的专业术语和核心概念

**输入**：分割后的句子列表

**输出**：`output/log/terminology.json`

```json
{
  "theme": "本视频介绍了深度学习在计算机视觉领域的应用...",
  "terms": [
    {
      "src": "Convolutional Neural Network",
      "tgt": "卷积神经网络",
      "note": "一种专门处理图像数据的深度学习模型"
    },
    {
      "src": "backpropagation",
      "tgt": "反向传播",
      "note": "神经网络训练的核心算法"
    }
  ]
}
```

**工作流程**：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 收集所有句子                                              │
│    → 按时间顺序拼接                                          │
│    → 限制在 summary_length 字符内                           │
├─────────────────────────────────────────────────────────────┤
│ 2. 构建术语表 Prompt                                         │
│    → 加载自定义术语（custom_terms.xlsx）                    │
│    → 排除已存在的术语                                        │
├─────────────────────────────────────────────────────────────┤
│ 3. 调用 LLM 提取术语                                         │
│    → 生成视频摘要（两句话）                                   │
│    → 提取专业术语（<15 个）                                  │
│    → 为每个术语提供翻译和注释                                 │
├─────────────────────────────────────────────────────────────┤
│ 4. 保存到 terminology.json                                   │
└─────────────────────────────────────────────────────────────┘
```

**Prompt 策略**（`core/prompts.py::get_summary_prompt`）：

```python
prompt = f"""
## Role
你是视频翻译专家和术语顾问，精通 {source_lang} 理解和 {target_lang} 表达优化

## Task
对于提供的 {source_lang} 视频文本：
1. 用两句话概括主要内容
2. 提取专业术语/名称并提供 {target_lang} 翻译（排除现有术语）
3. 为每个术语提供简要解释

Steps:
1. 主题摘要：
   - 快速扫描获得整体理解
   - 写两句话：第一句讲主题，第二句讲重点
2. 术语提取：
   - 标记专业术语和名称（排除已列出的）
   - 提供 {target_lang} 翻译或保持原文
   - 添加简要解释
   - 提取少于 15 个术语
"""
```

### 自定义术语支持

创建 `custom_terms.xlsx`：

| src | tgt | note |
|-----|-----|------|
| Machine Learning | 机器学习 | AI 的核心技术 |
| CNN | CNN | 卷积神经网络 |

加载逻辑：

```python
custom_terms = None
if os.path.exists('custom_terms.xlsx'):
    df = pd.read_excel('custom_terms.xlsx')
    custom_terms = {
        'terms': df.to_dict('records')
    }

# 传递给 Prompt
prompt = get_summary_prompt(content, custom_terms)
```

## 阶段 2：两步翻译流程

### translate_lines.py - 核心翻译逻辑

**设计原则**：

1. **上下文驱动**：每个句子都有前后文和摘要
2. **术语一致**：术语表作为翻译参考
3. **两步优化**：先准确，再流畅
4. **可恢复**：LLM 调用自动缓存

### Step 1: Faithfulness（忠实翻译）

**目标**：准确传达原文含义，不添加或删减内容

**Prompt 策略**（`get_prompt_faithfulness`）：

```python
prompt = f"""
## Role
你是专业的 Netflix 字幕翻译，精通 {source_lang} 和 {target_lang} 及其文化。
你的专长是准确理解原文的语义和结构，并忠实地翻译成 {target_lang}。

## Task
我们有一段 {source_lang} 原文字幕需要直接翻译成 {target_lang}。
这些字幕来自特定语境，可能包含特定主题和术语。

1. 逐行翻译原文字幕
2. 确保翻译忠实原文，准确传达原意
3. 考虑上下文和专业术语

<translation_principles>
1. 忠于原文：准确传达原文内容和含义，不随意更改、添加或省略
2. 术语准确：正确使用专业术语，保持术语一致性
3. 理解上下文：充分理解和反映文本的背景和上下关系
</translation_principles>

{shared_prompt}  # 包含前后文、摘要、术语表

<subtitles>
{lines}
</subtitles>
"""
```

**输出格式**：

```json
{
  "1": {
    "origin": "Hello, welcome to the tutorial",
    "direct": "你好，欢迎来到本教程"
  },
  "2": {
    "origin": "Today we'll learn about machine learning",
    "direct": "今天我们将学习机器学习"
  }
}
```

### Step 2: Expressiveness（表达优化）

**目标**：在保持原意的基础上，让译文更自然流畅

**Prompt 策略**（`get_prompt_expressiveness`）：

```python
prompt = f"""
## Role
你是专业的 Netflix 字幕翻译和语言顾问。
你的专长不仅在于准确理解原文，更在于优化 {target_lang} 翻译，
使其更符合目标语言的表达习惯和文化背景。

## Task
我们已有原文字幕的直接翻译版本。
你的任务是反思和改进这些直译，创建更自然流畅的 {target_lang} 字幕。

1. 逐行分析直译结果，指出存在的问题
2. 提供详细的修改建议
3. 基于分析进行意译
4. 不要在翻译中添加评论或解释，字幕是给观众看的
5. 意译中不要留空行，字幕是给观众看的

<Translation Analysis Steps>
请使用两步思考过程逐行处理文本：

1. 直译反思：
   - 评估语言流畅度
   - 检查语言风格是否与原文一致
   - 检查字幕简洁度，指出哪些翻译过于冗长

2. {target_lang} 意译：
   - 追求语境流畅和自然，符合 {target_lang} 表达习惯
   - 确保 {target_lang} 观众易于理解和接受
   - 调整语言风格以匹配主题（教程用口语，技术用专业术语等）
</Translation Analysis Steps>

{shared_prompt}

<subtitles>
{lines}
</subtitles>
"""
```

**输出格式**：

```json
{
  "1": {
    "origin": "Hello, welcome to the tutorial",
    "direct": "你好，欢迎来到本教程",
    "reflect": "直译准确但略显生硬，'本教程'较为正式",
    "free": "你好，欢迎来到这个教程"
  },
  "2": {
    "origin": "Today we'll learn about machine learning",
    "direct": "今天我们将学习机器学习",
    "reflect": "直译清晰，无需调整",
    "free": "今天我们来学习机器学习"
  }
}
```

### 上下文构建（`generate_shared_prompt`）

```python
def generate_shared_prompt(
    previous_content,   # 前文
    after_content,      # 后文
    summary,            # 摘要
    things_to_note      # 术语表
):
    return f"""### 上下文信息
<previous_content>
{previous_content}
</previous_content>

<subsequent_content>
{after_content}
</subsequent_content>

### 内容摘要
{summary}

### 注意事项
{things_to_note}"""
```

**上下文窗口大小**：

- **前文**：当前行之前的 3-5 句
- **后文**：当前行之后的 3-5 句
- **摘要**：整个视频的摘要（限制在 summary_length 字符）
- **术语表**：从 terminology.json 加载

### 翻译主流程（_4_2_translate.py）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 加载数据                                                  │
│    → split_result.json（分割后的句子）                      │
│    → terminology.json（术语表）                             │
├─────────────────────────────────────────────────────────────┤
│ 2. 分批处理                                                  │
│    → 按 chunk_size 分组（默认 5 行）                        │
│    → 避免单次 LLM 调用 token 过多                            │
├─────────────────────────────────────────────────────────────┤
│ 3. 并行翻译                                                  │
│    → 使用 ThreadPoolExecutor                                │
│    → 并发数由 max_workers 控制                               │
├─────────────────────────────────────────────────────────────┤
│ 4. 质量检查                                                  │
│    → 检查翻译相似度（是否有遗漏）                             │
│    → 检查行数一致性                                          │
├─────────────────────────────────────────────────────────────┤
│ 5. 时间戳对齐                                                │
│    → 将翻译结果与源时间戳对齐                                │
│    → 裁剪过长的翻译文本                                      │
├─────────────────────────────────────────────────────────────┤
│ 6. 保存结果                                                  │
│    → translation_result.xlsx                                │
└─────────────────────────────────────────────────────────────┘
```

## 阶段 3：后处理与质量保证

### 时间戳对齐

**问题**：翻译后的文本长度可能与原文不一致

**解决方案**：

```python
def align_timestamps(source_segments, translated_segments):
    """将翻译与源时间戳对齐"""
    result = []

    for src, tgt in zip(source_segments, translated_segments):
        # 获取源时间戳
        segment = {
            'start': src['start'],
            'end': src['end'],
            'text': tgt['text'],
            'source_text': src['text']
        }

        # 计算时长
        duration = src['end'] - src['start']

        # 如果翻译文本过长，使用 LLM 裁剪
    estimated_duration = estimate_text_duration(tgt['text'], target_lang)
    if estimated_duration > duration:
        trimmed = trim_text_by_llm(tgt['text'], duration)
        segment['text'] = trimmed

    result.append(segment)

    return result
```

### 文本裁剪 Prompt

```python
def get_subtitle_trim_prompt(text, duration):
    return f"""
## Role
你是专业的字幕编辑，在将长字幕交给配音演员前进行编辑和优化。
你的专长是巧妙地缩短字幕，同时确保原意和结构保持不变。

## INPUT
<subtitles>
字幕: "{text}"
时长: {duration} 秒
</subtitles>

## Processing Rules
考虑 a. 在不修改有意义内容的情况下减少填充词
      b. 省略不必要的修饰词或代词，例如：
      - "请解释你的思考过程" 可缩短为 "请解释思考过程"
      - "我们需要仔细分析这个复杂问题" 可缩短为 "我们需要分析这个问题"

## Processing Steps
请按以下步骤并在 JSON 输出中提供结果：
1. 分析：简要分析字幕结构、关键信息和可省略的填充词
2. 裁剪：根据规则和分析，通过处理规则优化字幕使其更简洁

## Output in only JSON format and no other text
```json
{{
    "analysis": "对字幕的简要分析，包括结构、关键信息和可能处理的位置",
    "result": "优化和缩短后的原字幕语言字幕"
}}
```
"""
```

### 质量检查

```python
def quality_check(source, translation):
    """检查翻译质量"""

    issues = []

    # 1. 检查行数
    if len(source) != len(translation):
        issues.append(f"行数不匹配: 源 {len(source)}, 译 {len(translation)}")

    # 2. 检查空行
    empty_count = sum(1 for t in translation if not t['text'].strip())
    if empty_count > 0:
        issues.append(f"发现 {empty_count} 行空翻译")

    # 3. 检查相似度
    similarity_ratio = calculate_similarity(source, translation)
    if similarity_ratio < 0.8:
        issues.append(f"翻译相似度过低: {similarity_ratio:.2%}")

    # 4. 检查术语一致性
    terms = load_terminology()
    for term in terms['terms']:
        if term['tgt'] not in str(translation):
            issues.append(f"术语 '{term['tgt']}' 可能未被正确使用")

    return issues
```

## 配置选项

### reflect_translate

控制是否启用第二步（表达优化）：

```yaml
# config.yaml
reflect_translate: true   # 启用两步翻译
reflect_translate: false  # 仅使用忠实翻译
```

**权衡**：
- `true`：翻译质量更高，但耗时更长（约 2 倍）
- `false`：速度快，但可能不够自然

### pause_before_translate

允许在翻译前手动编辑术语表：

```yaml
pause_before_translate: true
```

流程：
1. 术语提取完成
2. 程序暂停，提示用户编辑 `output/log/terminology.json`
3. 用户按 Enter 继续
4. 使用编辑后的术语表进行翻译

### summary_length

控制上下文摘要的大小：

```yaml
summary_length: 8000   # 默认，适合大多数模型
summary_length: 4000   # 减少 token 使用
summary_length: 16000  # 更详细的上下文
```

### max_split_length

控制首次分割的词数：

```yaml
max_split_length: 20   # 默认
```

**影响**：
- 过低（<18）：分割过细，影响翻译连贯性
- 过高（>22）：句子过长，后续字幕对齐困难

## 高级技巧

### 1. 提高术语一致性

创建领域特定的术语表：

```python
# custom_terms.xlsx
src                 tgt                note
------------------- ----------------- ------------------------
Large Language Model 大语言模型        LLM
Transformer         Transformer       注意力机制架构
Token               Token             文本最小单位
```

### 2. 优化翻译速度

```yaml
# 配置优化
max_workers: 8              # 提高 LLM 并发
summary_length: 4000        # 减少上下文长度
reflect_translate: false    # 跳过第二步（如果不需要）

# 使用更快的模型
api:
  model: 'gpt-4.1-mini'     # 或 'deepseek-v3'
```

### 3. 提高翻译质量

```yaml
# 使用更强的模型
api:
  model: 'claude-3-5-sonnet'

# 启用所有优化
reflect_translate: true
pause_before_translate: true  # 手动审核术语
summary_length: 12000         # 更详细的上下文
```

### 4. 处理特定格式

在 `custom_terms.xlsx` 中添加格式说明：

```python
# 在 note 中添加格式指导
src: "www.example.com"
tgt: "www.example.com"
note: "保持原样，不要翻译"
```

## 常见问题

### Q: 翻译质量不稳定？

**可能原因**：
1. 模型能力不足 → 使用更强模型（Claude/GPT-4）
2. 上下文不足 → 增加 `summary_length`
3. 术语不一致 → 添加自定义术语表

### Q: 翻译速度太慢？

**优化方案**：
1. 增加 `max_workers`
2. 使用更快的模型
3. 关闭 `reflect_translate`
4. 减少 `summary_length`

### Q: 翻译遗漏内容？

**原因**：LLM 输出格式错误

**解决方案**：
1. 检查 `output/gpt_log/error.json`
2. 更换支持 JSON 模式的模型
3. 启用 `llm_support_json: true`

### Q: 术语翻译不统一？

**解决方案**：
1. 使用 `custom_terms.xlsx` 明确指定术语
2. 启用 `pause_before_translate` 手动审核
3. 在术语表的 `note` 中提供更多上下文

## 自测问题

阅读完翻译原理后，尝试回答以下问题：

1. **为什么使用三步翻译而不是单次翻译？**
   
   <details>
   <summary>点击查看答案</summary>
   单次翻译容易出现直译问题，缺乏语境理解。三步流程通过「忠实翻译→反思改进→文化适配」逐步提升翻译质量，可减少 60% 以上的翻译错误。
   </details>

2. **`reflect_translate: false` 会跳过哪些步骤？**
   
   <details>
   <summary>点击查看答案</summary>
   会跳过第二步「表达优化」，只执行忠实翻译。这会加快处理速度约 50%，但翻译质量可能略有下降。
   </details>

3. **如何确保术语翻译一致性？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 创建 `custom_terms.xlsx` 明确指定术语翻译
   2. 启用 `pause_before_translate` 手动审核术语表
   3. 在术语表的 `note` 列提供更多上下文指导
   </details>

## 下一步

- 🔧 阅读 [配置说明](../configuration.md) 了解翻译相关配置
- 📖 阅读 [架构设计](../architecture.md) 了解整体流程
