# 安全最佳实践

> VideoLingo 安全配置与数据处理指南

## 学习目标

完成本教程后，你将能够：
- 安全管理 API 密钥
- 保护敏感数据
- 配置安全的生产环境
- 遵循数据隐私最佳实践

## API 密钥管理

### 环境变量（推荐）

使用环境变量存储敏感信息：

```bash
# ~/.bashrc 或 ~/.zshrc
export OPENAI_API_KEY="your-api-key"
export AZURE_API_KEY="your-api-key"
export VIDEO_LINGO_API_KEY="your-api-key"
```

```python
# config.yaml
api:
  key: '${OPENAI_API_KEY}'  # 从环境变量读取
```

### 密钥文件

创建单独的密钥文件（不提交到 Git）：

```bash
# secrets/keys.sh
export OPENAI_API_KEY="your-api-key"
export AZURE_API_KEY="your-api-key"
```

```bash
# 运行前加载
source secrets/keys.sh
streamlit run st.py
```

### .env 文件

使用 `.env` 文件（添加到 `.gitignore`）：

```bash
# .env
OPENAI_API_KEY=your-api-key
AZURE_API_KEY=your-api-key
```

```python
# 安装 python-dotenv
pip install python-dotenv

# 在代码中加载
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
```

### 密钥轮换

定期轮换 API 密钥：

```bash
# 1. 在 API 提供商处生成新密钥
# 2. 更新环境变量
export OPENAI_API_KEY="new-api-key"

# 3. 验证新密钥
python -c "from core.utils import check_api; print(check_api())"

# 4. 撤销旧密钥
```

## Git 安全

### .gitignore 配置

确保敏感文件不被提交：

```gitignore
# .gitignore

# API 密钥
.env
secrets/
*.key
*_api_key.txt

# 输出文件（可能包含敏感信息）
output/
batch/output/

# 配置文件（包含密钥）
config.yaml

# 模型缓存
_model_cache/

# 日志
*.log
output/gpt_log/
```

### 配置模板

提供配置模板而非实际配置：

```bash
# config.yaml.template
api:
  key: 'your-api-key-here'  # 替换为实际密钥
  base_url: 'https://api.openai.com'
  model: 'gpt-4.1'
```

```bash
# 使用脚本生成实际配置
cp config.yaml.template config.yaml
# 编辑 config.yaml 填入实际密钥
```

### 提交前检查

```bash
# 检查是否包含敏感信息
git diff --cached | grep -i "api.*key"

# 搜索可能的密钥
grep -r "sk-" . --include="*.py" --include="*.yaml"
grep -r "password" . --include="*.py" --include="*.yaml"
```

## 数据隐私

### 输入数据处理

**敏感视频**：处理包含敏感信息的视频时：

1. **本地处理**：不要上传到云服务
2. **禁用云 API**：使用本地 WhisperX 和 Ollama
3. **清理输出**：处理完成后删除敏感文件

```yaml
# config.yaml - 本地处理配置
whisper:
  runtime: 'local'  # 本地转录

api:
  base_url: 'http://localhost:11434/v1'  # 本地 LLM
```

### 输出文件管理

**自动清理**：

```python
# 处理完成后自动归档和清理
from core.utils.onekeycleanup import cleanup

# 归档到 history/ 并清理 output/
cleanup(target_dir="history/sensitive_data")
```

**手动清理**：

```bash
# 删除输出
rm -rf output/

# 删除日志（可能包含原文内容）
rm -rf output/log/

# 删除音频文件
rm -rf output/audio/
```

### 日志安全

LLM 调用日志包含原文内容：

```bash
# 日志位置
output/gpt_log/
├── default.json     # 包含完整的 prompt 和响应
├── translate.json   # 包含翻译内容
└── error.json       # 错误日志
```

**保护措施**：

1. **限制日志权限**：

```bash
chmod 600 output/gpt_log/*.json
```

2. **禁用日志**（不推荐）：

```python
# 修改 core/utils/ask_gpt.py
def ask_gpt(prompt, resp_type=None, valid_def=None, log_title="default"):
    # ... 不调用 _save_cache
    pass
```

3. **加密日志**：

```python
from cryptography.fernet import Fernet

# 加密日志
key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(json.dumps(log).encode())
```

## 网络安全

### API 通信

**HTTPS 强制**：

```python
# 验证使用 HTTPS
base_url = load_key("api.base_url")
if not base_url.startswith("https://"):
    raise ValueError("必须使用 HTTPS")
```

**证书验证**：

```python
import requests

# 验证 SSL 证书
response = requests.get(url, verify=True)

# 指定 CA 证书
response = requests.get(url, verify='/path/to/cacert.pem')
```

### 代理配置

```bash
# 设置代理
export https_proxy=http://proxy.example.com:8080
export http_proxy=http://proxy.example.com:8080

# 或在代码中
import os
os.environ['https_proxy'] = 'http://proxy.example.com:8080'
```

