# 多角色配音功能设计文档

> 状态：方案设计中，暂不实施
>
> 文档用途：用于后续资料调研、产品评审、技术评审与分阶段实施决策

## 1. 背景

VideoLingo 当前已经具备完整的视频翻译与配音流水线，适合处理单旁白、单主持人、单讲者这类场景。

但在访谈、影视片段、播客对话、多人解说、剧情短视频等场景中，原视频通常包含多个说话人，存在以下典型需求：

- 男角色和女角色希望使用不同音色
- 同一角色在整段视频中希望保持稳定的声音身份
- 配音结果希望保留角色差异，而不是整条视频都使用同一个统一 voice
- 用户希望在自动化和可控性之间做取舍：既可以自动推荐，也可以人工修正

当前系统对这类需求没有形成完整能力，因此需要提前设计一份可评审的方案文档，明确：

- 当前系统的能力边界
- 为什么暂时不建议直接实现
- 如果未来要做，应采用什么架构与实施顺序

## 2. 当前现状

### 2.1 当前支持的能力

当前配音能力主要分为两类：

#### A. 单 voice 配置型后端

例如：

- Edge TTS
- Azure TTS
- OpenAI TTS
- Fish TTS

这类后端通常通过单个全局配置项指定 voice，整条视频默认使用同一个 voice。

#### B. 参考音频驱动型后端

例如：

- GPT-SoVITS
- SiliconFlow FishTTS dynamic
- SiliconFlow CosyVoice2

这类后端已经具备“按句使用参考音频”的能力，因此在部分视频中可能表现出一定程度的多角色差异感，但本质上仍然不是完整的“多角色配音系统”。

### 2.2 当前不支持的能力

当前系统不支持以下能力：

- 自动识别多个角色并为每个角色绑定不同 voice
- 基于男声/女声自动切换不同 TTS voice
- 为同一角色在整条视频中维持稳定 voice identity
- 在 UI 中查看、编辑、覆盖“角色 -> voice”的映射关系
- 在 TTS 调度层对每一句字幕动态选择不同 voice

### 2.3 根本原因

问题不在于“没有一个下拉框”，而在于整条数据链路中缺少角色身份的持久化与调度机制。

当前链路的问题主要有四个：

#### 1. speaker 信息没有穿透到 TTS 阶段

部分 ASR 后端已经存在 `speaker_id`，但在后续字幕处理、音频任务生成、配音切块、TTS 调度过程中，这个字段没有被持续保留与使用。

#### 2. 音频任务合并逻辑不是 speaker-aware

当前短字幕合并与配音块切分逻辑主要按时长、停顿和文本长度工作，没有把“说话人边界”作为硬约束。结果是不同角色的文本有可能被合并到同一个 TTS 任务中。

#### 3. TTS 调度是全局 voice 思路

当前大部分 TTS 后端是“一个视频一个 voice”的设计，而不是“每句可覆盖 voice”。

#### 4. UI 与配置系统没有角色映射层

当前配置可以设置：

- 全局 `tts_method`
- 某个后端的单个 voice 或 character

但没有角色层级的配置，例如：

- SPK_0 -> 男声 A
- SPK_1 -> 女声 B
- SPK_2 -> 保持默认 voice

## 3. 问题定义

未来如果要支持多角色配音，需要先明确目标问题是什么。

### 3.1 我们真正想解决的问题

目标不是简单地“支持多个 voice”，而是：

> 在一个视频中识别多个说话人，并在配音阶段对不同说话人稳定地使用不同声音，同时允许用户查看、调整和覆盖自动分配结果。

### 3.2 这不是同一个问题的三种说法

以下三种诉求看起来相似，但技术难度和实现方式不同：

#### 需求 A：一个视频里允许用多种 voice

这是最基础的能力，表示系统允许不同句子使用不同的 voice。

#### 需求 B：同一个 speaker 始终绑定一个稳定 voice

这是多角色配音真正需要解决的核心问题。

