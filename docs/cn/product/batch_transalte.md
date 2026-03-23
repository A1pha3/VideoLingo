# 基于现有 VideoLingo 能力设计双路径批量翻译客户端

## 结论

当前 VideoLingo **没有**一个可以直接满足下面需求的命令行 client：

1. 命令行只接收两个参数：输入视频路径、输出视频路径。
2. 自动扫描输入路径中的视频。
3. 对尚未成功处理的视频按顺序执行：翻译、生成字幕、配音。
4. 将最终配音成功的视频放入输出路径，并记录成功结果。

VideoLingo 现有最接近的能力是批处理模式：

- 入口是 `python -m batch.utils.batch_processor`
- 依赖固定目录 `batch/input`
- 依赖任务表 `batch/tasks_setting.xlsx`
- 输出归档到 `batch/output`
- 处理状态记录在 Excel 的 `Status` 列

这套能力已经具备“按顺序处理多个视频”和“记录任务状态”的基础，但**不是一个双路径参数 CLI**。

## 现状分析

### 已有能力

现有仓库已经具备完整的单视频处理管线：

- `batch/utils/video_processor.py` 中的 `process_video(file, dubbing=False, is_retry=False)` 已经把单视频流程串起来。
- 其中会顺序调用：
  - 转录 `_2_asr.transcribe()`
  - 断句 `_3_1_split_nlp.split_by_spacy()`、`_3_2_split_meaning.split_sentences_by_meaning()`
  - 总结与翻译 `_4_1_summarize.get_summary()`、`_4_2_translate.translate_all()`
  - 字幕切分与对齐 `_5_split_sub.split_for_sub_main()`、`_6_gen_sub.align_timestamp_main()`
  - 字幕合成 `_7_sub_into_vid.merge_subtitles_to_video()`
  - 配音流程 `_8_1_audio_task.gen_audio_task_main()`、`_8_2_dub_chunks.gen_dub_chunks()`、`_9_refer_audio.extract_refer_audio_main()`、`_10_gen_audio.gen_audio()`、`_11_merge_audio.merge_full_audio()`、`_12_dub_to_vid.merge_video_audio()`
- 成功后会调用 `cleanup()` 把 `output` 下的结果归档。

现有批处理控制器也已经具备顺序处理能力：

- `batch/utils/batch_processor.py` 会遍历任务表。
- 对未完成或失败任务进行处理。
- 任务执行后把结果写回 Excel。

### 为什么现有能力不能直接满足需求

虽然现有批处理已经很接近，但它与目标需求之间还有几个关键差距：

1. **入口不对**

现有入口不是 `input_dir output_dir` 两个参数，而是固定读取 Excel 和固定目录。

1. **输入模型不对**

现有系统要求把待处理文件放到 `batch/input`，并且在 `batch/tasks_setting.xlsx` 中显式登记任务。

1. **输出模型不对**

现有系统归档到 `batch/output/<video_name>/`，不是直接按调用方指定的输出目录落产物。

1. **状态记录方式不对**

现有系统把状态写入 Excel，不适合一个纯 CLI 场景，也不方便脚本、调度器或其他服务读取。

1. **核心流程存在全局目录假设**

现有核心模块普遍默认使用仓库根目录下的 `output/` 作为工作目录，说明它天然更适合**串行处理**，不适合并发多任务。

## 设计目标

设计一个新的轻量命令行 client，满足以下目标：

1. 命令格式足够简单，只需要两个参数。
2. 尽量复用现有 `batch` 和 `core` 的能力，不重写核心流程。
3. 不引入新的复杂配置中心。
4. 以“串行、稳定、可恢复”为优先。
5. 最终输出目录中能直接拿到成功配音的视频。
6. 能记录哪些视频已成功处理，下次运行自动跳过。

## 推荐方案

### 方案定位

新增一个“薄封装” CLI，例如：

```bash
python -m cli.batch_translate <input_dir> <output_dir>
```

或者：

```bash
python tools/batch_translate.py <input_dir> <output_dir>
```

推荐放在仓库内独立的新入口模块中，而不是改造 `batch_processor.py`。原因很简单：

- `batch_processor.py` 的职责是“Excel 驱动批处理”。
- 新需求的职责是“目录驱动批处理”。
- 两者的批处理模型不同，但都可以复用 `process_video()`。

因此，最优雅的方式不是继续给 Excel 批处理打补丁，而是新增一个**目录适配层**。

## 最小复用架构

### 核心复用点

