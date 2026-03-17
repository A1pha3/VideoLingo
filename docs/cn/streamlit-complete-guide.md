# VideoLingo Streamlit 完全指南

> 从入门到精通：构建专业级视频处理 Web 界面

## 学习目标

完成本指南后，你将能够：

- **新手**：理解 Streamlit 核心概念，启动并定制 VideoLingo Web 界面
- **进阶**：掌握组件开发、状态管理和性能优化技巧
- **专家**：设计复杂交互、扩展组件库、部署生产环境

---

## 第一章：Streamlit 是什么

### 1.1 核心定位

Streamlit 是一个**纯 Python** 的 Web 应用框架，让你用数据科学的思维方式构建交互式界面。

**为什么 VideoLingo 选择 Streamlit？**

| 特性 | 传统 Web 开发 | Streamlit |
|------|--------------|-----------|
| 技术栈 | HTML + CSS + JS + 后端框架 | 纯 Python |
| 学习曲线 | 陡峭（需掌握多种技术） | 平缓（Python 开发者友好） |
| 开发速度 | 慢（需前后端联调） | 快（即时预览） |
| 数据集成 | 复杂（API 对接） | 原生支持（Pandas、Matplotlib 等） |
| 适用场景 | 大型复杂应用 | 数据应用、原型、内部工具 |

### 1.2 工作原理

```
你的 Python 脚本
      ↓
Streamlit 运行时（Tornado 服务器）
      ↓
浏览器（WebSocket 实时通信）
```

**关键特性**：每次用户交互，Streamlit 会**重新执行整个脚本**，通过 session state 保持状态。

### 1.3 VideoLingo 中的角色

在 VideoLingo 中，Streamlit 负责：

1. **视频输入**：YouTube 链接下载 / 本地上传
2. **参数配置**：侧边栏设置面板（语言、API 密钥、模型选择）
3. **进度展示**：转录、翻译、配音的实时进度
4. **结果预览**：字幕视频、配音视频的在线播放
5. **文件导出**：字幕文件打包下载

---

## 第二章：5 分钟快速上手

### 2.1 环境准备

确保已完成 VideoLingo 安装：

```bash
# 进入项目目录
cd VideoLingo

# 激活虚拟环境（如果使用 conda）
conda activate videolingo

# 或使用 uv
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows
```

### 2.2 启动 Web 界面

```bash
streamlit run st.py
```

启动成功后，你会看到：

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

浏览器会自动打开，界面分为三个主要区域：

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  VideoLingo                                      │
│  欢迎使用...                                             │
├──────────────┬──────────────────────────────────────────┤
│              │  a. 下载视频                              │
│   侧边栏     │  ┌─────────────────────────────────────┐ │
│   (设置)     │  │  YouTube 链接输入框                  │ │
│              │  │  [下载视频] 按钮                     │ │
│  - 语言设置  │  └─────────────────────────────────────┘ │
│  - API 配置  │                                          │
│  - 模型选择  │  b. 翻译和生成字幕                        │
│              │  ┌─────────────────────────────────────┐ │
│              │  │  处理步骤说明...                     │ │
│              │  │  [开始处理字幕] 按钮                 │ │
│              │  └─────────────────────────────────────┘ │
│              │                                          │
│              │  c. 配音                                  │
│              │  ┌─────────────────────────────────────┐ │
│              │  │  配音步骤说明...                     │ │
│              │  │  [开始音频处理] 按钮                 │ │
│              │  └─────────────────────────────────────┘ │
└──────────────┴──────────────────────────────────────────┘
```

### 2.3 第一个定制：修改页面标题

打开 `st.py`，找到第 11 行：

```python
st.set_page_config(page_title="VideoLingo", page_icon="docs/logo.svg")
```

修改为：

```python
st.set_page_config(
    page_title="我的视频翻译工具",
    page_icon="🎬",
    layout="wide"  # 宽屏布局
)
```

保存后，**无需重启**，浏览器会自动刷新！

---

## 第三章：核心概念详解

### 3.1 页面配置

```python
import streamlit as st