#### 需求 C：自动判断男声/女声并自动分配对应 voice

这是在需求 B 之上的增强能力，风险更高，误判概率也更大。

未来实施时应按 A -> B -> C 的顺序推进，而不是一步做到位。

## 4. 设计目标

### 4.1 总目标

建立一套“多说话人感知”的配音架构，使 VideoLingo 在未来具备：

- 保留 speaker 信息到 TTS 阶段
- 为不同 speaker 分配不同 voice
- 支持手工编辑 speaker 到 voice 的映射
- 在部分后端中支持自动推荐 voice
- 在最终视频中稳定输出多角色配音结果

### 4.2 分阶段目标

#### 第一阶段：可控多 speaker 配音

目标：

- 保留并使用 `speaker_id`
- 支持手工配置 `speaker -> voice`
- 至少让 Edge TTS / Azure TTS 这类后端可以按 speaker 切 voice

这阶段不追求自动识别男/女，也不追求完全自动化。

#### 第二阶段：自动推荐

目标：

- 对 speaker 进行基础画像
- 自动推荐更合适的 voice
- 允许用户覆盖推荐结果

#### 第三阶段：高级自动化

目标：

- 自动性别识别
- 自动 voice 分配
- 后续可扩展到角色聚类、情绪感知、主配角策略

## 5. 非目标

以下内容不属于第一版应解决的问题：

- 自动识别剧情角色姓名
- 自动识别角色阵营、身份、年龄
- 自动匹配最像原声的商业级 voice clone
- 完整做到影视级人物配音一致性
- 完全无人介入的高可靠角色分配

这些方向可以作为长期研究项，但不应进入第一版范围。

## 6. 为什么现在先不做

当前阶段不建议立即实施，原因如下：

### 6.1 复杂度高

该功能需要同时改动：

- ASR 结果结构
- 字幕切分与合并逻辑
- 音频任务表结构
- 配音切块逻辑
- TTS 调度层
- Streamlit 配置 UI
- 配置持久化结构
- 文档与测试体系

这不是一个单点功能，而是对整条配音链路的结构性升级。

### 6.2 自动效果不确定

即使实现了自动 speaker 分离和 gender 识别，也会遇到很多不稳定场景：

- 小孩声音与女声混淆
- 中性音色误判
- 同一角色在不同情绪下声线变化很大
- 背景噪音、BGM、混响干扰
- ASR 切分边界与真实角色边界不完全一致

### 6.3 用户体验风险高

如果系统直接“自动分错 voice”，用户感知会比“全片单 voice”更差。

因此未来实施时必须优先保证：

- 自动结果可见
- 用户可修改
- 用户可关闭

## 7. 总体方案概览

推荐采用四层架构：

### 7.1 Speaker Detection Layer

职责：识别说话人边界，给每个句段打上 `speaker_id`

输入：

- ASR 原始结果

输出：

- 带 `speaker_id` 的句段或词级结果

### 7.2 Speaker Profiling Layer

职责：对每个 speaker 生成可用于推荐的画像信息

可能包含：

- 性别提示 `gender_hint`
- 置信度 `confidence`
- 代表性参考音频 `reference_clip`
- 平均音高、时长、说话节奏等统计特征

### 7.3 Voice Mapping Layer

职责：把 speaker 映射到最终用于配音的 voice 或 character

支持三种来源：

- 系统自动推荐
- 用户手工指定
- 全局默认兜底

### 7.4 TTS Execution Layer

职责：在每个 TTS 任务执行时，根据当前句子的 `speaker_id` 选择相应 voice

## 8. 方案分级

未来实施建议分三版推进。

### 8.1 版本 V1：手工可控版

#### 目标

- 系统识别 speaker 或从 ASR 获取 speaker
- UI 展示 speaker 列表
- 用户手动为每个 speaker 选择 voice
- TTS 执行时按 speaker 切换 voice

#### 特点