新 client 只复用三层能力：

1. **单视频处理能力**

直接复用：

- `batch.utils.video_processor.process_video`

1. **结果归档能力**

继续沿用 `process_video()` 内部已有的 `cleanup()` 逻辑，让每个视频处理完成后先进入既有归档目录。

1. **配置读取能力**

继续使用现有 `config.yaml` 和 `core.utils.config_utils.load_key()`。

也就是说，新 CLI 不去重写“翻译、字幕、配音”的业务逻辑，只做以下几件事：

- 扫描输入目录
- 识别哪些视频未成功处理
- 顺序调用 `process_video(..., dubbing=True)`
- 从既有归档目录中拿到最终产物
- 拷贝到调用方指定输出目录
- 写入结构化状态文件

## 建议的目录与文件职责

建议新增以下模块：

```text
cli/
  __init__.py
  batch_translate.py
```

如果希望更贴近当前仓库风格，也可以放在：

```text
tools/
  batch_translate.py
```

### 模块职责

`batch_translate.py` 负责：

1. 解析命令行参数。
2. 校验输入目录与输出目录。
3. 扫描待处理视频。
4. 读取并更新状态文件。
5. 顺序调用 `process_video()`。
6. 从归档目录提取 `output_dub.mp4` 到输出目录。
7. 输出最终处理报告。

## CLI 设计

### 命令格式

严格按需求，可以设计为两个位置参数：

```bash
python -m cli.batch_translate /path/to/input /path/to/output
```

为了兼顾“简单好用”和“可扩展”，建议把 CLI 设计成**双模式**：

### 模式一：简单模式

保留最核心的双参数形式：

```bash
python -m cli.batch_translate <input_dir> <output_dir>
```

这个模式服务于 80% 的日常使用场景：

- 单个输入目录
- 单个输出目录
- 统一使用当前 `config.yaml`
- 自动断点续跑

### 模式二：任务文件模式

当出现“多个输入目录、多个输出目录、每组任务有不同配置”时，不建议继续增加大量命令行参数，而是增加一个可选任务文件：

```bash
python -m cli.batch_translate --job-file jobs.yaml
```

推荐原因：

- 多输入多输出本质上已经不是一个简单命令，而是一组批任务
- 如果继续堆积参数，CLI 很快会变得难记、难维护、难扩展
- 任务文件更适合表达目录映射、过滤规则和少量任务级覆盖项

这意味着最终设计不是“只能两个参数”，而是：

- 默认入口仍然是双参数
- 高级场景升级为任务文件模式

这是一个收益很高的扩展点。

### 参数语义

- 第一个参数：输入视频目录
- 第二个参数：输出结果目录

### 推荐保留的可选参数

为了保持 CLI 简洁，建议只增加少数几个真正高收益的可选参数。

#### 1. `--recursive`

作用：

- 递归扫描输入目录下的子目录

收益：

- 很多真实视频目录并不是平铺结构
- 这个参数非常常用，且实现成本低

#### 2. `--dry-run`

作用：

- 只做扫描、过滤、配置检查和任务计划展示，不真正执行翻译

收益：

- 非常适合大批量任务启动前做预检查
- 可以提前发现空目录、非法格式、重复文件、状态冲突等问题

#### 3. `--force`

作用：

- 强制重跑已经成功的视频

收益：

- 当用户更换了 `config.yaml` 中的目标语言、TTS、字幕设置后，往往需要重跑已有成功任务
- 不加这个参数，用户只能手工删状态文件或删输出文件，体验较差

建议默认行为仍然是“自动跳过已成功任务”，只有显式指定 `--force` 才重跑。

#### 4. `--job-file`

作用：

- 读取 YAML 或 JSON 任务文件，支持多组输入输出映射

收益：

- 这是处理多目录场景最干净的方式
- 比增加 `--input-dir`、`--output-dir` 的数组参数更清晰

### 不建议一开始就加入的参数

以下参数短期看似有用，但第一版不建议加入：

- `--workers`
- `--parallel`
- `--output-name-template`
- `--source-language`
- `--target-language`
- `--tts-model`

原因：

- 并发参数会与当前全局工作目录模型冲突
- 过多业务参数会和 `config.yaml` 形成双配置源，增加歧义
- 命名模板虽然灵活，但收益远低于复杂度

### 处理范围

输入目录下所有“允许的视频格式”文件都纳入处理范围。格式判断可以直接复用现有配置中的 `allowed_video_formats`。

