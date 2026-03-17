#!/usr/bin/env zsh

set -euo pipefail

SCRIPT_PATH="${(%):-%N}"
PROJECT_ROOT="${SCRIPT_PATH:A:h:h}"
PORT="${STREAMLIT_PORT:-8501}"
LOG_LEVEL="${STREAMLIT_LOG_LEVEL:-debug}"
LOG_FILE="${STREAMLIT_LOG_FILE:-$PROJECT_ROOT/logs/streamlit-debug.log}"
LOG_TO_FILE=1

usage() {
	cat <<'EOF'
用法:
	zsh scripts/start_streamlit.sh [--port 8501] [--log-level debug] [--log-file logs/streamlit-debug.log]

可选参数:
	--port, -p         Streamlit 监听端口，默认 8501
	--log-level, -l    日志级别，默认 debug
	--log-file, -f     日志文件路径，默认 logs/streamlit-debug.log
	--no-log-file      不写日志文件，只输出到当前终端
	--help, -h         显示帮助

也支持环境变量:
	STREAMLIT_PORT
	STREAMLIT_LOG_LEVEL
	STREAMLIT_LOG_FILE
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--port|-p)
			if [[ $# -lt 2 ]]; then
				echo "缺少参数: $1 需要一个端口值。" >&2
				exit 1
			fi
			PORT="$2"
			shift 2
			;;
		--log-level|-l)
			if [[ $# -lt 2 ]]; then
				echo "缺少参数: $1 需要一个日志级别。" >&2
				exit 1
			fi
			LOG_LEVEL="$2"
			shift 2
			;;
		--log-file|-f)
			if [[ $# -lt 2 ]]; then
				echo "缺少参数: $1 需要一个日志文件路径。" >&2
				exit 1
			fi
			LOG_FILE="$2"
			shift 2
			;;
		--no-log-file)
			LOG_TO_FILE=0
			shift
			;;
		--help|-h)
			usage
			exit 0
			;;
		*)
			echo "未知参数: $1" >&2
			usage >&2
			exit 1
			;;
	esac
done

if ! [[ "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1 || PORT > 65535 )); then
	echo "无效端口: $PORT" >&2
	exit 1
fi

cd "$PROJECT_ROOT"
source "$PROJECT_ROOT/scripts/activate_project_conda_env.zsh"

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
	echo "端口 $PORT 已被占用。请先停止占用进程，或改用其他端口。" >&2
	echo "示例: zsh scripts/start_streamlit.sh --port 8502" >&2
	exit 1
fi

if (( LOG_TO_FILE )); then
	mkdir -p "${LOG_FILE:h}"
	exec > >(python "$PROJECT_ROOT/scripts/redact_streamlit_output.py" | tee -a "$LOG_FILE") 2>&1
else
	exec > >(python "$PROJECT_ROOT/scripts/redact_streamlit_output.py") 2>&1
fi

echo "启动 Streamlit: port=$PORT log_level=$LOG_LEVEL"
if (( LOG_TO_FILE )); then
	echo "日志文件: $LOG_FILE"
else
	echo "日志文件: 已禁用，仅输出到当前终端"
fi

exec streamlit run st.py --server.headless true --server.port "$PORT" --logger.level "$LOG_LEVEL"
