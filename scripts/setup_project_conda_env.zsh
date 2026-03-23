#!/usr/bin/env zsh

() {
emulate -L zsh
setopt errexit nounset pipefail

SCRIPT_PATH="${(%):-%x}"
PROJECT_ROOT="${SCRIPT_PATH:A:h:h}"
PREFIX_ENV="$PROJECT_ROOT/.conda-env"
PROJECT_CACHE_ROOT="$PROJECT_ROOT/.cache"
PROJECT_CONDA_PKGS="$PROJECT_ROOT/.conda-pkgs"
PROJECT_PIP_CACHE="$PROJECT_CACHE_ROOT/pip"
PROJECT_HF_CACHE="$PROJECT_CACHE_ROOT/huggingface"
PROJECT_NLTK_DATA="$PROJECT_CACHE_ROOT/nltk_data"
OLD_HF_CACHE="$HOME/.cache/huggingface"
OLD_PIP_CACHE="$HOME/Library/Caches/pip"
OLD_NLTK_DATA="$HOME/nltk_data"
IS_SOURCED=0
MIGRATE_HF_CACHE="ask"
RUN_INSTALL="ask"
CLEAN_CONDA_CACHE="ask"
CLEAN_PIP_CACHE="ask"
DELETE_OLD_HF_CACHE="ask"

if [[ "${ZSH_EVAL_CONTEXT:-}" == *:file ]]; then
  IS_SOURCED=1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --migrate-hf-cache)
      MIGRATE_HF_CACHE="yes"
      ;;
    --skip-migrate-hf-cache)
      MIGRATE_HF_CACHE="no"
      ;;
    --run-install)
      RUN_INSTALL="yes"
      ;;
    --skip-install)
      RUN_INSTALL="no"
      ;;
    --clean-conda-cache)
      CLEAN_CONDA_CACHE="yes"
      ;;
    --skip-clean-conda-cache)
      CLEAN_CONDA_CACHE="no"
      ;;
    --clean-pip-cache)
      CLEAN_PIP_CACHE="yes"
      ;;
    --skip-clean-pip-cache)
      CLEAN_PIP_CACHE="no"
      ;;
    --delete-old-hf-cache)
      DELETE_OLD_HF_CACHE="yes"
      ;;
    --skip-delete-old-hf-cache)
      DELETE_OLD_HF_CACHE="no"
      ;;
    --help|-h)
      echo "用法: source scripts/setup_project_conda_env.zsh [options]"
      echo "  --migrate-hf-cache | --skip-migrate-hf-cache"
      echo "  --run-install | --skip-install"
      echo "  --clean-conda-cache | --skip-clean-conda-cache"
      echo "  --clean-pip-cache | --skip-clean-pip-cache"
      echo "  --delete-old-hf-cache | --skip-delete-old-hf-cache"
      return 0 2>/dev/null || exit 0
      ;;
    *)
      echo "未知参数: $1"
      return 1 2>/dev/null || exit 1
      ;;
  esac
  shift
done

if ! command -v conda >/dev/null 2>&1; then
  echo "conda 未安装或不在 PATH 中。"
  return 1 2>/dev/null || exit 1
fi

eval "$(conda shell.zsh hook)"

mkdir -p "$PROJECT_CACHE_ROOT" "$PROJECT_CONDA_PKGS" "$PROJECT_PIP_CACHE" "$PROJECT_HF_CACHE"
mkdir -p "$PROJECT_NLTK_DATA"

export CONDA_PKGS_DIRS="$PROJECT_CONDA_PKGS"
export PIP_CACHE_DIR="$PROJECT_PIP_CACHE"
export HF_HOME="$PROJECT_HF_CACHE"
export TRANSFORMERS_CACHE="$PROJECT_HF_CACHE"
export XDG_CACHE_HOME="$PROJECT_CACHE_ROOT"
export NLTK_DATA="$PROJECT_NLTK_DATA"

confirm() {
  local prompt="$1"
  local answer

  read -r "answer?$prompt [y/N]: "
  [[ "$answer:l" == "y" || "$answer:l" == "yes" ]]
}

should_run() {
  local mode="$1"
  local prompt="$2"

  if [[ "$mode" == "yes" ]]; then
    return 0
  fi

  if [[ "$mode" == "no" ]]; then
    return 1
  fi

  confirm "$prompt"
}

print_section() {
  echo
  echo "== $1 =="
}

print_section "项目路径"
echo "$PROJECT_ROOT"

print_section "将使用的目录"
echo "CONDA_PKGS_DIRS=$CONDA_PKGS_DIRS"
echo "PIP_CACHE_DIR=$PIP_CACHE_DIR"
echo "HF_HOME=$HF_HOME"
echo "PREFIX_ENV=$PREFIX_ENV"