### 处理策略

固定执行“字幕 + 配音”完整流程，也就是：

```python
process_video(file_name, dubbing=True, is_retry=False)
```

这与需求完全对齐，因为你要求最终输出的是“配音成功的视频文件”。

## 处理流程设计

### 总流程

```text
1. 读取 input_dir
2. 过滤出视频文件
3. 读取 output_dir/status.json
4. 找出未成功的视频
5. 对每个视频串行执行：
   - 复制到 batch/input
   - 调用 process_video(..., dubbing=True)
   - 从 batch/output/<video_name>/output_dub.mp4 复制到 output_dir
   - 更新 status.json
6. 输出汇总结果
```

### 单视频详细流程

对每个待处理视频：

1. 计算视频唯一键

建议使用输入文件名作为主键，必要时补充文件大小和修改时间，避免同名误判。

1. 判断是否已成功

如果状态文件中该视频状态为 `success`，并且输出目录中对应成品文件存在，则跳过。

1. 准备 batch 输入桥接

因为现有 `process_video()` 对本地文件的读取路径写死为 `batch/input/<file>`，所以最简复用方式是：

- 把当前视频复制到 `batch/input/`
- 调用 `process_video(文件名, dubbing=True, is_retry=False)`

这是一个“目录桥接”动作，不修改核心业务代码。

1. 调用现有单视频管线

`process_video()` 成功后，现有逻辑会把结果归档到既定目录。

1. 提取最终成品

从归档目录找到：

- `batch/output/<video_stem>/output_dub.mp4`

将其复制到用户指定输出目录，例如：

- `<output_dir>/<original_stem>_dub.mp4`

1. 记录状态

成功则写入 `success`；失败则写入失败步骤与错误信息。

## 状态文件设计

### 为什么不用 Excel

CLI 场景下，Excel 是不必要的外部依赖，且不适合自动化调用。更适合的是 JSON。

### 推荐文件

放在输出目录下：

```text
<output_dir>/batch_translate_status.json
```

### 推荐结构

```json
{
  "version": 1,
  "jobs": {
    "video1.mp4": {
      "fingerprint": {
        "size": 123456789,
        "mtime": 1711111111
      },
      "status": "success",
      "output_file": "video1_dub.mp4",
      "updated_at": "2026-03-22T12:00:00"
    },
    "video2.mp4": {
      "fingerprint": {
        "size": 987654321,
        "mtime": 1711112222
      },
      "status": "failed",
      "error_step": "🗣️ Generating audio",
      "error_message": "tts api timeout",
      "updated_at": "2026-03-22T12:15:00"
    }
  }
}
```

这里建议新增 `fingerprint`，至少记录：

- 文件大小
- 最后修改时间

这样比只用文件名更稳妥。因为实际使用中，用户可能会：

- 用新视频覆盖旧文件
- 保留原文件名但替换内容

如果只看文件名，CLI 会误判为“已经成功处理过”。

### 跳过规则

下次执行时，只跳过同时满足以下条件的视频：

1. 状态文件中标记为 `success`
2. 对应输出文件仍然存在
3. 当前输入文件的指纹与状态文件中记录的指纹一致

只依赖其中一个条件不够稳妥。这样设计可以避免状态文件和真实文件不一致。

### 状态文件写入策略

这是稳定性上必须补的一点：

- 不要直接覆盖写 JSON
- 应该先写入临时文件，再原子替换

推荐流程：

```text
status.json.tmp -> fsync -> rename(status.json)
```

这样可以避免处理中途崩溃时把状态文件写坏。

## 输出文件设计

### 建议输出

输出目录中至少包含：

```text
output_dir/
  video1_dub.mp4
  video2_dub.mp4
  batch_translate_status.json
  batch_translate_report.json
```

建议额外生成一份批次报告文件：

```text
batch_translate_report.json
```

它记录本次运行的汇总结果，例如：

- 扫描到多少文件
- 跳过多少
- 成功多少
- 失败多少
- 每个失败任务的失败步骤

这份报告的收益很高：

- 用户运行结束后一眼就能看结果
- 便于脚本或调度器消费
- 不会和长期状态文件混在一起

### 可选增强

如果调用方后续还需要字幕，可以顺手再复制：

- `output_sub.mp4`
- `.srt` 文件

但从当前需求看，**必须产出的是最终配音视频**，其他文件可以作为后续增强，不必进入第一版设计。

## 异常与恢复策略

### 串行执行