- 自动化程度低
- 实现复杂度相对可控
- 可解释性强
- 风险最低

#### 适合的后端

- Edge TTS
- Azure TTS
- OpenAI TTS

### 8.2 版本 V2：自动推荐版

#### 目标

- 根据音色特征和可选 gender 分类结果，给每个 speaker 推荐 voice
- 用户可接受或覆盖推荐结果

#### 特点

- 自动化增强
- 仍保留人工确认流程
- 适合作为默认体验提升，而不是强制自动化

### 8.3 版本 V3：克隆增强版

#### 目标

- 对支持参考音频的后端，为每个 speaker 维护独立参考音频池
- 提升多角色克隆类后端的一致性

#### 适合的后端

- GPT-SoVITS
- SiliconFlow FishTTS dynamic
- CosyVoice2
- 未来可能支持的更多 voice cloning 后端

## 9. 数据模型设计

### 9.1 ASR 结果扩展

建议未来在句段层统一保留以下字段：

```json
{
  "segment_id": 12,
  "start": 31.25,
  "end": 34.82,
  "text": "Hello everyone",
  "speaker_id": "SPK_1",
  "speaker_confidence": 0.91
}
```

### 9.2 音频任务表扩展

当前 `_8_1_AUDIO_TASK.xlsx` 建议未来新增以下列：

- `speaker_id`
- `speaker_group`
- `voice_key`
- `voice_source`
- `gender_hint`
- `voice_override`

示例：

| number | start_time | end_time | text | origin | speaker_id | voice_key | voice_source |
|------|------|------|------|------|------|------|------|
| 1 | 00:00:01.000 | 00:00:03.500 | 大家好 | Hello everyone | SPK_0 | zh-CN-YunxiNeural | manual |
| 2 | 00:00:03.500 | 00:00:05.800 | 欢迎回来 | Welcome back | SPK_1 | zh-CN-XiaoxiaoNeural | manual |

### 9.3 配置结构扩展

建议未来在 `config.yaml` 中引入：

```yaml
multi_speaker_dubbing:
  enabled: false
  mode: manual
  auto_assign_by_gender: false
  default_voice:
    edge_tts: zh-CN-XiaoxiaoNeural
    azure_tts: zh-CN-XiaoxiaoMultilingualNeural
  speaker_voice_map:
    SPK_0:
      edge_tts: zh-CN-YunxiNeural
      azure_tts: zh-CN-YunxiMultilingualNeural
    SPK_1:
      edge_tts: zh-CN-XiaoxiaoNeural
      azure_tts: zh-CN-XiaoxiaoMultilingualNeural
```

### 9.4 Speaker 画像缓存

建议新增缓存文件，例如：

```text
output/audio/speaker_profiles.json
```

用于记录：

- speaker_id
- 代表性 reference 音频路径
- gender_hint
- 推荐 voice 列表
- 用户最后一次确认结果

## 10. 流程设计

### 10.1 新的处理主流程

建议未来多角色配音流程如下：

1. ASR 输出带 speaker_id 的结果
2. 句子切分时保留 speaker_id
3. 生成字幕时保留 speaker_id
4. 生成音频任务时保留 speaker_id
5. 短句合并时禁止跨 speaker 合并
6. 配音切块时禁止跨 speaker 合并
7. 生成 speaker 列表和推荐 voice
8. 用户在 UI 中确认或修改 speaker -> voice 映射
9. TTS 按句读取 speaker_id 选择 voice
10. 最终合成视频

### 10.2 合并策略的关键约束

未来所有“合并句子”的地方都必须增加以下约束：

> 如果当前句与下一句的 `speaker_id` 不同，则禁止合并。

否则会出现一个 TTS 任务内同时混入两个角色的文本，后续无法准确切 voice。

### 10.3 兜底策略

如果以下任一条件不满足：

- 没有 speaker_id
- speaker 分类失败
- voice mapping 不完整
- 用户未确认映射

系统应自动回退到单 voice 模式，而不是继续半残地执行。

