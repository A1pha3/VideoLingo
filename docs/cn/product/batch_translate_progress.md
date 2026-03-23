# batch_translate CLI 任务进度

## 文档定位

这份文档用于持续记录 batch_translate CLI 的推进状态。

配套文档：

- 方案设计：`docs/cn/product/batch_transalte.md`
- 现有入口分析：`docs/cn/product/batch_processor_detail.md`
- 开发清单：`docs/cn/product/batch_translate_dev_todo.md`
- 使用说明：`docs/cn/product/batch_translate_user_guide.md`

后续无论是继续补方案、开始编码，还是补测试，都优先更新这里的状态。

## 当前阶段

当前处于：**CLI V1 已完成实现、验证与用户文档补齐。**

## 当前进度总览

### 已完成

1. 完成目录驱动 CLI 的总体设计文档
2. 完成对现有 `batch_processor.py` 的详细拆解
3. 完成 V1 范围收敛与参数策略设计
4. 完成开发清单、模块划分、验收标准与测试矩阵整理
5. 完成 CLI V1 主入口与基础模块落盘
6. 完成帮助命令真实环境验证
7. 修复项目 conda 激活脚本的 shell 选项泄漏问题
8. 完成 dry-run 最小链路验证，并确认报告文件可生成
9. 修复 `setup.py` 的包发现范围，使新增 `cli` 包可被安装发现
10. 新增 CLI unittest 18 项，并全部通过
11. 完成 `runner.py` 的成功与失败路径测试覆盖
12. 新增运行前配置预检，避免缺少关键配置时进入耗时处理
13. 增强锁文件处理，支持清理陈旧锁
14. 使用真实演示视频完成一次真实链路验证，确认成品、状态文件、报告文件和锁释放均正常
15. 完成真实成功样本的二次运行验证，确认会按状态文件跳过已完成任务
16. 清理 CLI 运行路径中的 Streamlit 依赖，确认 dry-run 与真实执行日志不再出现 `streamlit.runtime.caching` warning
17. 新增用户使用文档，补齐运行方式、状态文件、退出码和排障说明

### 进行中

1. 评估是否需要为真实链路补充可替换的集成测试夹具
2. 如需进一步产品化，补充失败样本目录的清理策略说明
3. 如需对外使用，补充 README 风格的简版入口说明

### 未开始

1. 如需进一步产品化，补充失败样本目录的清理策略说明
2. 如需对外使用，补充用户操作示例与故障排查说明
3. 如需维护成本更低，考虑补一个更小的 README 入口摘要

## 里程碑状态

| 里程碑 | 状态 | 说明 |
| --- | --- | --- |
| M1 方案设计完成 | 已完成 | 已形成完整设计与边界定义 |
| M2 现有代码复用路径确认 | 已完成 | 已确认以 `process_video()` 为主复用点 |
| M3 开发任务拆解完成 | 已完成 | 已形成模块拆分与实施阶段 |
| M4 CLI V1 主链路编码 | 已完成 | 主入口、基础模块与 CLI 执行路径已落盘并验证 |
| M5 状态、锁、报告补齐 | 已完成 | 已由真实单视频链路验证成品落盘、状态回写、报告生成和锁释放 |
| M6 可用性与测试校验 | 已完成 | 帮助命令、dry-run、预检逻辑、18 项 unittest、真实成功链路、真实失败链路、真实跳过逻辑和真实 `--force` 重跑均已验证 |

## 当前推荐下一步

按优先级建议的下一步是：

1. 如需发布给他人使用，补一段失败样本与 ERROR 归档说明
2. 如需面向团队交付，补一份 README 风格的简版入口说明
3. 视需要评估真实链路集成测试夹具

## 当前实现备注

### 1. `--dry-run` 当前行为

当前实现中：

- 会生成 `batch_translate_report.json`
- 不会生成 `batch_translate_status.json`

这是当前实现的明确行为，不是 bug。

### 2. 当前已通过的测试范围

当前已覆盖并通过的测试包括：

- 参数解析
- 状态文件写入与跳过规则
- 扫描逻辑与重复文件名保护
- `runner.py` 的成功路径与失败路径
- 运行前配置预检
- 锁文件创建、活锁拒绝和陈旧锁恢复

尚未覆盖的主要是：

- 失败样本归档策略的用户文档补充
- 用户操作与排障文档补充
- README 风格入口文档补充

## 当前风险

### 1. 归档目录依赖现有 `cleanup()` 规则

影响：

- 如果归档目录定位规则理解错，CLI 可能找不到最终成品

当前处理：

- 已在方案文档中明确将此作为重点风险
- 编码阶段需要优先做最小链路验证