建议第一版只支持串行执行，不做并发。原因：

1. 现有核心流程强依赖全局 `output/` 工作目录。
2. 现有 `cleanup()` 也是基于全局目录搬运结果。
3. 并发会引入目录互相覆盖风险。

除此之外，还建议增加一个**运行锁文件**机制：

- 例如在工作目录下创建 `.batch_translate.lock`
- 如果检测到已有未释放锁，则拒绝启动新任务

这个功能的收益非常高，因为它可以防止：

- 用户重复启动两个 CLI 实例
- CLI 与旧的 batch 模式同时运行
- 两个进程争用全局 `output/` 目录

相比并发，这个锁机制更值得优先实现。

### 单视频失败不影响整体批次

每个视频独立捕获异常：

- 当前视频失败后写入状态文件
- 继续处理下一个视频

### 断点续跑

依赖状态文件实现：

- 成功过的自动跳过
- 失败过的自动重试

### 临时文件清理

每个视频处理完成后，删除放入 `batch/input` 的桥接副本，避免下次扫描混淆。

同时建议把 CLI 自己的运行痕迹收敛到专属目录，例如：

```text
.videolingo_cli/
  logs/
  tmp/
  locks/
```

原因：

- 比把所有辅助文件散落在仓库根目录更可控
- 便于后续扩展日志、报告、锁文件和临时文件

## 多目录场景建议

这是当前文档里最值得补强的一点。

### 什么时候应该引入配置文件

如果只是一组：

- 输入目录
- 输出目录

那两个位置参数已经足够，不需要配置文件。

但如果变成下面这些场景，就建议切换到任务文件模式：

1. 多个输入目录分别输出到不同目录
2. 某些目录需要递归扫描，某些不需要
3. 某些目录只处理部分文件模式
4. 某些任务需要关闭配音，某些任务需要开启配音
5. 某些任务需要覆盖默认语言配置

### 推荐任务文件结构

建议使用 YAML，表达性更好：

```yaml
version: 1
jobs:
  - input_dir: /data/course_a
    output_dir: /result/course_a
    recursive: true
    dubbing: true
  - input_dir: /data/course_b
    output_dir: /result/course_b
    recursive: false
    dubbing: true
    include:
      - "*.mp4"
      - "*.mkv"
```

### 为什么任务文件比“多个输入参数”更好

因为多目录场景的本质不是“更多参数”，而是“多组任务定义”。

任务文件可以自然表达：

- 一组输入对应一组输出
- 每组任务有自己的过滤规则
- 将来增加少量任务级覆盖项时不会破坏 CLI 主入口

这是扩展性上收益最大的设计补充。

## 易用性改进建议

除了核心流程，CLI 的易用性还可以再补三点。

### 1. 启动前预检查摘要

在正式执行前，打印一段清晰摘要：

```text
Input Dir: ...
Output Dir: ...
Recursive: true
Detected Videos: 37
Will Run: 12
Will Skip: 25
```

这个收益很高，因为用户能在开跑前立刻发现配置是否符合预期。

### 2. 结束后汇总摘要

运行结束后打印：

```text
Processed: 12
Succeeded: 10
Failed: 2
Skipped: 25
Report: .../batch_translate_report.json
```

这个比只打印“完成了”更有用。

### 3. 明确退出码

建议 CLI 约定退出码：

- `0`：全部成功，或全部已跳过
- `1`：存在任务失败
- `2`：启动前配置错误或环境错误

这对脚本调用、cron、任务编排器非常重要，收益很高。

## 稳定性改进建议

当前文档里还有几个值得补上的稳定性点。

### 1. 成品文件原子落盘

最终复制 `output_dub.mp4` 到输出目录时，建议不要直接写目标文件，而是：

1. 先复制到临时文件
2. 校验文件存在且大小大于 0
3. 再原子重命名为正式文件

这样可以避免输出目录留下半截文件。

### 2. 成功判定再收紧一点

建议最终成功条件至少满足：

1. `process_video()` 返回成功
2. 归档目录存在 `output_dub.mp4`
3. 目标输出目录中的最终文件写入成功

如果只满足前两条，仍然可能在最后复制阶段失败。

### 3. 每任务单独日志

建议除了总报告，还为每个视频写一个轻量日志文件，例如：

```text
.videolingo_cli/logs/<video_stem>.log
```

这样排查失败时，不必只依赖控制台输出。

## 为什么这是“优雅且简洁”的方案