st.set_page_config(
    page_title="页面标题",           # 浏览器标签页标题
    page_icon="🚀",                 # 图标（emoji 或图片路径）
    layout="centered",              # 布局：centered（居中）或 wide（宽屏）
    initial_sidebar_state="expanded" # 侧边栏默认状态
)
```

### 3.2 文本显示

```python
import streamlit as st

# 标题层级（类似 HTML h1-h6）
st.title("一级标题")        # 最大标题
st.header("二级标题")       # 章节标题
st.subheader("三级标题")    # 小节标题

# 普通文本
st.text("固定宽度文本")
st.write("灵活文本（自动识别 Markdown）")
st.markdown("**粗体** 和 *斜体*")

# 代码显示
st.code("print('Hello')", language="python")

# 特殊文本
st.success("成功消息 ✓")
st.info("提示信息 ℹ️")
st.warning("警告 ⚠️")
st.error("错误 ✗")
```

### 3.3 数据展示

```python
import streamlit as st
import pandas as pd
import numpy as np

# DataFrame
df = pd.DataFrame({
    '列A': [1, 2, 3],
    '列B': ['a', 'b', 'c']
})
st.dataframe(df)  # 交互式表格
st.table(df)      # 静态表格

# JSON
st.json({"key": "value", "list": [1, 2, 3]})

# 图表（支持多种库）
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)
st.line_chart(chart_data)
st.bar_chart(chart_data)
```

### 3.4 用户输入

```python
import streamlit as st

# 文本输入
name = st.text_input("你的名字", placeholder="请输入...")

# 多行文本
desc = st.text_area("描述", height=100)

# 数字
age = st.number_input("年龄", min_value=0, max_value=150, value=25)

# 滑块
level = st.slider("水平", 0, 100, 50)

# 单选
color = st.radio("选择颜色", ["红", "绿", "蓝"])

# 下拉选择
option = st.selectbox("选择选项", ["A", "B", "C"])

# 多选
options = st.multiselect("多选", ["选项1", "选项2", "选项3"])

# 复选框
agree = st.checkbox("我同意条款")

# 文件上传
uploaded_file = st.file_uploader("上传文件", type=["csv", "txt"])
```

### 3.5 按钮与交互

```python
import streamlit as st

# 普通按钮
if st.button("点击我"):
    st.write("按钮被点击了！")

# 带图标的按钮
if st.button("🚀 启动", type="primary"):
    st.success("启动成功！")

# 下载按钮
data = "这是文件内容"
st.download_button(
    label="下载文件",
    data=data,
    file_name="example.txt",
    mime="text/plain"
)
```

### 3.6 布局控制

```python
import streamlit as st

# 侧边栏
with st.sidebar:
    st.header("设置")
    option = st.selectbox("选项", ["A", "B"])

# 分栏布局（2 列）
col1, col2 = st.columns(2)
with col1:
    st.write("左侧内容")
with col2:
    st.write("右侧内容")

# 比例分栏
col1, col2, col3 = st.columns([1, 2, 1])  # 1:2:1 比例

# 标签页
tab1, tab2 = st.tabs(["标签1", "标签2"])
with tab1:
    st.write("标签1内容")
with tab2:
    st.write("标签2内容")

# 可折叠区域
with st.expander("高级选项"):
    st.write("隐藏的内容")

# 带边框的容器
with st.container(border=True):
    st.write("容器内的内容")
```

### 3.7 媒体展示

```python
import streamlit as st

# 图片
st.image("path/to/image.png", caption="图片说明")

# 视频
st.video("path/to/video.mp4")
st.video("https://youtube.com/watch?v=xxx")  # 支持 URL

# 音频
st.audio("path/to/audio.mp3")
```

### 3.8 状态与反馈

```python
import streamlit as st
import time

