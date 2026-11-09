#!/bin/bash
# @Author: JogFeelingVI
# @Date:   2026-01-01 08:45:26
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-04 15:30:00

echo "=== 正在准备 Flet 运行环境 ==="

# 1. 强杀残留的 flet、应用子进程和 watchdog（main.py 子进程持有 uvicorn 端口，必须一起杀）
echo "清除后台残留的监听进程..."
pkill -f "flet run" 2>/dev/null
pkill -f "LoveTV/src/main.py" 2>/dev/null
pkill -f "watchdog" 2>/dev/null
sleep 1
pkill -9 -f "flet run" 2>/dev/null
pkill -9 -f "LoveTV/src/main.py" 2>/dev/null

# 2. 尝试提升当前 Pod/系统的 inotify 监听上限（如果权限允许）
if [ -w /proc/sys/fs/inotify/max_user_watches ]; then
    echo "正在临时调大内核 inotify 监视句柄上限..."
    echo 524288 > /proc/sys/fs/inotify/max_user_watches
    echo 512 > /proc/sys/fs/inotify/max_user_instances
else
    echo "[提示] 当前环境无权修改内核参数，将直接使用系统现有句柄池。"
fi

# 3. 运行标准的递归热载服务（通过 uv run 使用本项目的 .venv 环境）
cd "$(dirname "$0")"
export PYTHONPATH="$(dirname "$PWD"):$PYTHONPATH"
uv run flet run -d -r --web --host 0.0.0.0 --port 45678 --ignore-dirs .venv,__pycache__,build,storage,.ruff_cache,assets "$@"
