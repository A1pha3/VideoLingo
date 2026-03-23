# batch_translate CLI 使用说明

## 文档定位

这份文档面向实际使用 `batch_translate` CLI 的项目维护者与批处理操作人员。

它回答四个问题：

1. 这个命令怎么运行。
2. 运行前需要准备什么。
3. 运行后会生成什么文件。
4. 出错时应该先看哪里。

配套文档：

- 方案设计：[docs/cn/product/batch_transalte.md](docs/cn/product/batch_transalte.md)
- 现有批处理入口分析：[docs/cn/product/batch_processor_detail.md](docs/cn/product/batch_processor_detail.md)
- 开发清单：[docs/cn/product/batch_translate_dev_todo.md](docs/cn/product/batch_translate_dev_todo.md)
- 进度跟踪：[docs/cn/product/batch_translate_progress.md](docs/cn/product/batch_translate_progress.md)

## 一句话说明

`batch_translate` 是一个目录驱动的批量翻译与配音命令行工具。

它会：

1. 扫描输入目录中的视频文件。
2. 串行调用 VideoLingo 现有单视频处理链路。
3. 将最终配音视频写入输出目录。
4. 记录状态文件与报告文件。
5. 在下次运行时自动跳过已成功任务。

## 标准运行方式

### 1. 激活项目环境

项目标准激活方式：

```bash
cd /Volumes/mini_matrix/github/a1pha3/video/VideoLingo
source scripts/activate_project_conda_env.zsh
```

不要用其他临时方式替代这个命令，否则容易出现依赖、模型路径或环境变量不一致。

### 2. 运行最基本命令

```bash
python -m cli.batch_translate <input_dir> <output_dir>
```

示例：

```bash
python -m cli.batch_translate ./videos/input ./videos/output
```

含义：

- `input_dir`：待处理视频目录。
- `output_dir`：成品目录，同时会放状态文件和报告文件。

## 常用参数

### `--recursive`

递归扫描子目录中的视频文件。

```bash
python -m cli.batch_translate ./videos/input ./videos/output --recursive
```

### `--dry-run`

只扫描并输出本次执行计划，不真正处理视频。

```bash
python -m cli.batch_translate ./videos/input ./videos/output --dry-run
```

当前行为：

- 会生成 `batch_translate_report.json`
- 不会生成 `batch_translate_status.json`

### `--force`

强制重跑已经成功的视频。

```bash
python -m cli.batch_translate ./videos/input ./videos/output --force
```

适合以下场景：

- 修改了 `config.yaml` 中的目标语言
- 更换了 TTS 配置
- 想重新生成配音结果

真实验证结果已经确认：`--force` 会重新执行，不会继续跳过成功任务。

## 运行前检查清单

正式启动前，建议按下面顺序检查：

1. 输入目录存在且是目录。
2. 输出目录不是输入目录本身。
3. 输出目录不在输入目录内部。
4. `config.yaml` 已配置好本次需要的模型和配音参数。
5. 翻译 API Key 已配置。
6. 如果 Whisper 或 TTS 选用云端模式，对应 API Key 已配置。

当前 CLI 已经内置运行前预检。缺少关键配置时，会在入口直接报错，而不是跑到中途再失败。

## 支持的输入文件

默认使用项目配置中的 `allowed_video_formats`。

当前配置常见格式包括：

- `mp4`
- `mov`
- `avi`
- `mkv`
- `flv`
- `wmv`
- `webm`

## 输出目录结构

执行完成后，输出目录通常包含：

```text
output_dir/
  demo_dub.mp4
  batch_translate_status.json
  batch_translate_report.json
```

说明：

- `*_dub.mp4`：最终配音视频。
- `batch_translate_status.json`：任务级状态文件。
- `batch_translate_report.json`：本次运行汇总报告。

## 状态文件说明

状态文件路径：

```text
<output_dir>/batch_translate_status.json
```

当前状态字段示例：

```json
{
  "version": 1,
  "jobs": {
    "demo.mp4": {
      "status": "success",
      "fingerprint": {
        "size": 1385961,
        "mtime": 1774197993
      },
      "error_step": null,
      "error_message": null,
      "output_file": "demo_dub.mp4",
      "updated_at": "2026-03-22T18:00:51+00:00"
    }
  }
}
```