### Docker 网络隔离

```yaml
# docker-compose.yml
services:
  videolingo:
    networks:
      - internal
    # 不暴露外部端口，使用反向代理
    expose:
      - "8501"

networks:
  internal:
    driver: bridge
```

## 访问控制

### Streamlit 认证

添加基础认证：

```python
# st.py
import streamlit as st
import hashlib

def check_password():
    """简单的密码验证"""
    def password_entered():
        if st.session_state["password"] == hashlib.sha256("your-password".encode()).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 不存储密码
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        return False

    return st.session_state["password_correct"]

if not check_password():
    st.stop()

# 主应用代码
```

### 文件权限

```bash
# 限制配置文件权限
chmod 600 config.yaml

# 限制输出目录权限
chmod 700 output/

# 限制密钥文件权限
chmod 600 secrets/
```

## 生产环境安全

### 部署检查清单

- [ ] 所有 API 密钥使用环境变量
- [ ] config.yaml 不包含实际密钥
- [ ] 启用 HTTPS/TLS
- [ ] 配置访问控制
- [ ] 限制日志访问权限
- [ ] 定期更新依赖
- [ ] 配置资源限制
- [ ] 启用审计日志

### 依赖安全

```bash
# 检查已知漏洞
pip install safety
safety check

# 更新依赖
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# 自动安全更新
pip install pip-audit
pip-audit --fix
```

### 容器安全

```dockerfile
# Dockerfile
FROM python:3.10-slim

# 使用非 root 用户
RUN useradd -m -u 1000 videolingo
USER videolingo

# 最小化安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY --chown=videolingo:videolingo . .

# 限制权限
USER videolingo
```

```bash
# 扫描镜像漏洞
docker scan videolingo:latest
```

## 数据处理合规

### GDPR 合规

处理欧盟用户数据时：

1. **数据最小化**：只收集必要数据
2. **用户同意**：明确告知数据处理方式
3. **删除权**：提供删除数据的机制
4. **数据导出**：允许用户导出他们的数据

### 示例：同意流程

```python
# st.py
import streamlit as st

if "consent" not in st.session_state:
    st.warning("""
    ## 数据处理同意

    本服务将处理您的视频数据：
    - 上传的视频将发送到转录服务
    - 翻译内容由第三方 LLM 处理
    - 处理完成后数据将自动删除

    是否同意？
    """)

    col1, col2 = st.columns(2)
    if col1.button("同意"):
        st.session_state["consent"] = True
        st.rerun()
    if col2.button("拒绝"):
        st.error("需要同意才能使用服务")
        st.stop()
```

## 安全审计

### 审计日志

```python
import logging
from datetime import datetime

audit_log = logging.getLogger("audit")

def log_action(action, details):
    """记录安全相关事件"""
    audit_log.info({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": st.session_state.get("user_id", "anonymous")
    })

# 使用示例
log_action("video_upload", {"filename": video.name, "size": video.size})
log_action("api_call", {"model": "gpt-4", "tokens": 1000})
```

### 安全检查脚本

```bash
#!/bin/bash
# security-check.sh

echo "执行安全检查..."

# 检查配置文件权限
if [ $(stat -c %a config.yaml) != "600" ]; then
    echo "警告：config.yaml 权限不安全"
fi

# 检查是否有 API 密钥被提交
if git log --all --full-history --source -- "*api*key*" | grep -q "sk-"; then
    echo "警告：Git 历史中可能包含 API 密钥"
fi

# 检查依赖漏洞
pip-audit

echo "检查完成"
```

## 应急响应

### 密钥泄露处理

如果 API 密钥泄露：

1. **立即撤销**：在 API 提供商处撤销密钥
2. **生成新密钥**：创建新的 API 密钥
3. **更新配置**：更新所有使用该密钥的配置
4. **检查日志**：审查是否有异常使用
5. **轮换密钥**：建立定期密钥轮换机制

### 数据泄露处理

如果敏感数据泄露：

1. **隔离系统**：停止受影响的服务
2. **评估影响**：确定泄露范围
3. **通知用户**：按照法规要求通知
4. **清理数据**：删除已泄露的数据
5. **修复漏洞**：修复导致泄露的漏洞
6. **加固防护**：增强安全措施

## 最佳实践清单

### 开发环境

- [ ] 使用本地 API 密钥，不提交到 Git
- [ ] 确保 `.gitignore` 正确配置
- [ ] 使用虚拟环境隔离依赖
- [ ] 定期更新依赖

### 生产环境

- [ ] 所有密钥使用环境变量
- [ ] 启用 HTTPS/TLS
- [ ] 配置访问控制
- [ ] 限制日志访问
- [ ] 定期备份
- [ ] 监控异常活动
- [ ] 制定应急响应计划

## 下一步

- 📖 阅读 [配置说明](configuration.md) 了解配置管理
- 📖 阅读 [部署指南](docker-deployment.md) 了解生产部署