这个方案的关键优点在于，它没有碰核心处理逻辑，只新增了一个很薄的适配层。

### 优雅的地方

1. **不重写业务流程**

翻译、字幕、配音全部继续使用现有实现。

1. **不改动 Streamlit 流程**

Web UI 仍保持原样，新 CLI 与现有 UI 并行存在。

1. **不破坏 batch 模式**

Excel 驱动批处理继续存在，目录驱动批处理新增为另一种入口。

1. **失败恢复清晰**

状态文件天然适合断点续跑。

### 简洁的地方

第一版其实只需要增加一个入口文件和少量辅助函数：

- 扫描输入目录
- 状态文件读写
- 调用 `process_video()`
- 复制最终成品

这比直接改造整个 `batch_processor.py` 要干净很多。

## 补充后的推荐设计结论

在保留原文档主思路不变的前提下，最值得补充的高收益能力有 6 个：

1. **双模式入口**：默认双参数，复杂场景走 `--job-file`
2. **少量高价值参数**：`--recursive`、`--dry-run`、`--force`、`--job-file`
3. **更稳的状态模型**：加入文件指纹与原子写入
4. **单实例锁**：防止多个进程争用全局工作目录
5. **批次报告与退出码**：提升自动化集成能力
6. **多目录场景用任务文件表达**：不要用大量参数硬撑

这些改动都属于：

- 实现成本相对可控
- 对易用性、稳定性、扩展性提升明显
- 不会破坏“复用现有 VideoLingo 核心链路”的主设计

## V1 最终推荐规范

为了让后续开发更容易落地，建议把第一版实现范围明确收敛为下面这组规范。

### V1 必做能力

第一版建议只实现这些能力：

1. 双参数主入口

```bash
python -m cli.batch_translate <input_dir> <output_dir>
```

1. 串行处理所有待执行视频

1. 默认开启断点续跑

1. 默认只输出最终配音视频

1. 使用 JSON 状态文件记录处理结果

1. 支持 `--recursive`

1. 支持 `--dry-run`

1. 支持 `--force`

1. 支持单实例锁

1. 输出批次报告文件

1. 提供明确退出码

这是一个比较稳的 V1 范围，因为它已经覆盖了：

- 日常直接使用
- 批量重跑
- 自动化脚本接入
- 故障恢复
- 多数常见目录结构

### V1 不做的能力

第一版明确不做下面这些内容：

1. 并发处理

1. 任务级 TTS/语言模型覆盖参数

1. 复杂输出命名模板

1. Web UI 管理这个新 CLI

1. 远程任务调度或服务化 API

### V1.5 再做的能力

如果 V1 运行稳定，再继续加这些扩展：

1. `--job-file` 任务文件模式

1. 多输入目录、多输出目录

1. 任务级 include/exclude 规则

1. 可选输出字幕文件与字幕视频

1. 更细粒度的任务级配置覆盖

这样分阶段实现的好处是：

- 先把单目录工作流做稳定
- 再处理复杂场景
- 避免一开始就把 CLI 设计做重

## 推荐命令规范

### 最小命令

```bash
python -m cli.batch_translate ./input ./output
```

### 递归扫描

```bash
python -m cli.batch_translate ./input ./output --recursive
```

### 只预检查不执行

```bash
python -m cli.batch_translate ./input ./output --dry-run
```

### 强制重跑

```bash
python -m cli.batch_translate ./input ./output --force
```

### 未来任务文件模式

```bash
python -m cli.batch_translate --job-file jobs.yaml
```

## 推荐状态模型

建议把状态值收敛为有限集合，而不是自由字符串。

### 推荐状态枚举

- `pending`
- `running`
- `success`
- `failed`
- `skipped`

### 为什么比仅写字符串更好

这比只写：

- `Done`
- `Error: ...`

更适合后续扩展，因为它把“状态”和“错误信息”拆开了。

推荐结构如下：

```json
{
  "version": 1,
  "jobs": {
    "lesson01.mp4": {
      "status": "failed",
      "fingerprint": {
        "size": 123456,
        "mtime": 1711111111
      },
      "error_step": "generate_audio",
      "error_message": "tts api timeout",
      "output_file": null,
      "updated_at": "2026-03-22T12:15:00"
    }
  }
}
```

### 推荐步骤标识

为避免后续程序处理困难，建议 `error_step` 不直接写带 emoji 的展示文本，而写稳定的内部标识，例如：

