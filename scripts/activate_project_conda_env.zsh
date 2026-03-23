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

if ! command -v conda >/dev/null 2>&1; then
  echo "conda 未安装或不在 PATH 中。"
  return 1 2>/dev/null || exit 1
fi

if [[ ! -d "$PREFIX_ENV" ]]; then
  echo "未找到项目前缀环境: $PREFIX_ENV"
  echo "请先执行: source scripts/setup_project_conda_env.zsh"
  return 1 2>/dev/null || exit 1
fi

eval "$(conda shell.zsh hook)"

export CONDA_PKGS_DIRS="$PROJECT_CONDA_PKGS"
export PIP_CACHE_DIR="$PROJECT_PIP_CACHE"
export HF_HOME="$PROJECT_HF_CACHE"
export TRANSFORMERS_CACHE="$PROJECT_HF_CACHE"
export XDG_CACHE_HOME="$PROJECT_CACHE_ROOT"
export NLTK_DATA="$PROJECT_NLTK_DATA"

conda activate "$PREFIX_ENV"

echo "已激活 VideoLingo 项目前缀环境。"
echo "python: $(which python)"
} "$@"