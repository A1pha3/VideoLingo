# batch_processor.py 功能详解

## 文档目标

这份文档专门说明 VideoLingo 现有批处理入口 `batch/utils/batch_processor.py` 的职责、输入输出、执行流程、状态管理、失败重试机制，以及它与其他模块之间的关系。

如果后续要把 VideoLingo 改造成“目录驱动的命令行客户端”，这个文件就是最直接的复用入口分析。

## 一句话结论

`batch_processor.py` 是一个**基于 Excel 任务表驱动的串行批处理控制器**。

它本身不负责翻译、字幕或配音算法，而是负责：

- 校验批处理任务是否合法
- 按 Excel 行顺序依次执行任务
- 在任务开始前临时切换语言配置
- 调用单视频处理管线
- 把结果状态写回 Excel
- 对失败任务提供“下次自动重试”的入口

可以把它理解为：

> 一个把 `tasks_setting.xlsx` 翻译成“逐个调用 process_video()”的调度器。

## 文件定位

文件路径：

```text
batch/utils/batch_processor.py
```

它所在的 batch 模块分工大致如下：

- `batch/utils/settings_check.py`：校验 Excel 配置与输入文件
- `batch/utils/batch_processor.py`：批处理调度器
- `batch/utils/video_processor.py`：单视频处理执行器

三者关系是：

```text
tasks_setting.xlsx
        |
        v
batch_processor.py
   |        \
   |         \__ settings_check.py
   |
   \____________ video_processor.py
                    |
                    v
                 core/*
```

## 直接依赖

`batch_processor.py` 的关键依赖有以下几类。

### 1. 配置校验依赖

```python
from batch.utils.settings_check import check_settings
```

用途：

- 检查 `batch/tasks_setting.xlsx` 是否可读
- 检查 `batch/input` 中的视频文件是否和 Excel 对得上
- 检查 `Dubbing` 字段是否合法

如果校验失败，`process_batch()` 会直接终止，不进入任何视频处理。

### 2. 单视频处理依赖

```python
from batch.utils.video_processor import process_video
```

用途：

- 处理单个任务对应的视频
- 串起转录、翻译、字幕生成、可选配音、视频合成
- 返回成功或失败信息

`batch_processor.py` 自己不做视频处理，只把当前行任务交给 `process_video()`。

### 3. 配置读写依赖

```python
from core.utils.config_utils import load_key, update_key
```

用途：

- 读取当前全局配置中的 `whisper.language`
- 读取当前全局配置中的 `target_language`
- 在处理单个任务前，按 Excel 行内容临时改写语言配置
- 任务完成后恢复原配置

这意味着这个批处理器依赖的是**全局配置切换模型**，不是任务内局部配置对象。

### 4. 任务表读写依赖

```python
import pandas as pd
```

用途：

- 读取 `batch/tasks_setting.xlsx`
- 修改当前行 `Status`
- 处理完每个任务后把整个表重新写回 Excel

### 5. 文件恢复依赖

```python
import shutil
```

用途：

- 当任务是“失败重试”时，把之前归档到 `batch/output/ERROR/<video_name>/` 的内容恢复回 `output/`

## 对外入口

这个模块的对外入口只有一个：

```python
def process_batch():
```

并且文件底部直接提供了脚本化运行方式：

```python
if __name__ == "__main__":
    process_batch()
```

因此它既可以这样调用：

```bash
python -m batch.utils.batch_processor
```

也可以被其他 Python 代码以函数形式调用。

## 输入模型

`batch_processor.py` 的输入不是命令行参数，而是两个固定来源。

### 1. 固定输入目录

```text
batch/input/
```

这里存放本地视频文件。

### 2. 固定任务表

```text
batch/tasks_setting.xlsx
```

任务表至少依赖以下列：

- `Video File`
- `Source Language`
- `Target Language`
- `Dubbing`
- `Status`

这些列共同定义了“批处理任务队列”。

## 输出模型

`batch_processor.py` 自身不直接生成视频，它的输出体现在两个地方。

### 1. Excel 状态更新

处理结果会写回：

```text
batch/tasks_setting.xlsx
```

写入 `Status` 列的值大致有两种：

- `Done`
- `Error: <step> - <message>`

### 2. 批处理产物目录

单视频处理实际生成的结果最终会进入：

```text
batch/output/
```

如果任务失败，相关结果通常会被归入：

```text
batch/output/ERROR/
```