## 11. UI 设计

### 11.1 配置入口

建议在 Streamlit 的 `Dubbing Settings` 下增加一个新的折叠区：

- `Multi-Speaker Dubbing`

包含以下选项：

- 启用多角色配音
- 模式选择：`off / manual / auto-recommend`
- 是否启用按性别自动推荐
- 默认 voice

### 11.2 Speaker 映射面板

建议在检测到 speaker 后，展示一个列表：

| Speaker | 样例文本 | 推荐 | 当前 voice | 操作 |
|------|------|------|------|------|
| SPK_0 | 大家好，欢迎回来 | 男声推荐 | Yunxi | 可切换 |
| SPK_1 | 今天我们继续聊 | 女声推荐 | Xiaoxiao | 可切换 |

建议提供以下交互：

- 播放该 speaker 的参考原声
- 试听目标 voice
- 一键应用推荐
- 手动覆盖 voice
- 恢复默认

### 11.3 透明度要求

UI 必须清楚告知：

- 自动推荐不保证完全正确
- 用户修改优先级高于系统推荐
- 若关闭该功能，系统自动回退到单 voice 配音

## 12. 后端适配策略

### 12.1 Edge TTS / Azure TTS / OpenAI TTS

这是最适合先支持多角色配音的后端。

原因：

- voice 是显式字符串配置
- 切换成本低
- 每句切换 voice 容易实现
- 结果可控、便于调试

建议第一版优先支持这类后端。

### 12.2 GPT-SoVITS / FishTTS dynamic / CosyVoice2

这类后端更适合第二阶段和第三阶段。

原因：

- 它们更依赖 reference audio，而不是单个 voice code
- 未来应做成 `speaker -> reference bank` 的映射，而不是简单的 `speaker -> voice string`

#### 建议策略

- 为每个 speaker 选择代表性参考音频
- 为每个 speaker 维护单独的 reference cache
- 在 TTS 阶段按 speaker_id 传递对应 reference

### 12.3 F5-TTS

当前实现更偏向整片复用同一个 reference audio，不适合第一版多角色方案。

如果未来需要支持，应单独重构为 per-speaker reference upload 流程。

## 13. 自动推荐策略设计

### 13.1 推荐而不是强制自动分配

未来若做“男声/女声自动切换”，应默认作为推荐机制，而不是直接强制使用。

### 13.2 可能的推荐输入

- speaker 的平均基频
- 高频能量分布
- 音色 embedding
- 说话速度
- 参考音频时长

### 13.3 推荐输出

推荐结果建议包含：

- `gender_hint`: male / female / unknown
- `confidence`: 0~1
- `recommended_voices`: 候选列表
- `reason`: 简短解释

### 13.4 误判风险

以下情况应特别注意：

- 儿童说话人
- 中性音色
- 反串表演
- 情绪化高音/低音
- 低质量录音

因此推荐系统必须允许用户修改，而不是直接生效。

## 14. 缓存与断点恢复设计

多角色配音会引入更多缓存失效场景，未来需要统一考虑。

### 14.1 新增的缓存依赖

一旦以下任意项变化，应考虑失效相关音频缓存：

- `speaker_voice_map`
- `default_voice`
- `multi_speaker_dubbing.enabled`
- `multi_speaker_dubbing.mode`
- `speaker_profiles.json`
- 代表性参考音频的选择结果

### 14.2 推荐新增签名维度

建议在现有 TTS cache signature 的基础上追加：

- `speaker_id`
- `voice_key`
- `voice_source`
- `reference_audio_hash`

否则会出现用户改了 speaker 映射，但系统仍复用旧音频的情况。

## 15. 测试策略

### 15.1 功能测试

至少覆盖以下场景：

- 单 speaker 视频，功能关闭
- 单 speaker 视频，功能开启
- 双 speaker 视频，手工映射两个不同 voice
- 多 speaker 视频，其中一个 speaker 未配置 voice
- 自动推荐后用户手工覆盖

