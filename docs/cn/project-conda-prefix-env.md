# 项目内 Conda 前缀环境使用说明

> 适用于希望把 VideoLingo 的 Python 环境、下载缓存和模型缓存尽量放在项目所在磁盘，而不是默认写入用户主目录的用户。

## 常见误区

- 必须使用 `source scripts/setup_project_conda_env.zsh` 或 `source scripts/activate_project_conda_env.zsh`
- 不要直接执行 `./scripts/setup_project_conda_env.zsh`
- 初始化环境后，安装依赖仍然要运行 `python install.py`
- 重新打开终端后，需要重新执行激活脚本

## 这份文档解决什么问题

如果你的系统盘空间比较紧张，直接使用默认的 Conda 环境和默认缓存目录，通常会遇到这些问题：

- Conda 环境默认创建在用户目录下
- pip 下载缓存默认写到用户目录下
- Hugging Face 模型缓存默认写到用户目录下
- WhisperX、spaCy、Transformers 等依赖和模型会持续占用系统盘

本方案的目标是：

- 把 Python 环境放到项目目录下
- 把 Conda 包缓存放到项目目录下
- 把 pip 缓存放到项目目录下
- 把 Hugging Face 缓存放到项目目录下
- 后续每次进入项目时，使用方式尽量简单

## 推荐命令速查

如果你只想先知道怎么用，看这一节就够了。

### 第一次使用

```bash
cd /path/to/VideoLingo
source scripts/setup_project_conda_env.zsh
python install.py
```

### 以后每天使用

```bash
cd /path/to/VideoLingo
source scripts/activate_project_conda_env.zsh
```

### 需要重新安装依赖

```bash
python install.py
```

### 需要启动项目

```bash
streamlit run st.py
```

### 判断当前环境是否正确

```bash
which python
```

如果输出包含下面这个路径，说明你正在使用项目内环境：

```text
VideoLingo/.conda-env/bin/python
```

### 一句话记忆

- 第一次：`source scripts/setup_project_conda_env.zsh`
- 以后：`source scripts/activate_project_conda_env.zsh`
- 安装依赖：`python install.py`
- 启动项目：`streamlit run st.py`

## 目录结构

执行完成后，项目目录中会出现这些本地目录：

```text
VideoLingo/
├── .conda-env/        # 项目内 Python 环境
├── .conda-pkgs/       # 项目内 conda 包缓存
├── .cache/
│   ├── pip/           # 项目内 pip 缓存
│   └── huggingface/   # 项目内模型缓存
└── scripts/
    ├── setup_project_conda_env.zsh
    └── activate_project_conda_env.zsh
```

这些目录已经加入 [VideoLingo/.gitignore](../../.gitignore)，不会污染仓库提交。

## 两个脚本分别做什么

### 初始化脚本

脚本路径： [VideoLingo/scripts/setup_project_conda_env.zsh](../../scripts/setup_project_conda_env.zsh)

用途：首次配置项目内环境。

它会负责：

- 创建项目内 Conda 前缀环境
- 设置项目内缓存目录
- 激活该环境
- 可选迁移旧的 Hugging Face 缓存
- 可选清理旧的 conda 和 pip 缓存
- 可选直接运行 [VideoLingo/install.py](../../install.py)

### 激活脚本

脚本路径： [VideoLingo/scripts/activate_project_conda_env.zsh](../../scripts/activate_project_conda_env.zsh)

用途：后续日常使用。

它只做一件事：

- 重新设置缓存目录环境变量
- 激活项目内前缀环境

也就是说：

- 第一次用 `setup_project_conda_env.zsh`
- 以后日常进入项目用 `activate_project_conda_env.zsh`

## 首次使用

### 前置条件

开始前请确认：

- 已安装 Conda
- 当前 shell 是 zsh
- 已经进入 VideoLingo 项目根目录

```bash
cd /path/to/VideoLingo
```

### 推荐命令

第一次配置，直接执行：

```bash
source scripts/setup_project_conda_env.zsh
```

注意这里必须使用 `source`，不要直接执行：

```bash
./scripts/setup_project_conda_env.zsh
```

原因是直接执行会在子 shell 中激活环境，当前终端不会保留激活结果。

### 执行后你会看到什么

初始化脚本会依次处理：

1. 显示项目路径和缓存目录
2. 创建项目内环境 `.conda-env`
3. 激活环境
4. 显示当前 Python 版本
5. 询问是否迁移旧的 Hugging Face 缓存
6. 询问是否运行 `python install.py`
7. 询问是否清理旧的 conda 和 pip 缓存

如果你只是想先建环境，不想马上安装依赖，也完全可以在提示中选择跳过。

## 日常使用

以后每次重新打开终端，只需要进入项目目录后执行：

```bash
source scripts/activate_project_conda_env.zsh
```

执行成功后，脚本会输出当前使用的 Python 路径。

如果你看到的 Python 位于下面这个目录，说明环境已正确激活：

```text
VideoLingo/.conda-env/bin/python
```

## 如何安装 VideoLingo 依赖

激活项目环境后，正常执行：