# 进度条
progress_bar = st.progress(0)
for i in range(100):
    time.sleep(0.1)
    progress_bar.progress(i + 1)

# 加载状态
with st.spinner("处理中..."):
    time.sleep(2)
st.success("完成！")

# 气球动画（庆祝）
st.balloons()

# 雪花动画
st.snow()

# 状态容器
with st.status("正在处理...", expanded=True) as status:
    st.write("步骤 1：下载...")
    time.sleep(1)
    st.write("步骤 2：处理...")
    time.sleep(1)
    status.update(label="处理完成！", state="complete")
```

---

## 第四章：VideoLingo 实战

### 4.1 项目结构解析

```
VideoLingo/
├── st.py                           # Streamlit 主入口
├── core/
│   └── st_utils/                   # Streamlit 工具模块
│       ├── __init__.py
│       ├── imports_and_utils.py    # 通用工具、样式
│       ├── sidebar_setting.py      # 侧边栏设置
│       └── download_video_section.py # 视频下载区域
├── translations/                   # 国际化
│   ├── translations.py
│   ├── en.json
│   └── zh-CN.json
└── .streamlit/
    └── config.toml                 # Streamlit 配置
```

### 4.2 主入口 st.py 解析

```python
import streamlit as st
import os, sys
from core.st_utils.imports_and_utils import *
from core import *

# 设置页面配置（必须在最前面）
st.set_page_config(page_title="VideoLingo", page_icon="docs/logo.svg")

# 定义输出文件路径
SUB_VIDEO = "output/output_sub.mp4"
DUB_VIDEO = "output/output_dub.mp4"

def text_processing_section():
    """字幕处理区域"""
    st.header(t("b. Translate and Generate Subtitles"))
    
    with st.container(border=True):
        # 步骤说明
        st.markdown(f"""
        <p style='font-size: 20px;'>
        {t("This stage includes the following steps:")}
        <p style='font-size: 20px;'>
            1. {t("WhisperX word-level transcription")}<br>
            2. {t("Sentence segmentation using NLP and LLM")}<br>
            ...
        """, unsafe_allow_html=True)

        # 根据文件存在性控制流程
        if not os.path.exists(SUB_VIDEO):
            if st.button(t("Start Processing Subtitles")):
                process_text()
                st.rerun()  # 重新运行脚本刷新界面
        else:
            st.video(SUB_VIDEO)
            download_subtitle_zip_button(text=t("Download All Srt Files"))

def process_text():
    """实际处理逻辑"""
    with st.spinner(t("Using Whisper for transcription...")):
        _2_asr.transcribe()
    with st.spinner(t("Splitting long sentences...")):
        _3_1_split_nlp.split_by_spacy()
    # ... 更多步骤
    st.success(t("Subtitle processing complete! 🎉"))
    st.balloons()

def main():
    # Logo 和欢迎语
    logo_col, _ = st.columns([1, 1])
    with logo_col:
        st.image("docs/logo.png", width="stretch")
    
    # 侧边栏
    with st.sidebar:
        page_setting()  # 设置面板
        st.markdown(give_star_button, unsafe_allow_html=True)
    
    # 主内容区
    download_video_section()
    text_processing_section()
    audio_processing_section()

if __name__ == "__main__":
    main()
```

### 4.3 侧边栏设置开发

`core/st_utils/sidebar_setting.py`：

```python
import streamlit as st
from core.utils import load_key, update_key
from translations.translations import translate as t

def page_setting():
    """侧边栏设置面板"""
    st.header(t("Settings"))
    
    # 语言选择
    language_setting()
    
    # API 设置
    with st.expander(t("API Settings"), expanded=True):
        api_key = st.text_input(
            t("LLM API Key"),
            value=load_key("api_key"),
            type="password"  # 密码输入，隐藏内容
        )
        update_key("api_key", api_key)
    
    # Whisper 设置
    with st.expander(t("Whisper Settings")):
        whisper_mode = st.radio(
            t("Whisper Mode"),
            ["local", "cloud"],
            index=0 if load_key("whisper_mode") == "local" else 1
        )
        update_key("whisper_mode", whisper_mode)