关键字段：

- `status`：`running`、`success`、`failed`
- `fingerprint`：用于判断输入文件是否发生变化
- `error_step`：失败时记录归一化步骤名
- `error_message`：失败时记录异常信息
- `output_file`：成功时记录输出文件名

## 报告文件说明

报告文件路径：

```text
<output_dir>/batch_translate_report.json
```

典型字段：

- `total_detected`：检测到的视频总数
- `planned`：本次计划执行的任务数
- `skipped`：本次跳过的任务数
- `succeeded`：本次成功数
- `failed`：本次失败数
- `failed_jobs`：失败任务详情

## 退出码说明

当前 CLI 的退出码约定：

- `0`：全部成功，或本次全部被跳过，或 dry-run 正常结束
- `1`：存在处理失败的视频
- `2`：运行时配置错误、锁冲突，或没有检测到可处理视频

## 已验证的真实行为

当前已经完成的真实验证包括：

1. 成功样本可完整跑通并输出配音视频。
2. 成功样本二次运行会被自动跳过。
3. 失败样本会返回退出码 `1`，并写入失败状态与失败报告。
4. 失败样本二次运行不会被跳过。
5. `--force` 会强制重跑成功样本。

## 典型使用场景

### 场景 1：首次跑一批视频

```bash
python -m cli.batch_translate ./input_videos ./output_videos
```

### 场景 2：先确认计划再执行

```bash
python -m cli.batch_translate ./input_videos ./output_videos --dry-run
```

### 场景 3：继续上次未完成的批次

```bash
python -m cli.batch_translate ./input_videos ./output_videos
```

### 场景 4：修改配置后强制重跑

```bash
python -m cli.batch_translate ./input_videos ./output_videos --force
```

## 失败时先看哪里

建议按下面顺序排查：

1. 终端输出中的失败步骤和错误信息。
2. `batch_translate_report.json` 中的 `failed_jobs`。
3. `batch_translate_status.json` 中对应任务的 `error_step` 和 `error_message`。
4. 现有归档目录中的失败产物。

失败任务通常会被归档到类似下面的位置：

```text
batch/output/ERROR/<video_name>/
```

## 常见问题

### 1. 为什么运行了命令却没有开始处理？

优先检查：

- 输入目录里是否真的有允许格式的视频
- 是否全部都已经成功并被自动跳过
- 是否执行了 `--dry-run`

### 2. 为什么返回码是 `2`？

最常见原因：

- 输入目录为空
- 运行前预检失败
- 已有另一个 `batch_translate` 实例在运行

### 3. 现在还会出现 Streamlit warning 吗？

当前 CLI 执行路径已经清理掉这类 warning。

如果你仍然看到异常终端输出，更可能是 VS Code 集成终端自己的 prompt hook 噪声，而不是 `batch_translate` 的功能错误。

### 4. 为什么失败视频下次还会继续跑？

这是当前设计的预期行为。

原因：

- 只有 `success` 状态才会被自动跳过
- `failed` 状态默认允许下次继续重试

## 推荐操作习惯

1. 首次处理大批量任务前，先跑一次 `--dry-run`
2. 每次批量处理都使用独立输出目录，避免不同批次混在一起
3. 修改 `config.yaml` 后，如果希望刷新已有成功结果，使用 `--force`
4. 出现失败时，优先看报告文件与状态文件，而不是只看终端最后一行

## 当前限制

当前版本仍有这些边界：

1. 只支持串行处理，不支持并发
2. 依赖现有全局工作目录模型
3. 失败产物仍沿用现有 `batch/output/ERROR` 归档逻辑
4. 当前文档主要覆盖目录驱动 CLI，不覆盖多任务文件模式

## 建议的最小操作流程

如果你是第一次使用，建议直接按下面流程：

```bash
cd /Volumes/mini_matrix/github/a1pha3/video/VideoLingo
source scripts/activate_project_conda_env.zsh
python -m cli.batch_translate ./input_videos ./output_videos --dry-run
python -m cli.batch_translate ./input_videos ./output_videos
```

如果修改了配置并想重跑：

```bash
python -m cli.batch_translate ./input_videos ./output_videos --force
```