这里的实际搬运动作不是在 `batch_processor.py` 里完成的，而是 `video_processor.py` 内部调用 `cleanup()` 完成的。

## 代码结构拆解

这个文件很小，核心只有两个函数：

- `record_and_update_config(source_language, target_language)`
- `process_batch()`

下面分别解释。

## 函数一：record_and_update_config

### 作用

这个函数的职责是：

1. 先记住当前系统里的原始语言配置
2. 再根据当前任务行的配置临时覆盖全局配置
3. 最后把原始值返回给调用方，供处理完成后恢复

### 输入

- `source_language`
- `target_language`

它们来自 Excel 当前行。

### 内部逻辑

先读取全局原值：

```python
original_source_lang = load_key('whisper.language')
original_target_lang = load_key('target_language')
```

然后按需覆盖：

- 如果 `source_language` 不为空，更新 `whisper.language`
- 如果 `target_language` 不为空，更新 `target_language`

最后返回旧值：

```python
return original_source_lang, original_target_lang
```

### 为什么这样设计

因为现有核心流程大量依赖 `config.yaml` 中的全局配置，而不是函数参数传递。批处理器只能通过“改配置 -> 跑任务 -> 恢复配置”的方式，为每一行任务切换语言。

### 这个设计的含义

优点：

- 改动少，直接兼容现有核心模块

缺点：

- 存在全局状态副作用
- 天然只适合串行运行
- 不适合并发处理多个任务

## 函数二：process_batch

这是整个模块的主流程。

可以按 7 个阶段来理解。

## 阶段 1：预检查

```python
if not check_settings():
    raise Exception("Settings check failed")
```

含义是：

- 先校验输入目录和任务表是否一致
- 如果不一致，直接抛异常中止

这里的策略是“先失败，后处理”，避免处理过程中才发现输入不完整。

### 预检查实际覆盖内容

由 `settings_check.py` 实现，主要包括：

- `batch/input` 是否存在
- Excel 中的本地文件是否在 `batch/input` 中真实存在
- `Video File` 是否是合法 URL 或本地文件
- `Dubbing` 是否为 `0` 或 `1`
- 输入目录里是否有未在 Excel 中登记的文件

需要注意的是：

- 如果输入目录里有多余文件，也会导致 `check_settings()` 返回失败
- 这说明当前 batch 模式强调“目录与任务表严格一致”

## 阶段 2：加载任务表

```python
df = pd.read_excel('batch/tasks_setting.xlsx')
```

之后所有任务都以 DataFrame 行遍历的方式执行。

这意味着：

- Excel 行顺序就是任务执行顺序
- 批处理器没有额外的队列优先级机制
- 也没有并发调度机制

## 阶段 3：筛选需要执行的任务

核心判断条件是：

```python
if pd.isna(row['Status']) or 'Error' in str(row['Status']):
```

这代表只有两类任务会被执行：

1. `Status` 为空的任务
2. `Status` 包含 `Error` 的任务

反过来说，以下任务会被跳过：

- `Status = Done`
- 任何非空且不包含 `Error` 的状态值

### 这相当于什么状态机

这个模块隐含了一个非常简单的状态机：

```text
空状态 -> 执行 -> Done
空状态 -> 执行 -> Error: ...
Error: ... -> 重试 -> Done
Error: ... -> 重试 -> Error: ...
Done -> 跳过
```

它没有显式枚举状态，只是通过字符串模式匹配来识别状态。

### 这个设计的优点和问题

优点：

- 实现简单
- 非常容易人工查看和修改

问题：

- 依赖字符串约定，不够结构化
- 不便于更细粒度的自动化处理
- 一旦状态格式变化，筛选逻辑就可能失效

## 阶段 4：区分首次处理和失败重试

进入待执行分支后，代码会先判断当前任务是不是失败重试：

- 如果当前 `Status` 含 `Error`
- 则认定为重试任务

### 首次处理

首次处理只会打印一个当前任务面板：

```text
Now processing task: <video_file>
Task <index>/<total>
```

### 失败重试

失败重试除了打印“Retry Task”面板，还会尝试恢复之前失败时留下的工作目录内容。

恢复来源是：

```text
batch/output/ERROR/<video_name>/
```

恢复目标是：

```text
output/
```

### 为什么要恢复文件

原因在于 `video_processor.py` 和底层核心流程使用固定的全局工作目录 `output/`。如果要在失败基础上继续重试，有些中间文件可能仍然有价值，因此这里会尝试把 `ERROR` 目录中的内容复制回 `output/`。

