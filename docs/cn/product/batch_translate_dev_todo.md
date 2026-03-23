# batch_translate CLI 开发任务清单

## 文档定位

这是一份面向开发落地的精简清单。

配套文档：

- 详细方案：`docs/cn/product/batch_transalte.md`
- 现有批处理入口分析：`docs/cn/product/batch_processor_detail.md`
- 进度跟踪：`docs/cn/product/batch_translate_progress.md`
- 使用说明：`docs/cn/product/batch_translate_user_guide.md`

如果要开始编码，优先看这份清单；如果要理解设计背景，再回看详细方案。

## 当前状态

当前状态：**CLI V1 编码已完成，主入口、dry-run、运行前预检和 18 项 unittest 已验证，真实成功/失败/跳过/force 重跑行为均已通过。**

当前建议入口顺序：

1. 先完成“阶段 1：主链路打通”的最小真实验证
2. 再看 `batch_translate_progress.md` 中的当前阶段与风险
3. 然后按“阶段 2 -> 阶段 3 -> 阶段 4”继续推进

当前已完成的实现质量项：

1. `setup.py` 已修正为可发现新增 `cli` 包
2. 已新增 3 个 CLI unittest 文件
3. 当前 unittest 共 18 项，执行结果为 `OK`
4. 已新增运行前配置预检，缺少关键配置时会在入口直接报错
5. 锁文件已支持陈旧锁恢复，避免异常中断后被永久阻塞

## V1 目标

交付一个新的目录驱动命令行工具：

```bash
python -m cli.batch_translate <input_dir> <output_dir>
```

该工具需要满足：

1. 扫描输入目录中的视频文件
2. 跳过已成功处理的视频
3. 串行调用现有 VideoLingo 单视频处理链路
4. 复制最终 `output_dub.mp4` 到目标输出目录
5. 记录状态、生成报告、支持断点续跑

## V1 范围

### 必做

1. 双参数入口
2. 串行处理
3. JSON 状态文件
4. 文件指纹判断
5. 单实例锁
6. 批次报告
7. `--recursive`
8. `--dry-run`
9. `--force`
10. 明确退出码

### 不做

1. 并发处理
2. 多目录任务文件模式
3. 任务级语言/TTS 覆盖
4. 复杂输出命名模板
5. Web UI 集成

## 推荐目录结构

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

## 模块任务

### 1. `cli/batch_translate.py`

任务：

1. 作为主入口
2. 调用参数解析
3. 初始化路径、锁、状态、报告
4. 串行执行任务
5. 汇总退出码

完成标准：

1. 可以直接运行 `python -m cli.batch_translate`
2. 主流程不包含过多实现细节

### 2. `args.py`

任务：

1. 定义位置参数 `input_dir output_dir`
2. 定义可选参数 `--recursive --dry-run --force`
3. 校验参数合法性
4. 输出统一配置对象

完成标准：

1. 缺失参数时给出明确错误信息
2. 参数解析结果稳定可测试

### 3. `scanner.py`

任务：

1. 扫描输入目录
2. 过滤允许视频格式
3. 支持递归扫描
4. 生成文件指纹
5. 根据状态文件判断 `planned/skipped`

完成标准：

1. 能输出统一任务对象列表
2. 同名文件替换后可通过指纹识别变更

### 4. `state_store.py`

任务：

1. 读取状态文件
2. 初始化空状态
3. 提供 `mark_running / mark_success / mark_failed / mark_skipped`
4. 原子写回 JSON
5. 管理状态结构版本

完成标准：

1. 中途崩溃后状态文件仍为合法 JSON
2. 状态字段结构固定可预期

### 5. `runner.py`

任务：

1. 复制桥接输入文件到 `batch/input`
2. 调用 `process_video(video_name, dubbing=True, is_retry=False)`
3. 定位归档目录
4. 查找 `output_dub.mp4`
5. 原子复制成品到输出目录
6. 清理桥接文件

完成标准：

1. 单个视频任务可以独立执行
2. 失败不会污染后续任务

### 6. `reporter.py`

任务：

1. 生成启动前摘要
2. 生成结束后摘要
3. 写出 `batch_translate_report.json`

完成标准：

1. 用户能看清本次运行的总数、成功数、失败数、跳过数
2. 报告文件可被脚本读取

### 7. `lockfile.py`

任务：

1. 创建运行锁
2. 检测重复运行
3. 释放锁
4. 异常退出时尽量保证锁可恢复

完成标准：

1. 两个实例同时运行时，第二个实例会被拒绝

### 8. `paths.py`

任务：

1. 管理 `.videolingo_cli/locks`
2. 管理 `.videolingo_cli/logs`
3. 管理 `.videolingo_cli/tmp`
4. 管理状态文件和报告文件路径

