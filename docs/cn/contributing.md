# 贡献指南

> 如何为 VideoLingo 项目做出贡献

## 学习目标

完成本教程后，你将能够：
- 理解项目的贡献流程
- 了解代码审查标准
- 掌握 Issue 和 PR 的最佳实践

## 贡献类型

我们欢迎以下类型的贡献：

| 类型 | 说明 | 示例 |
|------|------|------|
| 🐛 Bug 修复 | 修复已知问题 | 修复字幕时间轴偏移 |
| ✨ 新功能 | 添加新功能 | 支持新的 TTS 引擎 |
| 📝 文档 | 改进文档 | 修正错误、添加示例 |
| 🎨 UI/UX | 改进用户界面 | 优化 Streamlit 布局 |
| ⚡ 性能 | 提升性能 | 优化处理速度 |
| 🧪 测试 | 添加测试 | 添加单元测试 |
| 🌍 国际化 | 添加翻译 | 添加新的界面语言 |

## 开始之前

### 行为准则

- 尊重所有贡献者
- 建设性反馈
- 接受不同观点
- 专注于解决问题而非人身攻击

### 兼容性要求

- Python 3.10+
- 跨平台支持（Windows/macOS/Linux）
- 向后兼容配置文件

## 贡献流程

### 1. 寻找要解决的问题

**好问题来源**：