def language_setting():
    """语言设置"""
    lang = st.selectbox(
        t("Language"),
        ["🇬🇧 English", "🇨🇳 简体中文"],
        index=0 if load_key("language") == "en" else 1
    )
    update_key("language", "en" if "English" in lang else "zh-CN")
```

### 4.4 添加新功能模块

**步骤 1**：创建新模块文件 `core/st_utils/my_feature.py`

```python
import streamlit as st
from translations.translations import translate as t
from core.utils import load_key, update_key

def my_feature_section():
    """我的新功能区域"""
    st.header(t("d. My New Feature"))
    
    with st.container(border=True):
        st.markdown(t("Feature description..."))
        
        # 功能参数
        param1 = st.slider(t("Parameter 1"), 0, 100, 50)
        param2 = st.selectbox(t("Parameter 2"), ["Option A", "Option B"])
        
        # 保存设置
        update_key("my_feature.param1", param1)
        update_key("my_feature.param2", param2)
        
        # 执行按钮
        if st.button(t("Start Processing"), type="primary"):
            with st.spinner(t("Processing...")):
                result = process_my_feature(param1, param2)
            st.success(t("Complete!"))
            st.write(result)

def process_my_feature(param1, param2):
    """实际处理逻辑"""
    # 实现你的功能
    return f"Processed with {param1} and {param2}"
```

**步骤 2**：在 `st.py` 中引入

```python
from core.st_utils.my_feature import my_feature_section

def main():
    # ... 原有代码
    download_video_section()
    text_processing_section()
    audio_processing_section()
    my_feature_section()  # 添加新模块
```

---

## 第五章：状态管理与缓存

### 5.1 Session State

Streamlit 每次交互都会重新执行脚本，使用 `st.session_state` 保存状态：

```python
import streamlit as st

# 初始化状态
if "counter" not in st.session_state:
    st.session_state.counter = 0
    st.session_state.user_name = ""

# 读取状态
st.write(f"计数：{st.session_state.counter}")

# 修改状态
if st.button("增加"):
    st.session_state.counter += 1
    st.rerun()  # 重新运行以更新界面

# 文本输入绑定到状态
st.session_state.user_name = st.text_input(
    "用户名",
    value=st.session_state.user_name
)
```

### 5.2 回调函数

```python
import streamlit as st

def on_button_click():
    st.session_state.clicked = True
    st.session_state.message = "按钮被点击了！"

st.button("点击我", on_click=on_button_click)

if st.session_state.get("clicked", False):
    st.success(st.session_state.message)
```

### 5.3 数据缓存

使用装饰器缓存 expensive 操作：

```python
import streamlit as st
import pandas as pd

@st.cache_data  # 缓存数据
def load_data(url):
    """加载数据（只执行一次，后续从缓存读取）"""
    df = pd.read_csv(url)
    return df

@st.cache_resource  # 缓存资源（如模型）
def load_model():
    """加载机器学习模型"""
    from transformers import pipeline
    return pipeline("sentiment-analysis")

# 使用
data = load_data("https://example.com/data.csv")
model = load_model()
```

**缓存策略对比**：

| 装饰器 | 用途 | 适用场景 |
|--------|------|----------|
| `@st.cache_data` | 缓存数据（DataFrame、列表等） | 数据加载、预处理 |
| `@st.cache_resource` | 缓存资源（模型、数据库连接） | ML 模型、API 客户端 |

---

## 第六章：样式定制

### 6.1 自定义 CSS

在 `st.py` 或工具模块中添加：

```python
import streamlit as st

