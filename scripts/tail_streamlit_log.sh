#!/usr/bin/env zsh

set -euo pipefail

SCRIPT_PATH="${(%):-%N}"
PROJECT_ROOT="${SCRIPT_PATH:A:h:h}"
LOG_FILE="${STREAMLIT_LOG_FILE:-$PROJECT_ROOT/logs/streamlit-debug.log}"
LINES="${TAIL_LINES:-80}"

usage() {
	cat <<'EOF'
用法:
	zsh scripts/tail_streamlit_log.sh [--log-file logs/streamlit-debug.log] [--lines 80]

可选参数:
	--log-file, -f     要跟踪的日志文件，默认 logs/streamlit-debug.log
	--lines, -n        先显示最后多少行，再持续跟踪，默认 80
	--help, -h         显示帮助

也支持环境变量:
	STREAMLIT_LOG_FILE
	TAIL_LINES
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--log-file|-f)
			if [[ $# -lt 2 ]]; then
				echo "缺少参数: $1 需要一个日志文件路径。" >&2
				exit 1
			fi
			LOG_FILE="$2"
			shift 2
			;;
		--lines|-n)
			if [[ $# -lt 2 ]]; then
				echo "缺少参数: $1 需要一个行数值。" >&2
				exit 1
			fi
			LINES="$2"
			shift 2
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

if ! [[ "$LINES" =~ ^[0-9]+$ ]] || (( LINES < 1 )); then
	echo "无效行数: $LINES" >&2
	exit 1
fi

cd "$PROJECT_ROOT"

if [[ ! -f "$LOG_FILE" ]]; then
	echo "日志文件不存在: $LOG_FILE" >&2
	echo "请先运行: zsh scripts/start_streamlit.sh" >&2
	exit 1
fi

echo "跟踪日志文件: $LOG_FILE"
echo "先显示最后 $LINES 行，然后持续输出新日志。按 Ctrl+C 结束。"

exec tail -n "$LINES" -f "$LOG_FILE"