### 15.2 回归测试

必须确认以下功能不被破坏：

- 单 voice 正常配音
- 双语配音字幕开关
- 删除并重试配音
- 缓存失效逻辑
- 原有各 TTS 后端

### 15.3 质量测试

需要人工听测以下问题：

- 角色 voice 是否稳定
- 是否出现角色错配
- 是否出现跨 speaker 合并导致的一句多音色问题
- 语速和时长是否明显异常

## 16. 风险清单

### 16.1 技术风险

- speaker diarization 稳定性不足
- gender 分类误判
- 不同后端对多 speaker 支持程度差异大
- 参考音频切分质量影响克隆效果

### 16.2 产品风险

- 功能复杂，用户学习成本高
- 自动结果不可信时，用户感知可能比单 voice 更差
- UI 如果过于复杂，会拉高 Streamlit 配置面板的理解成本

### 16.3 维护风险

- 每增加一个 TTS 后端，都要考虑 multi-speaker 兼容策略
- 后续代码复杂度、缓存逻辑、问题排查成本都会上升

## 17. 推荐实施顺序

未来若决定实施，建议严格按以下顺序推进。

### 第一阶段：基础设施改造

- 保留 `speaker_id` 到 TTS 任务阶段
- 所有合并逻辑改为 speaker-aware
- 在缓存签名中加入 speaker/voice 维度

### 第二阶段：手工可控多角色配音

- 新增 `speaker_voice_map`
- TTS 调度支持 per-line voice override
- Edge TTS / Azure TTS 先支持多 speaker
- UI 展示 speaker 列表并允许手动切换 voice

### 第三阶段：自动推荐

- 增加 speaker profiling
- 增加 gender_hint 与候选 voice 推荐
- 用户确认后再执行配音

### 第四阶段：克隆类后端增强

- 按 speaker 构建 reference bank
- GPT-SoVITS / CosyVoice2 / FishTTS dynamic 适配 per-speaker reference

## 18. 暂定里程碑建议

### 里程碑 M1：技术可行性验证

目标：

- 用一个双人对话视频验证 speaker_id 能否稳定传递到 TTS 任务表
- 验证 Edge TTS 是否能在同一视频里按 speaker 切换两种 voice

### 里程碑 M2：最小可用版本

目标：

- 手工映射两个 speaker
- 生成可接受的多角色配音视频
- UI 可配置

### 里程碑 M3：推荐系统

目标：

- 基础自动推荐
- 用户确认再执行

## 19. 实施前必须回答的问题

在真正启动开发前，建议先完成以下资料收集与决策：

### 产品问题

- 是否真的有足够多用户需要多角色配音
- 用户更需要“自动化”还是“可控性”
- 第一版是否只支持部分 TTS 后端

### 技术问题

- 当前默认 ASR 后端中，哪个最稳定提供 speaker_id
- 现有分句逻辑引入 speaker-aware 约束后，对字幕质量影响多大
- 当前缓存系统是否足以承载 speaker 维度扩展

### 体验问题

- UI 放在侧边栏是否会过于拥挤
- 是否需要单独的“角色配音设置页”
- 是否要先做离线配置，再开始配音

## 20. 最终建议

综合当前系统现状、复杂度和效果不确定性，建议如下：

### 当前决策

- 暂不实施多角色配音功能
- 先保留该设计文档，作为后续调研与评审基础

### 未来如果重启该需求

建议从“手工可控多 speaker 配音”开始，而不是直接做“自动识别男声/女声自动切 voice”。

原因：

- 风险更低
- 结果更可控
- 更容易验证产品价值
- 更适合逐步扩展到克隆类后端

### 一句话总结

> 多角色配音不是一个简单的 voice 下拉框问题，而是一次从 ASR 到 TTS 的整条链路升级。若未来实施，应优先做“speaker 保留 + 手工映射 + per-line voice override”，再考虑自动推荐与自动性别判断。
