# 国际化指南

> 添加多语言支持的完整指南

## 学习目标

完成本教程后，你将能够：
- 添加新的界面语言
- 创建翻译文件
- 处理多语言文本
- 测试国际化功能

## 国际化架构

```
VideoLingo 国际化系统
├── translations/
│   ├── translations.py      # 翻译加载逻辑
│   ├── en.json             # 英文翻译
│   ├── zh-CN.json          # 简体中文翻译
│   ├── zh-HK.json          # 繁体中文翻译
│   ├── ja.json             # 日语翻译
│   ├── es.json             # 西班牙语翻译
│   ├── ru.json             # 俄语翻译
│   └── fr.json             # 法语翻译
└── config.yaml
    └── display_language     # 当前显示语言
```

## 添加新语言

### 步骤 1：创建翻译文件

在 `translations/` 目录创建新的 JSON 文件：

```bash
# 示例：添加韩语
touch translations/ko.json
```

### 步骤 2：定义翻译内容

```json
{
  "API_KEY": "API 密钥",
  "BASE_URL": "API 基础 URL",
  "MODEL": "模型",
  "LLM Configuration": "LLM 配置",
  "Subtitles Settings": "字幕设置",
  "Dubbing Settings": "配音设置",
  ...
}
```

**提示**：复制 `en.json` 作为模板，然后翻译所有键值。

### 步骤 3：注册语言

编辑 `translations/translations.py`：

```python
DISPLAY_LANGUAGES = {
    "🇬🇧 English": "en",
    "🇨🇳 简体中文": "zh-CN",
    "🇭🇰 繁体中文": "zh-HK",
    "🇯🇵 日本語": "ja",
    "🇪🸸 Español": "es",
    "🇷🇺 Русский": "ru",
    "🇫🇷 Français": "fr",
    "🇰🇷 한국어": "ko",  # 添加
}
```

### 步骤 4：测试新语言

```bash
# 在 config.yaml 中设置
display_language: "ko"

# 启动应用
streamlit run st.py
```

## 翻译管理

### 翻译键命名规范

```
格式：功能.子功能.具体项

示例：
- api.key → API 密钥
- whisper.model → Whisper 模型
- tts.azure_tts.voice → Azure TTS 语音
```

### 翻译工具

推荐工具：
- **Poedit**：专业的翻译编辑器
- **Crowdin**：协作翻译平台
- **DeepL**：机器翻译辅助

### 翻译检查

```python
# 检查缺失的翻译
import json

def check_translations():
    """检查所有语言文件的翻译完整性"""
    base_file = "translations/en.json"
    with open(base_file) as f:
        base_keys = set(json.load(f).keys())

    languages = ["zh-CN", "ja", "es", "ru", "fr"]

    for lang in languages:
        with open(f"translations/{lang}.json") as f:
            lang_keys = set(json.load(f).keys())

        missing = base_keys - lang_keys
        if missing:
            print(f"{lang}: 缺少 {len(missing)} 个翻译")
            for key in sorted(missing):
                print(f"  - {key}")
```

## 代码中使用

### 基本用法

```python
from translations.translations import translate as t

# 简单翻译
title = t("API_KEY")
st.title(title)

# 带参数翻译（如需）
message = t("welcome_message").format(name="用户")
```

### 动态语言切换

```python
import streamlit as st
from translations.translations import translate as t, DISPLAY_LANGUAGES
from core.utils import load_key, update_key

# 语言选择器
display_language = st.selectbox(
    "Display Language 🌐",
    options=list(DISPLAY_LANGUAGES.keys()),
    index=list(DISPLAY_LANGUAGES.values()).index(load_key("display_language"))
)

# 更新语言设置
if DISPLAY_LANGUAGES[display_language] != load_key("display_language"):
    update_key("display_language", DISPLAY_LANGUAGES[display_language])
    st.rerun()
```

### 回退机制

翻译键不存在时自动回退到键名：

```python
def translate(key):
    try:
        translations = load_translations(display_language)
        return translations.get(key, key)
    except:
        return key  # 回退到原键名
```

## 常见问题

### Q: 翻译显示为键名？

**原因**：翻译键在当前语言文件中不存在

**解决**：检查 JSON 文件是否包含该键，注意 JSON 格式正确性

### Q: 翻译不生效？

**原因**：
1. JSON 文件有语法错误
2. 语言代码不匹配
3. 缓存问题

**解决**：
```bash
# 验证 JSON 格式
python -m json.tool translations/zh-CN.json

# 重启应用
# 清除浏览器缓存
```

### Q: 如何处理复数形式？

使用不同的键：

```json
{
  "item": "项目",
  "items": "多个项目"
}
```

```python
count = 1
text = t("items" if count > 1 else "item")
```

## 最佳实践

1. **保持翻译同步**：添加新键时更新所有语言文件
2. **提供上下文**：翻译键名应清晰描述内容
3. **测试所有语言**：发布前测试每种语言
4. **使用专业翻译**：确保翻译质量
5. **收集反馈**：接受用户对翻译的改进建议

## 自测问题

添加国际化支持时，尝试回答以下问题：

1. **如何添加新的界面语言？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 在 `translations/` 目录创建新的语言文件（如 `fr.json`）
   2. 复制 `en.json` 作为模板
   3. 翻译所有键值
   4. 在 `config.yaml` 的 `display_language` 中添加选项
   5. 在 `translations/i18n.py` 中注册新语言
   </details>

2. **翻译键命名有什么规范？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 使用点号分隔命名空间：`section.action.description`
   2. 保持简洁但具有描述性
   3. 使用英文命名，便于维护
   4. 相似功能的键使用统一前缀
   </details>

3. **如何确保翻译质量？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 使用专业翻译或母语者审核
   2. 保持术语一致性
   3. 考虑文化差异和习惯表达
   4. 测试 UI 显示效果（不同语言文本长度差异）
   </details>

## 下一步

- 📖 阅读 [UI 定制指南](ui-customization.md) 了解界面开发
- 📖 阅读 [开发指南](development.md) 了解代码规范