- `process_input`
- `transcribe`
- `split_sentences`
- `translate`
- `align_subtitles`
- `merge_subtitles`
- `generate_audio_tasks`
- `extract_reference_audio`
- `generate_audio`
- `merge_audio`
- `merge_dub_video`

面向用户展示时，再映射成人类可读文本。

这个改动收益很高，因为它能明显提升：

- 状态文件可读性
- 自动化统计能力
- 失败原因聚合能力

## 推荐目录约定

为了降低和现有系统的耦合混乱，建议新 CLI 统一使用一组自己的运行目录：

```text
.videolingo_cli/
  locks/
  logs/
  tmp/
```

其中：

- `locks/`：运行锁
- `logs/`：单任务日志
- `tmp/`：桥接输入文件与临时状态文件

这样做的收益很明确：

- 与仓库自带的 `batch/`、`output/`、`history/` 目录边界更清楚
- 后续排障时更容易定位 CLI 自己产生的文件

## 推荐成功判定规则

建议把“成功”定义收紧为以下 4 个条件同时成立：

1. `process_video()` 返回成功

1. 归档目录中存在 `output_dub.mp4`

1. 拷贝到目标输出目录成功

1. 目标文件大小大于 0

这样比单纯信任 `process_video()` 的返回值更稳。

## 推荐批次报告字段

建议 `batch_translate_report.json` 至少包含这些字段：

```json
{
  "started_at": "2026-03-22T12:00:00",
  "finished_at": "2026-03-22T13:30:00",
  "input_dir": "/data/input",
  "output_dir": "/data/output",
  "recursive": true,
  "total_detected": 37,
  "planned": 12,
  "skipped": 25,
  "succeeded": 10,
  "failed": 2,
  "failed_jobs": [
    {
      "file": "lesson11.mp4",
      "step": "generate_audio",
      "message": "tts api timeout"
    }
  ]
}
```

这个报告足够覆盖：

- 运行回顾
- 调度器消费
- 快速问题定位

## 最终落地建议

如果现在就进入开发阶段，我建议按下面顺序落地：

1. 实现 V1 CLI 主入口与参数解析

1. 打通目录扫描、状态文件、桥接输入、单视频处理、结果复制

1. 补单实例锁与原子写状态文件

1. 补 `--dry-run` 与批次报告

1. 最后再考虑 `--job-file`

这个顺序的好处是：

- 每一步都能单独验证
- 不会一开始就把范围扩得太大
- 很快就能得到一个可用版本

## 开发拆解建议

为了让后续实现更顺畅，建议按“薄入口 + 小工具模块”的方式拆分，而不是把所有逻辑都堆进一个文件。

### 推荐文件划分

建议新增如下结构：

```text
cli/
  __init__.py
  batch_translate.py
  batch_translate_lib/
    __init__.py
    args.py
    scanner.py
    state_store.py
    runner.py
    reporter.py
    lockfile.py
    paths.py
```

如果不想新增子包，也可以先放在一个文件里，但从可维护性看，上面的拆法更稳。

### 各模块职责建议

#### 1. `cli/batch_translate.py`

职责：

- 作为唯一对外入口
- 调用参数解析
- 组织整体执行流程
- 返回进程退出码

这个文件应该尽量薄，不承载业务细节。

#### 2. `args.py`

职责：

- 定义 CLI 参数
- 校验参数组合是否合法
- 规范化输入输出路径

建议把以下规则放在这里：

- 简单模式必须同时提供 `input_dir` 和 `output_dir`
- `--job-file` 模式下不能再混用位置参数
- `--force`、`--recursive`、`--dry-run` 都归一到统一配置对象

#### 3. `scanner.py`

职责：

- 扫描输入目录中的视频文件
- 按扩展名过滤
- 生成每个视频的文件指纹
- 按状态文件判断哪些需要执行、哪些应该跳过

建议输出统一的任务对象，而不是散落的路径字符串。

#### 4. `state_store.py`

职责：

- 读取 `batch_translate_status.json`
- 维护状态结构版本
- 原子写回状态文件
- 提供 `mark_running`、`mark_success`、`mark_failed`、`mark_skipped` 等方法

这是后续稳定性的核心模块，值得单独拆出来。

#### 5. `runner.py`

职责：

- 处理单个视频任务
- 复制桥接输入到 `batch/input`
- 调用 `process_video()`
- 查找归档目录中的 `output_dub.mp4`
- 原子复制最终成品到输出目录

这是新 CLI 和现有 VideoLingo 处理链路的主要连接点。

