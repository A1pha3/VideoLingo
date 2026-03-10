# 视频源管理指南

> YouTube 下载与本地视频处理

## 学习目标

完成本教程后，你将能够：
- 从 YouTube 下载视频
- 处理会员视频
- 管理本地视频文件
- 解决下载问题

## YouTube 下载

### 基本下载

```python
from core import _1_ytdlp

# 下载视频
_1_ytdlp.download_video_ytdlp(
    url="https://www.youtube.com/watch?v=xxx",
    resolution="1080"
)
```

### 分辨率选项

| 选项 | 说明 |
|------|------|
| `360` | 360p（最快） |
| `1080` | 1080p（推荐） |
| `best` | 最高可用 |

### 配置下载

```yaml
# config.yaml
youtube:
  cookies_path: ''  # Cookies 文件路径（会员视频）
ytb_resolution: '1080'  # 默认分辨率
```

## 会员视频

### 使用 Cookies

1. **导出 Cookies**：

   **Chrome**:
   - 安装 "Get cookies.txt" 扩展
   - 访问 YouTube
   - 点击扩展，导出 cookies.txt

   **Firefox**:
   - 安装 "cookies.txt" 扩展
   - 同上

2. **配置路径**：

```yaml
youtube:
  cookies_path: '/path/to/cookies.txt'
```

### 验证 Cookies

```bash
# 测试下载
yt-dlp --cookies cookies.txt "https://www.youtube.com/watch?v=xxx"
```

## 本地视频

### 支持的格式

```
视频: mp4, mov, avi, mkv, flv, wmv, webm
音频: wav, mp3, flac, m4a, ogg
```

### 文件大小限制

建议：
- **小文件**: < 500MB，处理快速
- **中等文件**: 500MB - 2GB，正常处理
- **大文件**: > 2GB，需要更多时间和内存

### 文件命名

使用简洁的文件名（避免特殊字符）：

```
推荐: my_video.mp4
不推荐: 我的视频 (2024)!.mp4
```

## 批量下载

### 从播放列表

```bash
# 下载整个播放列表
yt-dlp -f "bestvideo[height<=1080]+bestaudio" \
  --cookies cookies.txt \
  --output "%(title)s.%(ext)s" \
  "https://www.youtube.com/playlist?list=xxx"
```

### 从文本文件

创建 `urls.txt`：
```
https://www.youtube.com/watch?v=abc123
https://www.youtube.com/watch?v=def456
```

下载：
```bash
yt-dlp -f "bestvideo[height<=1080]+bestaudio" \
  -a urls.txt \
  --cookies cookies.txt \
  --output "%(title)s.%(ext)s"
```

## 音频提取

### 直接提取音频

```bash
# 只下载音频（更快）
yt-dlp -x --audio-format mp3 \
  "https://www.youtube.com/watch?v=xxx"
```

### 视频 + 音频

```bash
# 下载并合并
yt-dlp -f "bestvideo[height<=1080]+bestaudio" \
  --merge-output-format mp4 \
  "https://www.youtube.com/watch?v=xxx"
```

## 常见问题

### Q: 下载速度慢？

**A**:

```bash
# 使用代理
yt-dlp --proxy http://127.0.0.1:7890 "URL"

# 限制速度（避免被封）
yt-dlp -r 1M "URL"
```

### Q: 视频地区限制？

**A**:

```bash
# 使用代理
yt-dlp --proxy http://proxy:port "URL"

# 或指定国家代码
yt-dlp --geo-bypass-country US "URL"
```

### Q: 下载失败？

**A**:

1. 更新 yt-dlp：`pip install --upgrade yt-dlp`
2. 检查网络连接
3. 尝试不同的格式：`-f "best"`

## 视频预处理

### 转换格式

```bash
# 转换为 MP4
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

### 调整分辨率

```bash
# 降分辨率
ffmpeg -i input_4k.mp4 -s 1920x1080 output_1080p.mp4
```

### 提取片段

```bash
# 提取 10-60 秒
ffmpeg -i input.mp4 -ss 00:00:10 -to 00:01:00 -c copy output.mp4
```

## 自测问题

处理不同视频来源时，尝试回答以下问题：

1. **YouTube 下载失败怎么办？**
   
   <details>
   <summary>点击查看答案</summary>
   1. 更新 yt-dlp：`pip install --upgrade yt-dlp`
   2. 使用 cookies 绕过登录限制：`cookiesfrombrowser: chrome`
   3. 检查视频是否有地区限制
   4. 尝试不同的分辨率选项
   </details>

2. **如何处理有背景音乐的视频？**
   
   <details>
   <summary>点击查看答案</summary>
   在配置中启用 `demucs: true`，会在转录前分离人声和背景音乐。这可以显著提高 WhisperX 的识别准确率，但处理时间会增加约 30%。
   </details>

3. **本地视频文件支持哪些格式？**
   
   <details>
   <summary>点击查看答案</summary>
   VideoLingo 支持 FFmpeg 能处理的所有格式，包括：mp4、mov、avi、mkv、flv、wmv、webm 等。音频文件也支持：wav、mp3、flac、m4a、ogg。
   </details>

## 下一步

- 📖 阅读 [批处理指南](batch-processing.md) 批量处理视频
- 📖 阅读 [故障排除](troubleshooting.md) 解决下载问题
