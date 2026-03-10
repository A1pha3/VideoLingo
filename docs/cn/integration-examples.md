# 集成示例

> VideoLingo 与其他系统集成的示例代码

## 学习目标

完成本教程后，你将能够：
- 将 VideoLingo 集成到 Python 应用
- 使用 API 调用核心功能
- 构建自动化工作流
- 部署为微服务

## Python 集成

### 基本集成

```python
#!/usr/bin/env python3
"""
VideoLingo 基本集成示例
"""

from core import _2_asr, _3_1_split_nlp, _4_2_translate
from core.utils import load_key, update_key

def translate_video(video_path: str, target_language: str = "简体中文"):
    """翻译视频的核心流程"""

    # 1. 设置目标语言
    update_key('target_language', target_language)

    # 2. 转录
    print("正在转录...")
    _2_asr.transcribe()

    # 3. 分割句子
    print("正在分割句子...")
    _3_1_split_nlp.split_by_spacy()

    # 4. 翻译
    print("正在翻译...")
    _4_2_translate.translate_all()

    print("翻译完成！")
    return True

# 使用
if __name__ == "__main__":
    translate_video("input.mp4", "日本語")
```

### 高级集成

```python
#!/usr/bin/env python3
"""
VideoLingo 高级集成 - 完整流程
"""

import os
from core import (
    _1_ytdlp, _2_asr,
    _3_1_split_nlp, _3_2_split_meaning,
    _4_1_summarize, _4_2_translate,
    _5_split_sub, _6_gen_sub, _7_sub_into_vid
)
from core.utils import load_key, update_key

class VideoLingoProcessor:
    """VideoLingo 处理器类"""

    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path

    def process_youtube(self, url: str, target_language: str):
        """处理 YouTube 视频"""

        # 下载视频
        print(f"下载视频: {url}")
        _1_ytdlp.download_video_ytdlp(url)

        # 设置目标语言
        update_key('target_language', target_language)

        # 完整处理流程
        return self.process_full()

    def process_local(self, video_path: str, target_language: str):
        """处理本地视频"""

        # 复制到 output 目录
        import shutil
        os.makedirs('output', exist_ok=True)
        shutil.copy(video_path, 'output/video.mp4')

        # 设置目标语言
        update_key('target_language', target_language)

        return self.process_full()

    def process_full(self):
        """完整处理流程（字幕 + 配音）"""

        steps = [
            ("转录", _2_asr.transcribe),
            ("NLP 分割", _3_1_split_nlp.split_by_spacy),
            ("语义分割", _3_2_split_meaning.split_sentences_by_meaning),
            ("摘要", _4_1_summarize.get_summary),
            ("翻译", _4_2_translate.translate_all),
            ("字幕分割", _5_split_sub.split_for_sub_main),
            ("生成字幕", _6_gen_sub.align_timestamp_main),
            ("烧录字幕", _7_sub_into_vid.merge_subtitles_to_video),
        ]

        for name, func in steps:
            print(f"正在执行: {name}...")
            try:
                func()
            except Exception as e:
                print(f"错误 ({name}): {e}")
                return False

        print("处理完成！")
        return True

# 使用示例
if __name__ == "__main__":
    processor = VideoLingoProcessor()

    # 处理 YouTube 视频
    processor.process_youtube(
        url="https://www.youtube.com/watch?v=xxx",
        target_language="简体中文"
    )
```

## API 服务

### FastAPI 封装