# 自定义 CSS
custom_css = """
<style>
    /* 主标题 */
    h1 {
        color: #1f77b4;
        font-size: 3rem;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    
    /* 信息框 */
    .stAlert {
        border-radius: 10px;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
```

### 6.2 主题配置

创建 `.streamlit/config.toml`：

```toml
[theme]
primaryColor = "#4CAF50"           # 主色（按钮、链接）
backgroundColor = "#ffffff"        # 背景色
secondaryBackgroundColor = "#f0f2f6"  # 次要背景（侧边栏）
textColor = "#262730"              # 文字颜色
font = "sans serif"                # 字体：sans serif / serif / monospace

[server]
headless = true
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false  # 禁用使用统计
```

### 6.3 响应式设计

```python
import streamlit as st

# 检测屏幕宽度（近似）
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.write("小屏幕布局")
with col2:
    st.write("中屏幕布局")
with col3:
    st.write("大屏幕布局")

# 更好的做法：使用自适应布局
with st.container():
    cols = st.columns([1, 2, 1])  # 比例布局
    # 内容会自动适应
```

---

## 第七章：性能优化

### 7.1 优化原则

| 问题 | 解决方案 |
|------|----------|
| 页面加载慢 | 使用 `@st.cache_data` 缓存数据 |
| 重复计算 | 将计算移到函数外或使用缓存 |
| 大量数据展示 | 使用分页或虚拟滚动 |
| 文件上传慢 | 限制文件大小，显示进度条 |

### 7.2 实际优化案例

```python
import streamlit as st
import pandas as pd

# ❌ 不好的做法：每次交互都重新加载
data = pd.read_csv("large_file.csv")  # 100MB 文件
st.dataframe(data)

# ✅ 好的做法：缓存数据加载
@st.cache_data
def load_large_data():
    return pd.read_csv("large_file.csv")

data = load_large_data()
st.dataframe(data)

# ✅ 更好的做法：分页显示
@st.cache_data
def load_data_chunk(offset, limit):
    return pd.read_csv("large_file.csv", skiprows=range(1, offset), nrows=limit)

page = st.number_input("页码", min_value=1, value=1)
page_size = 100
data = load_data_chunk((page - 1) * page_size + 1, page_size)
st.dataframe(data)
```

### 7.3 异步处理

对于长时间任务，考虑使用后台处理：

```python
import streamlit as st
import threading
import queue

# 创建任务队列
task_queue = queue.Queue()
result_queue = queue.Queue()

def background_worker():
    """后台工作线程"""
    while True:
        task = task_queue.get()
        if task is None:
            break
        result = process_task(task)
        result_queue.put(result)

# 启动后台线程
worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()

# UI
if st.button("提交任务"):
    task_queue.put("task_data")
    st.info("任务已提交，后台处理中...")

# 检查结果
if not result_queue.empty():
    result = result_queue.get()
    st.success(f"任务完成：{result}")
```

---

## 第八章：调试与故障排除

### 8.1 调试技巧

```bash
# 启用调试模式
streamlit run st.py --logger.level debug

# 指定端口
streamlit run st.py --server.port 8080

# 禁用自动重载（生产环境）
streamlit run st.py --server.runOnSave false
```

### 8.2 常见问题

**问题 1**：页面空白或加载失败

```python
# 检查：确保 st.set_page_config 在最前面
import streamlit as st

st.set_page_config(page_title="App")  # ✅ 正确

# 其他导入和代码...
```

**问题 2**：状态丢失

```python
# 检查：正确使用 session_state
if "key" not in st.session_state:  # ✅ 先检查是否存在
    st.session_state.key = "value"
```

**问题 3**：缓存不更新

```python
# 清除缓存按钮
if st.button("清除缓存"):
    st.cache_data.clear()
    st.rerun()
```

**问题 4**：CSS 不生效

```python
# 确保使用 unsafe_allow_html=True
st.markdown("<style>...</style>", unsafe_allow_html=True)  # ✅
```

### 8.3 日志记录

```python
import streamlit as st
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process():
    logger.info("开始处理...")
    try:
        # 处理逻辑
        logger.info("处理完成")
    except Exception as e:
        logger.error(f"处理失败：{e}")
        st.error(f"处理失败：{e}")
```

---

## 第九章：部署与生产化

### 9.1 本地部署

```bash
# 使用生产级服务器
pip install streamlit

# 启动（后台运行）
nohup streamlit run st.py --server.port 8501 > streamlit.log 2>&1 &

# 或使用 systemd 管理服务
```

### 9.2 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "st.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# 构建和运行
docker build -t videolingo .
docker run -p 8501:8501 videolingo
```

### 9.3 反向代理配置（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9.4 安全最佳实践

```python
import streamlit as st
import os

# 1. 敏感信息使用环境变量
api_key = os.environ.get("API_KEY", "")

# 2. 密码输入使用 type="password"
password = st.text_input("密码", type="password")

# 3. 文件上传限制类型和大小
uploaded_file = st.file_uploader(
    "上传文件",
    type=["mp4", "mov"],
    help="最大 500MB"
)

# 4. 输入验证
user_input = st.text_input("输入")
if user_input:
    if len(user_input) > 1000:
        st.error("输入过长")
    elif not user_input.isalnum():
        st.error("只能包含字母和数字")
```

---

## 第十章：进阶技巧

### 10.1 自定义组件

使用 `st.components` 集成第三方库：

```python
import streamlit as st
import streamlit.components.v1 as components

# 嵌入 HTML/JS
components.html("""
    <div id="chart"></div>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        Plotly.newPlot('chart', [{
            x: [1, 2, 3],
            y: [1, 2, 3],
            type: 'scatter'
        }]);
    </script>