### 2. 全局工作目录冲突

影响：

- 多实例执行会相互污染 `output/` 和 `batch/input/`

当前处理：

- 方案已明确要求加入单实例锁

### 3. 状态文件与真实输出不一致

影响：

- 可能出现状态写成功但目标输出未真正落盘

当前处理：

- 方案已明确要求原子写状态和原子复制成品

### 4. source 激活脚本对当前 shell 的副作用

影响：

- 在 VS Code 集成终端中，`source` 之后可能触发 `RPROMPT` 等变量相关警告

当前处理：

- 已将两个项目 conda 脚本改为 `emulate -L zsh`，限制 shell 选项泄漏到调用方环境

### 5. VS Code 集成终端的 prompt hook 噪声

影响：

- 在当前工具终端里仍可能看到 `__vsc_preexec` 或 `RPROMPT` 相关提示

当前处理：

- 已确认项目环境路径与 CLI 帮助命令本身可正常工作
- 暂将其视为 VS Code 终端 hook 噪声，不作为 CLI 逻辑缺陷处理

### 6. 真实链路验证耗时较长

影响：

- 真实样本验证可能在转写和音频分离阶段持续较长时间
- 当前回合内未必能立即得到最终成品与报告文件

当前处理：

- 已用仓库内 `docs/public/videos/demo.mp4` 完成一次真实验证
- 已确认最终输出文件、状态文件和报告文件均正确落盘
- 二次运行已验证会直接跳过成功任务

### 7. CLI 执行路径曾混入 Streamlit warning

影响：

- 之前的 dry-run 与真实运行日志顶部会出现 `streamlit.runtime.caching` warning

当前处理：

- 已移除 `video_processor.py` 对 `core.st_utils.imports_and_utils` 的无用依赖
- 已将 `runner` 导入延迟到真正开始执行任务时
- 已通过 dry-run 与真实失败样本验证，确认 warning 不再出现

## 文档更新记录

### 2026-03-22

1. 新增总体方案文档 `batch_transalte.md`
2. 新增现有批处理入口分析文档 `batch_processor_detail.md`
3. 新增开发清单文档 `batch_translate_dev_todo.md`
4. 新增本进度文档 `batch_translate_progress.md`
5. 新增 CLI V1 主入口与基础模块
6. 用项目激活脚本完成 `python -m cli.batch_translate --help` 验证
7. 修复 `activate_project_conda_env.zsh` 与 `setup_project_conda_env.zsh` 的 shell 选项泄漏问题
8. 使用占位 `.mp4` 文件完成 `--dry-run` 验证，并生成 `batch_translate_report.json`
9. 修复 `setup.py`，确保新增 `cli` 包在安装模式下可被发现
10. 新增 3 个 CLI unittest 文件，共 9 项测试，执行结果为 `OK`
11. 新增 `tests/test_batch_translate_runner.py`，扩展后共 15 项测试，执行结果为 `OK`
12. 新增 `cli/batch_translate_lib/preflight.py` 与对应测试，将缺失关键配置的失败前移到入口
13. 新增 `tests/test_batch_translate_lockfile.py`，扩展后共 18 项测试，执行结果为 `OK`
14. 使用 `docs/public/videos/demo.mp4` 启动真实样本验证，确认状态文件进入 `running`，并由活锁阻止重复实例
15. 真实样本最终产出 `demo_dub.mp4`，报告显示 `succeeded=1 failed=0`
16. 二次运行同一输入目录，CLI 正确输出 `Will Run: 0`、`Will Skip: 1`，退出码为 `0`
17. 使用空 `bad.mp4` 完成真实失败样本验证，退出码为 `1`，状态文件记录 `failed/transcribe`
18. 再次运行失败样本，CLI 正确输出 `Will Run: 1`、`Will Skip: 0`，确认失败任务不会被误跳过
19. 在真实成功样本上执行 `--force`，报告显示 `planned=1 skipped=0 succeeded=1`，确认会强制重跑而非跳过
20. 移除 `video_processor.py` 对 Streamlit UI 模块的无用依赖，并延迟导入 `runner`
21. 重新运行 18 项 CLI unittest，结果为 `OK`
22. 使用新的 dry-run 与真实失败样本验证日志，确认不再出现 `streamlit.runtime.caching` warning
23. 新增 `batch_translate_user_guide.md`，补齐使用说明与排障入口

## 更新规则

后续推进时，建议按下面规则维护这份文档：

1. 每完成一个阶段，就更新“当前阶段”
2. 每新增一个核心文件，就更新“当前进度总览”
3. 每发现一个高风险点，就补到“当前风险”
4. 每完成一轮实现或验证，就补到“文档更新记录”