```bash
python install.py
```

这个步骤仍然是 VideoLingo 官方的安装入口。项目内 Conda 前缀环境方案，只是改变环境和缓存的位置，不改变项目本身的安装逻辑。

## 最常用的两套操作

### 场景一：第一次安装

```bash
cd /path/to/VideoLingo
source scripts/setup_project_conda_env.zsh
python install.py
```

### 场景二：以后继续使用

```bash
cd /path/to/VideoLingo
source scripts/activate_project_conda_env.zsh
python install.py
```

如果依赖已经装好了，最后一步就换成你自己的启动命令，例如：

```bash
streamlit run st.py
```

## 脚本参数说明

初始化脚本支持参数，适合想减少交互的人。

```bash
source scripts/setup_project_conda_env.zsh [options]
```

可选参数如下：

| 参数 | 作用 |
| ---- | ---- |
| `--migrate-hf-cache` | 迁移旧的 Hugging Face 缓存到项目目录 |
| `--skip-migrate-hf-cache` | 跳过 Hugging Face 缓存迁移 |
| `--run-install` | 直接运行 `python install.py` |
| `--skip-install` | 跳过依赖安装 |
| `--clean-conda-cache` | 清理旧的 conda 下载缓存 |
| `--skip-clean-conda-cache` | 跳过清理 conda 缓存 |
| `--clean-pip-cache` | 清理旧的 pip 缓存 |
| `--skip-clean-pip-cache` | 跳过清理 pip 缓存 |
| `--delete-old-hf-cache` | 删除未迁移的旧 Hugging Face 缓存 |
| `--skip-delete-old-hf-cache` | 跳过删除旧 Hugging Face 缓存 |

例如，只创建环境和缓存目录，不做迁移、不做安装、不做清理：

```bash
source scripts/setup_project_conda_env.zsh \
  --skip-migrate-hf-cache \
  --skip-install \
  --skip-clean-conda-cache \
  --skip-clean-pip-cache \
  --skip-delete-old-hf-cache
```

## 缓存现在会写到哪里

激活环境后，以下缓存都会优先落到项目目录：

| 类型 | 位置 |
| ---- | ---- |
| Conda 包缓存 | `VideoLingo/.conda-pkgs` |
| pip 缓存 | `VideoLingo/.cache/pip` |
| Hugging Face 缓存 | `VideoLingo/.cache/huggingface` |
| Transformers 缓存 | `VideoLingo/.cache/huggingface` |
| NLTK 数据 | `VideoLingo/.cache/nltk_data` |
| XDG 缓存根目录 | `VideoLingo/.cache` |

这意味着以后重新下载模型时，主要占用的是项目所在磁盘，而不是系统盘。

## 如何确认当前真的在用项目内环境

执行：

```bash
which python
python --version
```

如果输出指向：

```text
.../VideoLingo/.conda-env/bin/python
```

说明环境正确。

还可以检查这些变量：

```bash
echo $CONDA_PKGS_DIRS
echo $PIP_CACHE_DIR
echo $HF_HOME
echo $TRANSFORMERS_CACHE
echo $XDG_CACHE_HOME
```

如果都指向项目目录，说明缓存配置也正确。

## 常见问题

### 为什么必须用 source

因为脚本内部调用了 `conda activate`。如果不用 `source`，激活结果不会保留在当前终端。

正确写法：

```bash
source scripts/setup_project_conda_env.zsh
source scripts/activate_project_conda_env.zsh
```

### 可以直接运行 `python install.py` 吗

可以，但前提是你已经先激活了项目内环境。

推荐顺序：

```bash
source scripts/activate_project_conda_env.zsh
python install.py
```

### 重新打开终端后还要重新执行吗

要。因为环境变量和 `conda activate` 只在当前 shell 会话内生效。

日常只需要执行这句：

```bash
source scripts/activate_project_conda_env.zsh
```

### 可以删除默认位置下旧的缓存吗

可以，但建议先确认当前项目环境能正常工作。

通常优先处理：

- 旧的 pip 缓存
- 旧的 conda 下载缓存
- 旧的 Hugging Face 缓存

如果你已经将 Hugging Face 缓存迁移到项目目录，并且旧路径已经是软链接，那么后续模型就不会继续写到系统盘。

### 这个方案会不会影响仓库提交

不会。本地环境目录已经加入 [VideoLingo/.gitignore](../../.gitignore)。

## 推荐使用习惯

为了最省心，建议固定使用这套流程：

### 第一次

```bash
cd /path/to/VideoLingo
source scripts/setup_project_conda_env.zsh
```

### 以后每次进入项目

```bash
cd /path/to/VideoLingo
source scripts/activate_project_conda_env.zsh
```

### 需要重新安装依赖时

```bash
python install.py
```

### 需要启动项目时

```bash
streamlit run st.py
```

## 一句话总结

如果你只记一条命令：

首次用：

```bash
source scripts/setup_project_conda_env.zsh
```

以后用：

```bash
source scripts/activate_project_conda_env.zsh
```

然后再执行：

```bash
python install.py
```