""")

# 嵌入 iframe
components.iframe("https://example.com", height=500)
```

### 10.2 多页面应用

Streamlit 1.28+ 支持原生多页面：

```
pages/
├── 1_📊_数据分析.py
├── 2_📝_文本处理.py
└── 3_⚙️_设置.py
```

```python
# pages/1_📊_数据分析.py
import streamlit as st

st.set_page_config(page_title="数据分析")
st.title("数据分析页面")
```

### 10.3 表单批量处理

```python
import streamlit as st

with st.form("my_form"):
    st.write("批量处理表单")
    
    col1, col2 = st.columns(2)
    with col1:
        param1 = st.number_input("参数1")
    with col2:
        param2 = st.number_input("参数2")
    
    # 表单提交按钮
    submitted = st.form_submit_button("提交")
    
    if submitted:
        st.write(f"处理结果：{param1 + param2}")
```

### 10.4 动态图表

```python
import streamlit as st
import numpy as np
import time

# 实时更新的图表
chart = st.line_chart(np.random.randn(10, 2))

for i in range(100):
    new_data = np.random.randn(1, 2)
    chart.add_rows(new_data)
    time.sleep(0.1)
```

---

## 第十一章：VideoLingo 定制实战

### 11.1 添加自定义主题

修改 `core/st_utils/imports_and_utils.py`：

```python
import streamlit as st

# 深色主题
dark_theme = """
<style>
    .main {
        background-color: #1a1a2e;
        color: #eee;
    }
    
    h1, h2, h3 {
        color: #16213e;
    }
    
    .stButton > button {
        background-color: #0f3460;
        color: white;
    }
    
    [data-testid="stSidebar"] {
        background-color: #16213e;
    }