```python
#!/usr/bin/env python3
"""
VideoLingo REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os

app = FastAPI(title="VideoLingo API")

class TranslationRequest(BaseModel):
    video_url: str
    target_language: str
    enable_dubbing: bool = False

class TranslationStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int

# 任务存储
tasks = {}

@app.post("/api/translate", response_model=dict)
async def create_translation(request: TranslationRequest, background_tasks: BackgroundTasks):
    """创建翻译任务"""

    import uuid
    task_id = str(uuid.uuid4())

    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "request": request.dict()
    }

    # 后台处理
    background_tasks.add_task(process_video, task_id, request)

    return {"task_id": task_id}

@app.get("/api/status/{task_id}", response_model=TranslationStatus)
async def get_status(task_id: str):
    """获取任务状态"""

    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]

def process_video(task_id: str, request: TranslationRequest):
    """后台处理视频"""

    tasks[task_id]["status"] = "processing"

    try:
        # 调用 VideoLingo 处理
        processor = VideoLingoProcessor()
        processor.process_youtube(
            url=request.video_url,
            target_language=request.target_language
        )

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 工作流集成

### Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def process_video_task(**context):
    """Airflow 任务"""
    video_url = context['params']['video_url']
    target_language = context['params']['target_language']

    processor = VideoLingoProcessor()
    processor.process_youtube(video_url, target_language)

# DAG 定义
dag = DAG(
    'videolingo_translation',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# 任务
translate_task = PythonOperator(
    task_id='translate_video',
    python_callable=process_video_task,
    provide_context=True,
    op_kwargs={
        'params': {
            'video_url': 'https://www.youtube.com/watch?v=xxx',
            'target_language': '简体中文'
        }
    },
    dag=dag
)
```

### Prefect 流程

```python
from prefect import flow, task

@task
def download_video(url: str):
    from core import _1_ytdlp
    _1_ytdlp.download_video_ytdlp(url)
    return "output/video.mp4"

@task
def transcribe():
    from core import _2_asr
    _2_asr.transcribe()

@task
def translate(target_language: str):
    from core.utils import update_key
    from core import _4_2_translate
    update_key('target_language', target_language)
    _4_2_translate.translate_all()

@flow(name="Video Translation")
def video_translation_flow(url: str, target_language: str):
    """视频翻译流程"""

    download_video(url)
    transcribe()
    translate(target_language)

# 使用
video_translation_flow(
    url="https://www.youtube.com/watch?v=xxx",
    target_language="简体中文"
)
```

## CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/videolingo.yml
name: Video Translation

on:
  push:
    paths:
      - 'videos/**'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Process videos
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          python scripts/batch_translate.py
```

## Webhook 集成

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/videolingo', methods=['POST'])
def videolingo_webhook():
    """VideoLingo Webhook"""

    data = request.json

    # 验证请求
    if 'video_url' not in data:
        return jsonify({'error': 'Missing video_url'}), 400

    # 触发处理
    processor = VideoLingoProcessor()
    result = processor.process_youtube(
        url=data['video_url'],
        target_language=data.get('target_language', '简体中文')
    )

    return jsonify({
        'status': 'success' if result else 'failed'
    })

if __name__ == '__main__':
    app.run(port=5000)
```

## 消息队列集成

### Celery 任务

```python
from celery import Celery

celery_app = Celery(
    'videolingo',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task
def translate_video_task(video_url: str, target_language: str):
    """Celery 翻译任务"""

    processor = VideoLingoProcessor()
    return processor.process_youtube(
        url=video_url,
        target_language=target_language
    )

# 使用
result = translate_video_task.delay(
    video_url="https://www.youtube.com/watch?v=xxx",
    target_language="简体中文"
)
```

## 最佳实践

1. **错误处理**：捕获并记录所有异常
2. **进度回调**：向用户反馈处理进度
3. **资源清理**：处理完成后清理临时文件
4. **并发控制**：限制同时处理的任务数
5. **状态持久化**：保存任务状态到数据库

## 自测问题

完成集成开发后，尝试回答以下问题：

1. **如何在 API 服务中实现异步处理？**
   
   <details>
   <summary>点击查看答案</summary>
   使用后台任务（如 FastAPI 的 BackgroundTasks）或消息队列（如 Celery）。视频处理通常需要几分钟，不应阻塞 HTTP 请求。返回任务 ID，让客户端轮询状态。
   </details>

2. **如何确保处理失败时能够恢复？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 使用断点续传机制（检查中间文件是否存在）
   2. 将任务状态持久化到数据库
   3. 实现重试逻辑（如 Celery 的重试机制）
   4. 保存错误日志以便排查
   </details>

3. **如何限制并发处理数量？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 使用信号量（Semaphore）限制并发
   2. 配置 Celery 的并发 worker 数量
   3. 使用队列系统控制任务分发速率
   4. 监控 GPU 内存使用，动态调整并发数
   </details>

## 下一步

- 📖 阅读 [API 参考](api-reference.md) 了解核心 API
- 📖 阅读 [开发指南](development.md) 了解开发规范