#### 6. `reporter.py`

职责：

- 生成本次运行的汇总信息
- 写出 `batch_translate_report.json`
- 输出启动摘要和结束摘要

#### 7. `lockfile.py`

职责：

- 创建和释放运行锁
- 防止多个 CLI 实例并发执行

#### 8. `paths.py`

职责：

- 统一管理 `.videolingo_cli`、锁文件、日志目录、临时目录等路径
- 减少硬编码路径散落在各个文件中

## 推荐实现顺序

从工程落地角度，建议用 5 个小阶段实现，而不是一次写完。

### 阶段 1：打通最小可运行链路

目标：

- 能接受 `input_dir output_dir`
- 能扫描视频
- 能逐个调用 `process_video()`
- 能复制 `output_dub.mp4` 到输出目录

这一步先不追求完整，只追求“单条主链路打通”。

### 阶段 2：补状态文件

目标：

- 支持跳过已成功任务
- 支持失败任务重新运行
- 支持文件指纹判断

### 阶段 3：补运行锁和原子写

目标：

- 防止双开
- 防止状态文件写坏
- 防止输出目录留下损坏的成品文件

### 阶段 4：补 `--dry-run` 和汇总报告

目标：

- 在真正执行前看到任务计划
- 在执行后得到结构化报告

### 阶段 5：补 `--recursive`

目标：

- 支持更真实的目录结构

这个阶段顺序的关键原因是：

- 每一步都能单独验证
- 每一步都能显著提升可用性
- 不会因为一次性做太多而难以定位问题

## 开发任务清单

下面这份清单可以直接作为实现 TODO。

### P0：必须完成

1. 新增 CLI 入口文件

1. 实现位置参数 `input_dir output_dir`

1. 扫描输入目录中的允许视频格式

1. 为每个视频生成任务对象和文件指纹

1. 调用 `process_video(video_name, dubbing=True, is_retry=False)`

1. 从归档目录提取 `output_dub.mp4`

1. 把最终成品复制到输出目录

1. 写入 JSON 状态文件

1. 输出成功、失败、跳过摘要

1. 返回正确退出码

### P1：强烈建议完成

1. 单实例锁

1. 状态文件原子写入

1. 输出文件原子落盘

1. `--dry-run`

1. `--recursive`

1. `--force`

1. 批次报告文件

### P2：后续扩展

1. `--job-file`

1. 多目录批任务

1. include/exclude 规则

1. 可选拷贝字幕文件

1. 每任务独立日志增强

## 验收标准

如果要判断这个 V1 CLI 是否达到可用标准，建议至少满足下面这些验收项。

### 功能验收

1. 给定一个输入目录和输出目录，CLI 能成功处理至少 1 个本地视频

1. 成功后输出目录中存在对应的 `_dub.mp4` 成品文件

1. 状态文件中写入 `success`

1. 第二次运行时，已成功文件会被自动跳过

1. 使用 `--force` 时，已成功文件会重新执行

1. 使用 `--dry-run` 时，不产生实际视频输出，只打印任务计划

### 稳定性验收

1. 处理中途异常退出后，状态文件仍然是合法 JSON

1. 两个 CLI 实例同时启动时，第二个实例会被明确拒绝

1. 目标输出文件不会出现 0 字节成品被误判为成功

1. 单个视频失败不会阻塞后续视频处理

### 易用性验收

1. 启动时打印输入目录、输出目录、待执行数、跳过数

1. 结束时打印成功数、失败数、跳过数和报告路径

1. 失败时错误信息至少包含视频文件名、失败步骤和错误消息

## 测试建议

第一版不一定要做非常完整的自动化测试，但至少建议补这些高价值测试。

### 单元测试建议

优先测试不依赖真实视频处理的纯逻辑模块：

- 状态文件读写
- 文件指纹比较
- 跳过规则判断
- 参数解析
- 路径规范化
- 报告生成

### 集成测试建议

至少覆盖下面几类场景：

1. 单文件成功

1. 单文件失败

1. 多文件混合：部分成功、部分失败

1. 二次运行自动跳过已成功任务

1. `--force` 强制重跑

1. `--dry-run` 不执行真实处理

### 人工验证建议

由于真实视频处理链路依赖较多外部能力，建议保留一组人工验证清单：

1. 准备 2 到 3 个小视频样本

1. 手工跑一次最小命令

1. 检查输出目录、状态文件、报告文件是否一致

1. 故意制造一个失败任务，确认不会影响后续任务