- [Issues](https://github.com/Huanshere/VideoLingo/issues) - 标记为 `good first issue` 或 `help wanted`
- 自己使用中发现的问题
- 功能建议（先创建 Issue 讨论）

**在开始工作前**：

1. 检查是否已有相关 Issue
2. 如果没有，创建新 Issue 描述你的计划
3. 等待维护者确认

### 2. Fork 并克隆

```bash
# 1. Fork 仓库到你的账号
# 2. 克隆你的 Fork
git clone https://github.com/your-username/VideoLingo.git
cd VideoLingo

# 3. 添加上游仓库
git remote add upstream https://github.com/Huanshere/VideoLingo.git

# 4. 创建功能分支
git checkout -b feature/your-feature-name
```

### 3. 开发

**开发环境**：

```bash
# 创建虚拟环境
conda create -n videolingo-dev python=3.10 -y
conda activate videolingo-dev

# 安装依赖
pip install -e .

# 安装开发工具
pip install pre-commit black flake8
```

**代码规范**：

```bash
# 格式化代码
black .

# 检查代码
flake8 .
```

**提交信息格式**：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型（type）：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建/工具更新

示例：

```
feat(tts): add support for Azure TTS

- Implement Azure TTS backend
- Add configuration options
- Update documentation

Closes #123
```

### 4. 测试

```bash
# 运行应用
streamlit run st.py

# 测试单个模块
python -m core._2_asr

# 运行批处理测试
python -m batch.utils.batch_processor
```

**测试清单**：

- [ ] 功能正常工作
- [ ] 没有新的警告
- [ ] 跨平台兼容（如果可能）
- [ ] 文档已更新

### 5. 创建 Pull Request

```bash
# 推送到你的 Fork
git push origin feature/your-feature-name

# 在 GitHub 上创建 PR
```

**PR 标题格式**：与提交信息相同

**PR 描述模板**：

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 破坏性变更
- [ ] 文档更新

## 描述
简要描述你的变更...

## 相关 Issue
Closes #(issue number)

## 测试
描述你如何测试这些变更...

## 截图（如适用）
```

### 6. 代码审查

审查期间可能需要：

1. **回复评论**：解释你的设计决策
2. **修改代码**：根据反馈调整
3. **更新测试**：确保新功能有测试

**审查标准**：

- 代码符合项目规范
- 变更有充分的理由
- 文档已更新
- 没有引入新问题

### 7. 合并

审查通过后，维护者会合并你的 PR。

```bash
# 更新本地仓库
git checkout main
git pull upstream main

# 删除已合并的分支
git branch -d feature/your-feature-name
```

## 开发指南

### 项目结构

```
VideoLingo/
├── core/              # 核心处理逻辑
├── batch/             # 批处理
├── docs/              # 文档
├── translations/      # 国际化
├── config.yaml        # 配置
├── install.py         # 安装脚本
├── setup.py           # 包设置
├── st.py              # Streamlit 入口
└── requirements.txt   # 依赖
```

### 添加新功能

**决策清单**：

- [ ] 是否符合项目目标？
- [ ] 是否需要新依赖？如果有，是否合理？
- [ ] 是否影响现有功能？
- [ ] 是否需要更新配置？
- [ ] 是否需要更新文档？

### 添加 TTS/ASR 后端

参考：
- [TTS 后端扩展](advanced/tts-backend.md)
- [ASR 后端扩展](advanced/asr-backend.md)

### 修改 Prompt

Prompt 位于 `core/prompts.py`，修改时：

1. 保持结构一致
2. 测试多种模型
3. 添加注释说明修改原因

### 修改配置

1. 在 `config.yaml` 添加新配置
2. 更新 `core/utils/config_utils.py` 如果需要新函数
3. 更新文档

## 文档贡献

### 改进现有文档

1. 找到文档文件（`docs/` 目录）
2. 编辑文档
3. 提交 PR

### 添加新文档

1. 在适当的目录创建新文件
2. 遵循现有文档格式
3. 更新 `README.md` 添加链接

### 翻译文档

1. 复制英文文档到对应语言目录
2. 翻译内容
3. 保持代码块和链接不变

## 报告 Bug

### Bug 报告模板

```markdown
**问题描述**
简要描述问题...

**复现步骤**
1. 步骤一
2. 步骤二
3. 步骤三

**预期行为**
描述你期望发生什么...

**实际行为**
描述实际发生了什么...

**环境信息**
- OS: [e.g. Windows 11]
- Python 版本: [e.g. 3.10.0]
- GPU: [e.g. RTX 3080]
- VideoLingo 版本: [e.g. 3.0.0]

**日志**
```
粘贴相关日志...
```

**截图**
如果有，请添加截图

**附加信息**
任何其他相关信息...
```

## 功能建议

### 功能请求模板

```markdown
**功能描述**
简要描述你希望添加的功能...

**问题背景**
这个功能解决什么问题？为什么需要？

**建议方案**
你希望这个功能如何工作...

**替代方案**
描述你考虑过的替代方案...

**附加信息**
任何其他相关信息、截图等...
```

## 代码审查

### 审查者指南

**关注点**：

1. **正确性**：代码是否实现预期功能
2. **可读性**：代码是否易于理解
3. **维护性**：代码是否易于维护
4. **性能**：是否有明显的性能问题
5. **测试**：是否有足够的测试

**评论风格**：

- ✅ "考虑使用 X 代替 Y，因为..."
- ✅ "我建议重构这部分，原因是..."
- ❌ "这段代码不好"

### 作者回应

- 接受建设性反馈
- 解释不清楚的设计决策
- 愿意修改代码
- 提问以理解反馈

## 发布流程

维护者负责：

1. 更新版本号（`setup.py`）
2. 更新 CHANGELOG
3. 创建 Git tag
4. 发布 GitHub Release

## 许可证

贡献的代码将在 Apache License 2.0 下发布。

## 致谢

感谢所有贡献者！你的贡献让 VideoLingo 变得更好。

---

## 联系方式

- GitHub Issues: [提交问题](https://github.com/Huanshere/VideoLingo/issues)
- Email: team@videolingo.io
- Twitter: [@Huanshere](https://twitter.com/Huanshere)

## 下一步

- 📖 阅读 [开发指南](development.md) 开始开发
- 🔍 查看 [Issues](https://github.com/Huanshere/VideoLingo/issues) 寻找要解决的问题
