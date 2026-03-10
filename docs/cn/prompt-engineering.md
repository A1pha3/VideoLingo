# Prompt 工程指南

> VideoLingo LLM Prompt 优化与定制

## 学习目标

完成本教程后，你将能够：
- 理解 VideoLingo Prompt 架构
- 优化翻译质量
- 定制 Prompt 行为
- 调试 Prompt 问题

## Prompt 架构

```
core/prompts.py (所有 Prompt 定义)
├── get_split_prompt()         # 句子分割
├── get_summary_prompt()       # 摘要与术语提取
├── get_prompt_faithfulness()  # 忠实翻译
├── get_prompt_expressiveness() # 表达优化
├── get_align_prompt()         # 字幕对齐
├── get_subtitle_trim_prompt() # 字幕裁剪
└── get_correct_text_prompt()  # 文本清理
```

## Prompt 设计原则

### 1. 清晰的角色定义

```python
prompt = f"""
## Role
你是专业的 Netflix 字幕翻译，精通 {src_lang} 和 {tgt_lang}。

## Task
翻译以下字幕...
"""
```

### 2. 明确的任务描述

```python
prompt = f"""
## Task
1. 逐行翻译原文字幕
2. 确保翻译忠实原文
3. 考虑上下文和专业术语
"""
```

### 3. 具体的输出格式

```python
prompt = f"""
## Output in only JSON format and no other text
```json
{{
    "result": "翻译结果"
}}
```

Note: Start you answer with ```json and end with ```
```
```

### 4. 上下文信息

```python
prompt = f"""
### Context Information
<previous_content>
{previous_content}
</previous_content>

<subsequent_content>
{after_content}
</subsequent_content>

### Content Summary
{summary}

### Points to Note
{things_to_note}
"""
```

## 核心 Prompt 详解

### 句子分割 Prompt

**目标**：将长句分成 2-3 个短句

**关键要素**：
- Netflix 标准参考
- 均衡长度要求
- 自然分割点
- 避免重复词处理

```python
def get_split_prompt(sentence, num_parts=2, word_limit=20):
    prompt = f"""
## Role
你是专业的 Netflix 字幕分割专家，精通 {language}。

## Task
将给定字幕文本分成 {num_parts} 部分，每部分少于 {word_limit} 词。

1. 遵循 Netflix 字幕标准保持句子意义连贯
2. 最重要：各部分长度大致相等（最少 3 个词）
3. 在标点或连接词等自然点分割
4. 如果给定文本是重复词，只需在重复词中间分割

## Steps
1. 分析句子结构、复杂性和关键分割挑战
2. 用 [br] 标记生成两种替代分割方案
3. 比较两种方案，突出其优缺点
4. 选择最佳分割方案
"""
    return prompt.strip()
```

### 术语提取 Prompt

**目标**：提取专业术语和提供翻译

**关键要素**：
- 视频主题概括
- 术语数量限制（<15）
- 排除已有术语
- 提供简要解释

### 翻译 Prompt（两步）

#### 第一步：忠实翻译

**目标**：准确传达原文含义

**关键要素**：
- 逐行翻译
- 保持术语一致性
- 考虑上下文
- 不添加不删减

#### 第二步：表达优化

**目标**：让翻译更自然流畅

**关键要素**：
- 分析直译问题
- 指出冗长部分
- 适配目标语言文化
- 调整语言风格

## Prompt 优化技巧

### 1. 少样本提示

添加示例提高质量：

```python
prompt = f"""
## Examples

输入: "Hello, world!"
输出: {{"translation": "你好，世界！"}}

输入: "How are you?"
输出: {{"translation": "你好吗？"}}

## INPUT
{user_input}
"""
```

### 2. 思维链

引导模型逐步思考：

```python
prompt = f"""
## Steps
1. 首先，分析原文的语法结构
2. 然后，识别专业术语
3. 接着，确定目标语言的对应表达
4. 最后，生成自然流畅的翻译
"""
```

### 3. 负面约束

明确告诉模型不要做什么：

```python
prompt = f"""
## 禁止行为
- 不要在翻译中添加评论或解释
- 不要留下空行
- 不要改变原文的技术含义
"""
```

### 4. 格式强制

```python
prompt = f"""
## Output in only JSON format and no other text
```json
...
```

Note: Start you answer with ```json and end with ```  # 强制格式
"""
```
```