</style>
"""

def apply_theme(theme_name="default"):
    """应用主题"""
    if theme_name == "dark":
        st.markdown(dark_theme, unsafe_allow_html=True)
```

### 11.2 添加批量处理功能

```python
# core/st_utils/batch_processing.py
import streamlit as st
import os
from pathlib import Path

def batch_processing_section():
    """批量处理区域"""
    st.header("批量处理")
    
    # 文件夹选择
    input_dir = st.text_input("输入文件夹路径", value="./batch_input")
    output_dir = st.text_input("输出文件夹路径", value="./batch_output")
    
    if st.button("开始批量处理"):
        video_files = list(Path(input_dir).glob("*.mp4"))
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, video_file in enumerate(video_files):
            status_text.text(f"处理 {video_file.name}... ({i+1}/{len(video_files)})")
            
            # 处理单个视频
            process_single_video(video_file, output_dir)
            
            progress_bar.progress((i + 1) / len(video_files))
        
        st.success(f"完成！处理了 {len(video_files)} 个视频")

def process_single_video(input_path, output_dir):
    """处理单个视频"""
    # 实现处理逻辑
    pass
```

### 11.3 添加处理历史记录

```python
import streamlit as st
import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = "output/history.json"

def load_history():
    """加载处理历史"""
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(record):
    """保存处理记录"""
    history = load_history()
    history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def history_section():
    """历史记录区域"""
    st.header("处理历史")
    
    history = load_history()
    
    if not history:
        st.info("暂无处理记录")
        return
    
    for record in reversed(history[-10:]):  # 显示最近 10 条
        with st.expander(f"{record['time']} - {record['video_name']}"):
            st.write(f"状态：{record['status']}")
            st.write(f"输出：{record['output_path']}")
```

---

## 第十二章：最佳实践总结

### 12.1 代码组织

```
✅ 推荐结构
st.py                    # 主入口，保持简洁
pages/                   # 多页面（如需要）
core/st_utils/
    ├── __init__.py
    ├── base.py          # 基础组件
    ├── settings.py      # 设置面板
    ├── video_section.py # 视频处理区域
    └── utils.py         # 工具函数

❌ 避免
st.py                    # 2000+ 行的巨型文件
```

### 12.2 性能清单

- [ ] 使用 `@st.cache_data` 缓存数据加载
- [ ] 使用 `@st.cache_resource` 缓存模型
- [ ] 大数据集使用分页或采样
- [ ] 长时间任务显示进度条
- [ ] 避免不必要的 `st.rerun()`

### 12.3 用户体验清单

- [ ] 页面加载时显示加载状态
- [ ] 长时间操作提供取消选项
- [ ] 错误信息清晰友好
- [ ] 成功操作给予反馈（success/toast）
- [ ] 表单提供默认值和占位符

### 12.4 代码质量清单

- [ ] 函数添加 docstring
- [ ] 复杂逻辑添加注释
- [ ] 敏感信息使用环境变量
- [ ] 用户输入进行验证
- [ ] 异常使用 try-except 捕获

---

## 附录 A：Streamlit API 速查表

### 显示元素

| 函数 | 用途 |
|------|------|
| `st.title()` | 页面标题 |
| `st.header()` | 章节标题 |
| `st.subheader()` | 小节标题 |
| `st.text()` | 纯文本 |
| `st.write()` | 灵活文本（自动识别类型） |
| `st.markdown()` | Markdown 文本 |
| `st.code()` | 代码块 |
| `st.latex()` | LaTeX 公式 |

### 数据展示

| 函数 | 用途 |
|------|------|
| `st.dataframe()` | 交互式表格 |
| `st.table()` | 静态表格 |
| `st.json()` | JSON 数据 |
| `st.metric()` | 指标卡片 |
| `st.line_chart()` | 折线图 |
| `st.bar_chart()` | 柱状图 |
| `st.map()` | 地图 |

### 输入组件

| 函数 | 用途 |
|------|------|
| `st.button()` | 按钮 |
| `st.text_input()` | 单行文本 |
| `st.text_area()` | 多行文本 |
| `st.number_input()` | 数字输入 |
| `st.slider()` | 滑块 |
| `st.selectbox()` | 下拉选择 |
| `st.multiselect()` | 多选 |
| `st.radio()` | 单选 |
| `st.checkbox()` | 复选框 |
| `st.file_uploader()` | 文件上传 |
| `st.date_input()` | 日期选择 |
| `st.time_input()` | 时间选择 |
| `st.color_picker()` | 颜色选择 |

### 布局

| 函数 | 用途 |
|------|------|
| `st.sidebar` | 侧边栏 |
| `st.columns()` | 分栏布局 |
| `st.tabs()` | 标签页 |
| `st.expander()` | 可折叠区域 |
| `st.container()` | 容器 |
| `st.empty()` | 占位符 |

### 状态与反馈

| 函数 | 用途 |
|------|------|
| `st.progress()` | 进度条 |
| `st.spinner()` | 加载状态 |
| `st.success()` | 成功消息 |
| `st.info()` | 提示信息 |
| `st.warning()` | 警告 |
| `st.error()` | 错误 |
| `st.exception()` | 异常详情 |
| `st.balloons()` | 气球动画 |
| `st.snow()` | 雪花动画 |
| `st.toast()` | 轻提示 |

### 媒体

| 函数 | 用途 |
|------|------|
| `st.image()` | 图片 |
| `st.audio()` | 音频 |
| `st.video()` | 视频 |

### 高级

| 函数/装饰器 | 用途 |
|-------------|------|
| `@st.cache_data` | 数据缓存 |
| `@st.cache_resource` | 资源缓存 |
| `st.session_state` | 状态管理 |
| `st.rerun()` | 重新运行 |
| `st.stop()` | 停止执行 |
| `st.form()` | 表单 |
| `st.form_submit_button()` | 表单提交 |
| `st.set_page_config()` | 页面配置 |

---

## 附录 B：学习资源

### 官方资源

- [Streamlit 官方文档](https://docs.streamlit.io/)
- [Streamlit API 参考](https://docs.streamlit.io/library/api-reference)
- [Streamlit Gallery](https://streamlit.io/gallery)

### 社区资源

- [Streamlit 论坛](https://discuss.streamlit.io/)
- [Awesome Streamlit](https://github.com/MarcSkovMadsen/awesome-streamlit)

### VideoLingo 相关

- [VideoLingo GitHub](https://github.com/Huanshere/VideoLingo)
- [VideoLingo 文档](docs/)

---

## 自测问题

完成本指南后，尝试回答以下问题：

### 基础问题

1. **Streamlit 每次用户交互时会发生什么？**
   <details>
   <summary>点击查看答案</summary>
   Streamlit 会重新执行整个 Python 脚本。这就是为什么需要使用 `st.session_state` 来保持状态。
   </details>

2. **如何缓存数据避免重复加载？**
   <details>
   <summary>点击查看答案</summary>
   使用 `@st.cache_data` 装饰器装饰数据加载函数。对于模型等资源，使用 `@st.cache_resource`。
   </details>

3. **如何修改 Streamlit 的主题颜色？**
   <details>
   <summary>点击查看答案</summary>
   创建 `.streamlit/config.toml` 文件，在 `[theme]` 部分配置颜色。
   </details>

### 进阶问题

4. **如何在 VideoLingo 中添加一个新的处理区域？**
   <details>
   <summary>点击查看答案</summary>
   1. 在 `core/st_utils/` 创建新模块
   2. 实现处理函数和 UI 函数
   3. 在 `st.py` 中导入并调用
   4. 在翻译文件中添加对应的翻译键
   </details>

5. **如何处理长时间运行的任务？**
   <details>
   <summary>点击查看答案</summary>
   使用 `st.progress()` 显示进度，`st.spinner()` 显示加载状态。对于超长时间任务，考虑使用后台线程或队列。
   </details>

---

## 结语

本指南从 Streamlit 基础概念出发，逐步深入到 VideoLingo 的实战应用，涵盖了：

- **新手**：快速上手，理解核心概念
- **进阶**：组件开发、状态管理、性能优化
- **专家**：自定义主题、批量处理、生产部署

Streamlit 的强大之处在于**简单**——用纯 Python 就能构建专业级 Web 界面。希望本指南能帮助你更好地理解和定制 VideoLingo 的 Web 界面！

---

*文档版本：1.0*  
*最后更新：2024 年*  
*适用 VideoLingo 版本：v1.x*