1. 再次运行，确认断点续跑有效

## 风险与应对

后续实现最可能踩的坑，主要有下面几个。

### 1. 归档目录定位不稳定

风险：

- `cleanup()` 基于视频名归档，若文件名处理不一致，可能找不到归档目录

应对：

- CLI 层尽量保持原始文件名不变
- 提取成品时按稳定规则计算目标归档目录

### 2. 全局工作目录污染

风险：

- 当前底层流程依赖 `output/` 和 `batch/input/`
- 多实例或残留文件容易互相影响

应对：

- 强制单实例锁
- 每任务完成后删除桥接输入文件
- CLI 自己的辅助文件全部收敛到 `.videolingo_cli/`

### 3. 状态与真实文件不一致

风险：

- 状态写成功了，但最终成品复制失败

应对：

- 成功判定必须包含“最终成品已写入输出目录且大小大于 0”

### 4. 参数扩张失控

风险：

- 很容易不断加入业务参数，导致 CLI 和 `config.yaml` 双源冲突

应对：

- 坚持 V1 只保留少量高收益参数
- 更复杂的场景后续统一收敛到 `--job-file`

## 建议实现草图

下面是建议的伪代码结构：

```python
def main(input_dir: str, output_dir: str) -> int:
    ensure_dirs(input_dir, output_dir, "batch/input")
    status_store = StatusStore(output_dir / "batch_translate_status.json")
    videos = list_input_videos(input_dir)

    for video_path in videos:
        video_name = video_path.name

        if status_store.is_success(video_name):
            continue

        bridge_path = copy_to_batch_input(video_path)

        try:
            ok, error_step, error_message = process_video(video_name, dubbing=True, is_retry=False)

            if not ok:
                status_store.mark_failed(video_name, error_step, error_message)
                continue

            archived_dir = locate_archived_output(video_name)
            dub_file = archived_dir / "output_dub.mp4"
            final_file = copy_final_output(dub_file, output_dir, video_name)
            status_store.mark_success(video_name, final_file.name)

        except Exception as exc:
            status_store.mark_failed(video_name, "unhandled", str(exc))
        finally:
            remove_bridge_file(bridge_path)

    return 0
```

## 实现注意点

### 1. 文件名映射

由于 `cleanup()` 会按视频名归档，建议新 CLI 对输入文件名保持原样，不在处理前重命名。

### 2. 输出文件命名

建议统一输出为：

```text
<原文件名去扩展名>_dub.mp4
```

例如：

- `lesson01.mp4` -> `lesson01_dub.mp4`

### 3. 配置来源

第一版不新增额外 CLI 参数控制语言、TTS、模型。

全部沿用当前 `config.yaml`。这与“只接受两个参数”的需求是一致的，也能避免把 CLI 做复杂。

### 4. 成功判定

建议以“`process_video()` 返回成功，且归档目录下存在 `output_dub.mp4`”作为最终成功条件。

不要只依赖函数返回值。

### 5. 平台兼容

这个方案本质上是 Python CLI，不依赖 `OneKeyBatch.bat`，因此比现有批处理入口更适合 macOS 和 Linux。

## 不建议的方案

### 方案一：继续扩展 Excel 批处理

不建议。因为这样会把“目录驱动批处理”和“表驱动批处理”强行揉在一起，职责会越来越乱。

### 方案二：直接重写一套新的翻译/配音流程

不建议。这样会绕开现有稳定链路，重复代码太多，后期维护成本高。

### 方案三：并发处理多个视频

第一版不建议。当前实现明显依赖全局工作目录，先把串行版本做稳定更合理。

## 最终建议

最合适的落地方式是：

1. 保留现有 Streamlit 模式。
2. 保留现有 Excel 批处理模式。
3. 新增一个“目录驱动、双参数”的轻量 CLI。
4. CLI 内部直接复用 `batch.utils.video_processor.process_video()`。
5. 用 JSON 状态文件替代 Excel 状态列。

这样可以在**最小改动**下满足你的目标，而且不会破坏现有系统结构。

## 推荐后续实现顺序

如果下一步要真正编码，建议按这个顺序做：

1. 新增 `tools/batch_translate.py` 或 `cli/batch_translate.py`
2. 先打通“扫描目录 -> 逐个调用 `process_video()` -> 复制 `output_dub.mp4`”
3. 再补状态文件 `batch_translate_status.json`
4. 最后补更好的日志输出和失败重试策略

这样风险最低，也最容易验证。
