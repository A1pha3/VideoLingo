# Docker 部署指南

> 使用 Docker 容器化部署 VideoLingo

## 学习目标

完成本教程后，你将能够：
- 构建 VideoLingo Docker 镜像
- 运行容器化实例
- 配置持久化存储
- 处理 GPU 加速

## 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| NVIDIA Driver | 550+ | 最新稳定版 |
| CUDA | 12.4+ | 12.6+ |
| GPU | compute capability 7.0+ | RTX 30 系列 / 40 系列 / 50 系列 |
| 内存 | 16 GB | 32 GB |
| 磁盘 | 30 GB 可用空间 | 50 GB SSD |

### 验证环境

```bash
# 检查 NVIDIA Driver
nvidia-smi

# 检查 Docker
docker --version

# 检查 NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu20.04 nvidia-smi
```

## 快速开始

### 方法一：使用预构建镜像

```bash
# 拉取镜像
docker pull rqlove/videolingo:latest

# 运行容器
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  rqlove/videolingo:latest
```

访问 http://localhost:8501

### 方法二：自行构建

```bash
# 克隆仓库
git clone https://github.com/Huanshere/VideoLingo.git
cd VideoLingo

# 构建镜像
docker build -t videolingo:latest .

# 运行容器
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  videolingo:latest
```

## 持久化配置

### 数据卷挂载

```bash
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/_model_cache:/app/_model_cache \
  videolingo:latest
```

**挂载说明**：

| 宿主机路径 | 容器路径 | 用途 |
|------------|----------|------|
| `./output` | `/app/output` | 输出文件持久化 |
| `./config.yaml` | `/app/config.yaml` | 配置文件 |
| `./_model_cache` | `/app/_model_cache` | 模型缓存（避免重复下载）|

### 完整部署示例

```bash
#!/bin/bash
# deploy.sh

# 创建目录结构
mkdir -p videolingo-data/{output,_model_cache,config}

# 复制配置文件
cp config.yaml videolingo-data/config/

# 运行容器
docker run -d \
  --name videolingo \
  --restart unless-stopped \
  -p 8501:8501 \
  --gpus all \
  -v $(pwd)/videolingo-data/output:/app/output \
  -v $(pwd)/videolingo-data/_model_cache:/app/_model_cache \
  -v $(pwd)/videolingo-data/config/config.yaml:/app/config.yaml \
  videolingo:latest

echo "VideoLingo 已启动，访问 http://localhost:8501"
```

## 高级配置

### GPU 选择

指定使用特定 GPU：

```bash
# 只使用 GPU 0
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus '"device=0"' \
  videolingo:latest

# 使用 GPU 0 和 1
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus '"device=0,1"' \
  videolingo:latest
```

### 内存限制

```bash
# 限制 GPU 内存
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  --shm-size=16g \
  videolingo:latest
```

### 环境变量

```bash
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  -e MAX_WORKERS=4 \
  -e DISPLAY_LANGUAGE=zh-CN \
  videolingo:latest
```

### 网络配置

```bash
# 使用自定义网络
docker network create videolingo-net

docker run -d \
  --name videolingo \
  --network videolingo-net \
  -p 8501:8501 \
  --gpus all \
  videolingo:latest
```

## 模型管理

### 预下载模型

避免容器首次运行时下载模型：

```bash
# 方法 1：挂载已有模型缓存
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  -v /path/to/existing/_model_cache:/app/_model_cache \
  videolingo:latest

# 方法 2：使用预下载的模型文件
# 从以下位置下载：
# - Google Drive: https://drive.google.com/file/d/10gPu6qqv92WbmIMo1iJCqQxhbd1ctyVw
# - 百度网盘: https://pan.baidu.com/s/1hZjqSGVn3z_WSg41-6hCqA?pwd=2kgs
```

### 模型缓存位置

```
_model_cache/
├── whisper/
│   ├── large-v3.pt
│   └── large-v3-turbo.pt
└── spacy/
    ├── en_core_web_md
    ├── zh_core_web_md
    └── ...
```

## 多实例部署

### 负载均衡

运行多个 VideoLingo 实例：

```bash
# 实例 1
docker run -d \
  --name videolingo-1 \
  -p 8501:8501 \
  --gpus '"device=0"' \
  -v $(pwd)/data1/output:/app/output \
  videolingo:latest

# 实例 2
docker run -d \
  --name videolingo-2 \
  -p 8502:8501 \
  --gpus '"device=1"' \
  -v $(pwd)/data2/output:/app/output \
  videolingo:latest
```

### Nginx 反向代理

```nginx
# /etc/nginx/conf.d/videolingo.conf

upstream videolingo {
    least_conn;
    server localhost:8501;
    server localhost:8502;
}

server {
    listen 80;
    server_name videolingo.example.com;

    location / {
        proxy_pass http://videolingo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streamlit WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 生产环境部署

### Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  videolingo:
    image: rqlove/videolingo:latest
    container_name: videolingo
    restart: unless-stopped
    ports:
      - "8501:8501"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    volumes:
      - ./output:/app/output
      - ./config.yaml:/app/config.yaml
      - ./_model_cache:/app/_model_cache
    environment:
      - MAX_WORKERS=4
      - DISPLAY_LANGUAGE=zh-CN
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

启动：

```bash
docker-compose up -d
```

### Kubernetes

```yaml
# videolingo-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: videolingo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: videolingo
  template:
    metadata:
      labels:
        app: videolingo
    spec:
      containers:
      - name: videolingo
        image: rqlove/videolingo:latest
        ports:
        - containerPort: 8501
        resources:
          limits:
            nvidia.com/gpu: 1
        volumeMounts:
        - name: output
          mountPath: /app/output
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
      volumes:
      - name: output
        persistentVolumeClaim:
          claimName: videolingo-output
      - name: config
        configMap:
          name: videolingo-config
---
apiVersion: v1
kind: Service
metadata:
  name: videolingo
spec:
  ports:
  - port: 8501
    targetPort: 8501
  selector:
    app: videolingo
  type: LoadBalancer
```

## 故障排除

### 容器无法启动

```bash
# 查看日志
docker logs videolingo

# 交互式调试
docker run -it --rm \
  --gpus all \
  videolingo:latest \
  /bin/bash
```

### GPU 不可用

```bash
# 检查 NVIDIA Container Toolkit
dpkg -l | grep nvidia-container-toolkit

# 重新安装
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update
apt-get install -y nvidia-container-toolkit
systemctl restart docker
```

### 内存不足

```bash
# 增加共享内存
docker run -d \
  --name videolingo \
  --shm-size=16g \
  --gpus all \
  videolingo:latest
```

### 端口冲突

```bash
# 使用不同端口
docker run -d \
  --name videolingo \
  -p 8080:8501 \
  --gpus all \
  videolingo:latest
```

## 维护

### 更新镜像

```bash
# 停止并删除旧容器
docker stop videolingo
docker rm videolingo

# 拉取最新镜像
docker pull rqlove/videolingo:latest

# 重新运行
docker run -d \
  --name videolingo \
  -p 8501:8501 \
  --gpus all \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/_model_cache:/app/_model_cache \
  rqlove/videolingo:latest
```

### 清理

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

### 监控

```bash
# 容器资源使用
docker stats videolingo

# 实时日志
docker logs -f videolingo

# 进入容器
docker exec -it videolingo /bin/bash
```

## 下一步

- 📖 阅读 [配置说明](configuration.md) 了解详细配置
- 📖 阅读 [批处理指南](batch-processing.md) 进行批量处理
