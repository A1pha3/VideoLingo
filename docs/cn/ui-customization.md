# UI 定制指南

> Streamlit 界面定制与开发

## 学习目标

完成本教程后，你将能够：
- 理解 Streamlit UI 架构
- 自定义界面组件
- 修改样式和布局
- 添加新功能模块

## UI 架构

```
st.py (主入口)
    ├── page_setting()        # 侧边栏设置
    ├── download_video_section()  # 视频下载区域
    ├── text_processing_section() # 文本处理区域
    └── audio_processing_section() # 音频处理区域

core/st_utils/
    ├── sidebar_setting.py    # 设置面板逻辑
    ├── download_video_section.py  # 下载组件
    └── imports_and_utils.py  # 工具函数和样式
```

## 样式定制

### 全局样式

在 `st.py` 中修改：

```python
import streamlit as st

# 自定义 CSS
st.markdown("""
<style>
    /* 主容器 */
    .main {
        background-color: #f5f5f5;
    }

    /* 按钮 */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }

    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)
```

### 主题配置

Streamlit 支持主题配置：

```toml
# .streamlit/config.toml

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#f5f5f5"
secondaryBackgroundColor = "#ffffff"
textColor = "#262730"
font = "sans serif"
```

## 组件定制

### 侧边栏设置

添加新的设置项：

```python
# core/st_utils/my_settings.py
import streamlit as st
from core.utils import load_key, update_key

def my_custom_settings():
    """自定义设置面板"""
    with st.expander("我的自定义设置"):
        value = st.text_input(
            "自定义选项",
            value=load_key("my_custom.option", default="")
        )
        update_key("my_custom.option", value)
```

在 `st.py` 中调用：

```python
from core.st_utils.my_settings import my_custom_settings

def main():
    # 在侧边栏添加
    with st.sidebar:
        page_setting()
        my_custom_settings()  # 添加自定义设置
```

### 处理区域

添加新的处理区域：

```python
# core/st_utils/my_section.py
import streamlit as st
from translations.translations import translate as t

def my_processing_section():
    """自定义处理区域"""
    st.header(t("我的新功能"))

    with st.container(border=True):
        st.markdown("功能描述...")

        if st.button(t("开始处理")):
            # 处理逻辑
            st.success("处理完成！")
```

## 布局定制

### 分栏布局

```python
# 两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("左侧")
    # 左侧内容

with col2:
    st.subheader("右侧")
    # 右侧内容
```

### 标签页

```python
# 使用标签页组织内容
tab1, tab2, tab3 = st.tabs(["选项1", "选项2", "选项3"])

with tab1:
    st.write("内容1")

with tab2:
    st.write("内容2")

with tab3:
    st.write("内容3")
```

### 可折叠区域

```python
# 使用 expander 组织复杂内容
with st.expander("高级选项", expanded=False):
    st.text_input("高级设置1")
    st.text_input("高级设置2")
```

## 国际化

### 添加翻译键

1. 在 `translations/en.json` 添加：

```json
{
  "my_new_key": "My new feature",
  "my_feature_description": "This is a new feature..."
}
```

2. 在 `translations/zh-CN.json` 添加：

```json
{
  "my_new_key": "我的新功能",
  "my_feature_description": "这是一个新功能..."
}
```

3. 在代码中使用：

```python
from translations.translations import translate as t

st.header(t("my_new_key"))
st.markdown(t("my_feature_description"))
```

### 添加新语言

1. 创建新的语言文件：`translations/ja.json`

```json
{
  "my_new_key": "私の新しい機能"
}
```

2. 在 `translations/translations.py` 中添加：

```python
DISPLAY_LANGUAGES = {
    "🇬🇧 English": "en",
    "🇨🇳 简体中文": "zh-CN",
    "🇯🇵 日本語": "ja",  # 添加
    # ...
}
```

## 交互组件

### 文件上传

```python
uploaded_file = st.file_uploader(
    "选择文件",
    type=["mp4", "mov", "avi"],
    help="支持的视频格式"
)

if uploaded_file:
    # 处理文件
    st.success(f"已上传：{uploaded_file.name}")
```

### 进度条

```python
import time

progress_bar = st.progress(0)
status_text = st.empty()

for i in range(100):
    progress_bar.progress(i + 1)
    status_text.text(f"处理中... {i+1}%")
    time.sleep(0.1)

status_text.text("完成！")
```

### 状态容器

```python
# 使用 container 组织相关组件
with st.container():
    st.subheader("处理选项")
    option1 = st.checkbox("选项1")
    option2 = st.checkbox("选项2")

    if option1 or option2:
        st.write("已选择选项")
```

## 高级定制

### 会话状态

```python
# 初始化状态
if "counter" not in st.session_state:
    st.session_state.counter = 0

# 使用状态
if st.button("增加计数"):
    st.session_state.counter += 1

st.write(f"计数：{st.session_state.counter}")
```

### 回调函数

```python
def on_button_click():
    st.session_state.clicked = True

st.button("点击我", on_click=on_button_click)

if st.session_state.get("clicked", False):
    st.write("按钮被点击了！")
```

### 动态表单

```python
import streamlit as st

# 根据选择动态显示表单
option = st.selectbox("选择类型", ["A", "B", "C"])

if option == "A":
    st.text_input("A 的配置")
elif option == "B":
    st.number_input("B 的配置")
else:
    st.text_area("C 的配置")
```

## 最佳实践

1. **组件复用**：将重复组件抽取为函数
2. **状态管理**：使用 `st.session_state` 管理状态
3. **性能优化**：使用 `@st.cache_data` 缓存数据
4. **错误处理**：使用 `st.error` 显示错误信息
5. **响应式设计**：使用 `st.columns` 适配不同屏幕

## 下一步

- 📖 阅读 [开发指南](development.md) 了解开发环境
- 📖 阅读 [API 参考](api-reference.md) 了解核心 API