## 调试 Prompt

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| JSON 解析失败 | 模型不遵循格式 | 启用 JSON 模式 |
| 翻译遗漏 | 内容过长 | 减小 batch_size |
| 术语不一致 | 上下文不足 | 增加 summary_length |
| 语气不当 | 角色定义不清 | 强化角色描述 |

### 验证输出

```python
def validate_translation(response, original_lines):
    """验证翻译响应"""
    errors = []

    # 检查行数
    if len(response) != len(original_lines):
        errors.append(f"行数不匹配: {len(response)} vs {len(original_lines)}")

    # 检查空行
    for i, line in enumerate(response):
        if not line.get('text', '').strip():
            errors.append(f"第 {i+1} 行为空")

    return errors
```

### A/B 测试

```python
# 测试不同 Prompt 版本
prompts = {
    "v1": get_prompt_v1(text),
    "v2": get_prompt_v2(text),
    "v3": get_prompt_v3(text),
}

for version, prompt in prompts.items():
    result = ask_gpt(prompt, resp_type="json")
    score = evaluate_quality(result)
    print(f"{version}: {score}")
```

## 自定义 Prompt

### 添加新的 Prompt

在 `core/prompts.py` 中添加：

```python
def get_my_custom_prompt(input_data, context=""):
    """我的自定义 Prompt"""
    prompt = f"""
## Role
你是...

## Task
处理以下数据...

## INPUT
{input_data}

## Output Format
```json
{{
    "result": "..."
}}
```
"""
    return prompt.strip()
```

### 使用自定义 Prompt

```python
from core.prompts import get_my_custom_prompt
from core.utils.ask_gpt import ask_gpt

prompt = get_my_custom_prompt(data, context)
result = ask_gpt(prompt, resp_type="json", log_title="my_custom")
```

## Prompt 模板

### 翻译类模板

```python
translation_template = """
## Role
你是专业的 {role}，精通 {src_lang} 和 {tgt_lang}。

## Task
{task_description}

{context_section}

## INPUT
{input_text}

## Output in only JSON format and no other text
```json
{output_format}
```
"""
```

### 分析类模板

```python
analysis_template = """
## Role
你是 {role}，专长于 {expertise}。

## Task
{task_description}

## Analysis Steps
1. {step_1}
2. {step_2}
3. {step_3}

## INPUT
{input_text}

## Output in only JSON format and no other text
```json
{{
    "analysis": "分析结果",
    "conclusion": "结论"
}}
```
"""
```

## 最佳实践

1. **明确性 > 创意性**：清晰的指令比巧妙的措辞更重要
2. **测试多种模型**：不同模型对同一 Prompt 响应不同
3. **迭代优化**：根据输出质量持续调整
4. **记录有效版本**：保存好的 Prompt 版本
5. **版本控制**：Prompt 变更也应版本控制

## 自测问题

设计 Prompt 时，尝试回答以下问题：

1. **如何确保 LLM 输出符合预期的 JSON 格式？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 在 Prompt 末尾明确要求「Output in only JSON format and no other text」
   2. 启用 JSON 模式（`llm_support_json: true`）
   3. 提供完整的 JSON 示例结构
   4. 使用 `ask_gpt` 的 `resp_type="json"` 参数自动解析
   </details>

2. **为什么需要在 Prompt 中提供上下文？**
   
   <details>
   <summary>点击查看答案</summary>
   上下文帮助 LLM 理解翻译场景，包括：视频主题、前文后文、术语表等。充足的上下文可以减少 50% 以上的翻译错误，确保术语一致性和语义连贯性。
   </details>

3. **如何调试 Prompt 问题？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 检查 `output/gpt_log/` 中的 LLM 调用日志
   2. 使用 A/B 测试对比不同 Prompt 版本
   3. 逐步简化 Prompt 定位问题
   4. 尝试不同的模型（某些模型对特定格式支持更好）
   </details>

## 下一步

- 📖 阅读 [翻译原理](advanced/translation.md) 了解翻译系统
- 📖 阅读 [开发指南](development.md) 了解代码定制