完成标准：

1. 路径不在其他模块中散落硬编码

## 实现阶段

### 阶段 1：主链路打通

交付物：

1. CLI 主入口
2. 目录扫描
3. 调用 `process_video()`
4. 复制成品到输出目录

验收：

1. 至少 1 个本地视频能跑通

当前状态：

1. 主入口、扫描、任务执行桥接代码已完成
2. `runner.py` 的成功路径与失败路径已由 unittest 覆盖
3. 真实样本已完成闭环，确认最终成品、状态文件、报告文件和锁释放均正常
4. 同一输入目录的二次运行已验证会跳过成功任务
5. 失败样本已验证退出码为 `1`，并确认失败任务会在后续运行中继续执行
6. `--force` 已在真实成功样本上验证，会强制重跑并再次成功落盘

### 阶段 2：状态与跳过

交付物：

1. 状态文件
2. 文件指纹
3. 自动跳过已成功任务
4. `--force`

当前验证：

1. 已使用仓库内 `demo.mp4` 跑通真实单视频处理
1. 已确认输出目录生成 `demo_dub.mp4`
1. 已确认状态文件记录 `success`
1. 已确认二次运行会跳过已成功任务
1. 已使用空 `bad.mp4` 验证真实失败路径，状态记录为 `failed`
1. 已确认失败任务不会被误跳过
1. 已确认 `--force` 会重跑成功任务而不是跳过

验收：

1. 二次运行会跳过成功任务
2. `--force` 会重新执行

### 阶段 3：稳定性

交付物：

1. 运行锁
2. 状态原子写入
3. 成品原子落盘

验收：

1. 双开时第二个实例被拒绝
2. 异常退出后状态文件不损坏

### 阶段 4：可用性

交付物：

1. `--dry-run`
2. 启动前摘要
3. 结束后摘要
4. `batch_translate_report.json`

验收：

1. 运行计划和结果汇总清晰可读

### 阶段 5：递归扫描

交付物：

1. `--recursive`

验收：

1. 子目录视频可被正确发现

## 数据结构建议

### 任务对象

```python
{
  "name": "lesson01.mp4",
  "input_path": "/data/input/lesson01.mp4",
  "output_name": "lesson01_dub.mp4",
  "fingerprint": {
    "size": 123456,
    "mtime": 1711111111,
  },
  "planned": True,
}
```

### 状态对象

```python
{
  "version": 1,
  "jobs": {
    "lesson01.mp4": {
      "status": "success",
      "fingerprint": {
        "size": 123456,
        "mtime": 1711111111
      },
      "error_step": None,
      "error_message": None,
      "output_file": "lesson01_dub.mp4",
      "updated_at": "2026-03-22T12:00:00"
    }
  }
}
```

### 报告对象

```python
{
  "started_at": "2026-03-22T12:00:00",
  "finished_at": "2026-03-22T13:30:00",
  "input_dir": "/data/input",
  "output_dir": "/data/output",
  "recursive": True,
  "total_detected": 37,
  "planned": 12,
  "skipped": 25,
  "succeeded": 10,
  "failed": 2
}
```

## 退出码约定

1. `0`：全部成功，或全部已跳过
2. `1`：至少有一个任务失败
3. `2`：参数错误、环境错误或启动前校验失败

## 验收清单

### 功能

1. 本地视频可正常处理
2. 结果文件出现在输出目录
3. 状态文件正确写入
4. 重复运行可自动跳过
5. `--force` 可重跑
6. `--dry-run` 不执行真实任务

### 稳定性

1. 状态文件不会写坏
2. 不允许双开
3. 单个任务失败不影响整体批次
4. 最终成功文件大小大于 0

### 易用性

1. 启动摘要清晰
2. 结束摘要清晰
3. 错误信息包含文件名、步骤、错误消息

## 最小测试矩阵

### 单元测试

1. 参数解析
2. 文件指纹生成
3. 状态文件读写
4. 跳过规则判断
5. 报告生成

### 集成测试

1. 单文件成功
2. 单文件失败
3. 多文件混合成功/失败
4. 二次运行跳过成功任务
5. `--force` 重跑
6. `--dry-run` 不执行

## 开发顺序建议

1. 先实现主链路，不要一开始做 `--job-file`
2. 先保证串行稳定，不要碰并发
3. 先把状态、锁、报告做好，再考虑更多参数
4. 真正复杂的批任务等 V1 稳定后再扩展

## 当前推荐下一步

如果现在开始编码，最合理的第一步是：

1. 新建 `cli/batch_translate.py`
2. 新建 `state_store.py`
3. 新建 `runner.py`
4. 用最小命令先打通 1 个本地视频的完整处理链路