if [[ ! -d "$PREFIX_ENV" ]]; then
  print_section "创建项目内 conda 前缀环境"
  conda create --prefix "$PREFIX_ENV" python=3.10 -y
else
  print_section "检测到已存在的项目前缀环境"
  echo "$PREFIX_ENV"
fi

print_section "激活项目前缀环境"
conda activate "$PREFIX_ENV"

print_section "当前 Python"
which python
python --version

if [[ -d "$OLD_HF_CACHE" && ! -L "$OLD_HF_CACHE" ]]; then
  print_section "迁移 Hugging Face 缓存"
  echo "发现旧缓存: $OLD_HF_CACHE"
  echo "目标目录: $PROJECT_HF_CACHE"

  if should_run "$MIGRATE_HF_CACHE" "是否将旧 Hugging Face 缓存迁移到项目目录，并在原位置创建软链接？"; then
    mkdir -p "${OLD_HF_CACHE:h}"

    if [[ -n "$(ls -A "$PROJECT_HF_CACHE" 2>/dev/null)" ]]; then
      timestamp="$(date +%Y%m%d_%H%M%S)"
      mv "$PROJECT_HF_CACHE" "${PROJECT_HF_CACHE}_backup_$timestamp"
      mkdir -p "$PROJECT_HF_CACHE"
      echo "目标目录已有内容，已备份到 ${PROJECT_HF_CACHE}_backup_$timestamp"
    else
      rmdir "$PROJECT_HF_CACHE" 2>/dev/null || true
    fi

    mv "$OLD_HF_CACHE" "$PROJECT_HF_CACHE"
    ln -s "$PROJECT_HF_CACHE" "$OLD_HF_CACHE"
    echo "已迁移并建立软链接。"
  fi
fi

if [[ -d "$OLD_NLTK_DATA" && ! -L "$OLD_NLTK_DATA" && "$OLD_NLTK_DATA" != "$PROJECT_NLTK_DATA" ]]; then
  print_section "迁移 NLTK 数据目录"
  echo "发现旧目录: $OLD_NLTK_DATA"
  echo "目标目录: $PROJECT_NLTK_DATA"

  if [[ -z "$(ls -A "$PROJECT_NLTK_DATA" 2>/dev/null)" ]]; then
    rmdir "$PROJECT_NLTK_DATA" 2>/dev/null || true
    mv "$OLD_NLTK_DATA" "$PROJECT_NLTK_DATA"
    ln -s "$PROJECT_NLTK_DATA" "$OLD_NLTK_DATA"
    echo "已迁移并建立软链接。"
  else
    echo "目标目录已有内容，跳过自动迁移。"
  fi
fi

print_section "升级基础打包工具"
python -m pip install --upgrade pip setuptools wheel

if should_run "$RUN_INSTALL" "是否现在运行 python install.py 安装 VideoLingo 依赖？"; then
  print_section "运行安装脚本"
  python "$PROJECT_ROOT/install.py"
fi

if should_run "$CLEAN_CONDA_CACHE" "是否清理小盘上的 conda 下载缓存？"; then
  print_section "清理 conda 缓存"
  conda clean -a -y
fi

if [[ -d "$OLD_PIP_CACHE" ]]; then
  if should_run "$CLEAN_PIP_CACHE" "是否清理小盘上的 pip 缓存（$OLD_PIP_CACHE）？"; then
    print_section "清理 pip 缓存"
    PIP_CACHE_DIR="$OLD_PIP_CACHE" python -m pip cache purge
  fi
fi

if [[ -d "$OLD_HF_CACHE" && ! -L "$OLD_HF_CACHE" ]]; then
  if should_run "$DELETE_OLD_HF_CACHE" "是否直接删除小盘上的旧 Hugging Face 缓存（未迁移部分）？"; then
    print_section "删除旧 Hugging Face 缓存"
    rm -rf "$OLD_HF_CACHE"
  fi
fi

print_section "完成"
if (( IS_SOURCED )); then
  echo "当前会话已激活项目前缀环境。"
else
  echo "脚本已执行完成。由于这次是直接执行而不是 source，环境激活不会保留到当前 shell。"
  echo "如果你希望当前终端直接进入该环境，请改用："
  echo "  source scripts/setup_project_conda_env.zsh"
fi
echo "以后进入项目后，可执行："
echo "  export CONDA_PKGS_DIRS=$PROJECT_CONDA_PKGS"
echo "  export PIP_CACHE_DIR=$PROJECT_PIP_CACHE"
echo "  export HF_HOME=$PROJECT_HF_CACHE"
echo "  export TRANSFORMERS_CACHE=$PROJECT_HF_CACHE"
echo "  export XDG_CACHE_HOME=$PROJECT_CACHE_ROOT"
echo "  export NLTK_DATA=$PROJECT_NLTK_DATA"
echo "  conda activate $PREFIX_ENV"
} "$@"