### 恢复逻辑细节

恢复时会遍历 `error_folder` 中的所有项目：

- 如果是目录，先删除 `output/` 下同名目录，再整目录复制
- 如果是文件，先删除 `output/` 下同名文件，再复制文件

这说明它采用的是“失败现场整体恢复”的策略，而不是按文件类型精细恢复。

### 如果找不到 ERROR 目录会怎样

代码只打印警告：

```text
Warning: Error folder not found
```

不会中止整个批处理。随后仍然继续尝试执行当前任务。

## 阶段 5：根据任务行临时切换配置

当前任务开始前，会读取：

- `Source Language`
- `Target Language`

然后调用：

```python
original_source_lang, original_target_lang = record_and_update_config(...)
```

这个阶段的核心目的是：

- 让当前任务可以覆盖默认识别语言和目标翻译语言
- 但处理结束后不污染后续任务和系统默认设置

### 注意点

这里只处理语言配置，不处理其他字段，比如：

- TTS 模型
- LLM 模型
- API Key
- 烧录字幕开关
- FFmpeg/GPU 等配置

这些仍然完全依赖当前的全局配置文件。

## 阶段 6：调用单视频处理器

实际执行代码是：

```python
status, error_step, error_message = process_video(video_file, dubbing, is_retry)
```

这里三个输入分别表示：

- `video_file`：当前任务的视频文件名或 URL
- `dubbing`：是否生成配音
- `is_retry`：当前任务是不是失败重试

### dubbing 的来源

```python
dubbing = 0 if pd.isna(row['Dubbing']) else int(row['Dubbing'])
```

含义是：

- 为空时按 `0` 处理
- 非空则强制转 int

因此最终实际支持的是：

- `0`：只做字幕处理
- `1`：在字幕处理基础上继续做配音

### process_video 做了什么

`batch_processor.py` 不展开这些细节，但从依赖关系看，`process_video()` 会依次完成：

1. 准备 `output/` 工作目录
2. 下载或复制输入视频
3. 调用 Whisper 转录
4. 调用 NLP 与 LLM 进行断句和翻译
5. 生成并对齐字幕
6. 把字幕合成到视频
7. 如果启用配音，再生成音频并合成最终视频
8. 最后归档到 `batch/output/` 或 `batch/output/ERROR/`

### 返回值如何解释

`process_video()` 返回三元组：

```python
(status, error_step, error_message)
```

含义是：

- `status = True`：该视频处理成功
- `status = False`：该视频处理失败
- `error_step`：失败发生在哪个步骤
- `error_message`：失败的错误信息

## 阶段 7：写回状态并恢复配置

这是 `finally` 块中的逻辑，也是整个批处理最关键的“收尾阶段”。

无论成功还是失败，都会执行：

1. 恢复原始语言配置
2. 把状态写入 Excel
3. 主动触发垃圾回收
4. 暂停 1 秒

### 恢复配置

```python
update_key('whisper.language', original_source_lang)
update_key('target_language', original_target_lang)
```

目的是避免当前任务的语言设置影响后续任务。

### 生成状态字符串

成功时：

```python
status_msg = "Done"
```

失败时：

```python
status_msg = f"Error: {error_step} - {error_message}"
```

如果是外层未捕获异常，则写成：

```python
Error: Unhandled exception - <message>
```

### 写回 Excel

```python
df.at[index, 'Status'] = status_msg
df.to_excel('batch/tasks_setting.xlsx', index=False)
```

这里的写法是“每处理完一行，就把整个 DataFrame 重写一遍 Excel”。

### 为什么这么做

优点：

- 即使程序处理中途崩溃，之前已经完成的任务状态仍然保留
- 下次启动可以从最新状态继续

缺点：

- Excel 文件会被频繁写入
- 如果用户在运行过程中打开并占用 Excel，可能导致写回失败

## 跳过逻辑

对于不需要执行的任务，代码直接输出：

```text
Skipping task: <video> - Status: <status>
```

这说明批处理器默认认为：

- 只要状态不是空，且不包含 `Error`
- 就代表这个任务不应再次执行

这是一种非常宽松的“已完成”判断。

例如，如果有人把 `Status` 手工改成：

- `OK`
- `Done manually`
- `Skip`

程序同样会跳过该任务。

## 结束行为

所有任务遍历结束后，会打印一个完成面板：

```text
All tasks processed!
Check out in batch/output!
```

这个提示只表示：

- 任务遍历完成了

不表示：

- 所有任务都成功

因此使用者仍然需要回看 Excel 的 `Status` 列，确认哪些任务成功、哪些失败。

## 这个模块的职责边界

理解这个模块时，最重要的是分清楚它“做什么”和“不做什么”。

### 它负责什么

- 读取任务清单
- 校验任务合法性
- 决定哪些任务要执行
- 决定哪些任务要跳过
- 区分首次执行和失败重试
- 临时切换语言配置
- 调用单视频处理器
- 把执行结果写回任务表

### 它不负责什么

- 不直接处理视频内容
- 不实现转录逻辑
- 不实现翻译逻辑
- 不实现字幕对齐逻辑
- 不实现配音逻辑
- 不直接管理 `batch/output` 的归档细节
- 不提供目录参数化能力
- 不提供结构化日志文件

## 这个模块的优点

从工程复用角度看，它有几个明显优点。

### 1. 结构简单

代码量很小，核心逻辑一眼能读完。

### 2. 调度职责清楚

它不掺杂具体媒体处理逻辑，主要负责“调度”和“状态记录”。

### 3. 容易人工干预

任务表是 Excel，用户可以直接：

- 调整行顺序
- 修改语言
- 修改配音开关
- 查看失败原因
- 手动编辑状态后重新运行

### 4. 支持断点续跑

只要 Excel 状态还在，重新运行后就能自动跳过已完成项，重试失败项。

## 这个模块的局限性

如果要把它作为后续命令行客户端基础，这些局限性必须看清楚。

### 1. 强依赖 Excel

任务定义、状态记录都绑在 `tasks_setting.xlsx` 上，不利于自动化脚本和服务集成。

### 2. 强依赖固定目录

它假设输入在 `batch/input`，输出在 `output` 与 `batch/output`，不支持调用方传入目录。

### 3. 依赖全局配置切换

每个任务通过改写 `config.yaml` 的全局语言配置运行，这种模式不适合并发。

### 4. 状态格式不结构化

用字符串 `Done` 或 `Error: ...` 表示状态，适合人工阅读，不适合系统消费。

### 5. 重试恢复比较粗糙

恢复策略是整目录覆盖恢复，不区分哪些中间文件真的需要保留。

### 6. 无细粒度结果索引

虽然结果会归档，但 `batch_processor.py` 本身并不输出一个清晰的“输入文件 -> 最终成品文件”的结构化映射。

## 适合它的使用场景

这个模块适合下面几类场景：

- 人工维护少量或中等规模批任务
- 用户愿意用 Excel 管理任务清单
- 任务必须串行执行
- 主要运行环境是本地桌面或单机脚本

## 不适合它的使用场景

它不适合直接承担这些需求：

- 只接受两个路径参数的纯 CLI
- 服务化接口调用
- 多任务并发处理
- 大规模自动调度
- 机器可读的批处理状态追踪

## 如果后续要复用它，最值得保留的部分是什么

如果将来要做新的目录驱动 CLI，最值得保留的不是整个 `batch_processor.py`，而是它体现出来的这几个思路：

### 1. 任务串行调度模型

按顺序逐个处理，这与当前底层全局工作目录模型是兼容的。

### 2. 每任务独立状态更新

每完成一个任务就持久化结果，这一点非常重要，适合断点续跑。

### 3. 失败任务可重试

当前“空状态执行、Error 状态重试、Done 状态跳过”的模式很容易迁移到 JSON 状态文件中。

### 4. 调用单视频处理器而不是重复造轮子

真正应该复用的核心还是：

```python
process_video(video_file, dubbing, is_retry)
```

## 总结

`batch/utils/batch_processor.py` 本质上是 VideoLingo 当前 batch 模式的“任务调度层”。

它解决的是：

- 如何从 Excel 任务表中读取任务
- 如何决定任务是否执行
- 如何把任务交给单视频处理器
- 如何把结果写回任务表

它没有解决的是：

- 如何用更现代的 CLI 参数驱动批处理
- 如何用结构化状态文件记录批次结果
- 如何让输入输出目录由调用方控制

因此，如果你的目标是“理解现有 batch 入口能不能直接承接新需求”，答案是：

- **它适合作为调度逻辑参考**
- **不适合作为最终双路径 CLI 直接复用入口**
- **真正应该重点复用的是它调用的 `process_video()`，以及它的状态推进思路**
