#!/bin/bash
# @Author: JogFeelingVI
# @Date:   2026-01-01 08:45:26
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-04 15:30:00
#!/bin/bash
echo "=== 正在准备 Flet 运行环境 ==="

# 1. 更精准地按端口和进程树清理残留（直接杀掉占用 45678 端口的进程及其子进程）
echo "清除后台残留进程..."
fuser -k 45678/tcp 2>/dev/null || pkill -9 -f "flet" 2>/dev/null
sleep 0.5

# 2. 跳过 uv 的环境校验包装层，直接调用 .venv 里的二进制文件（省去 uv 包装进程内存）
cd "$(dirname "$0")"
export PYTHONPATH="$(dirname "$PWD"):$PYTHONPATH"
export PYTHONMALLOC=malloc  # 防止 Python 长期运行热重载后内存碎片只增不减

# 3. 补全 --ignore-dirs 中的 .git 和缓存目录，减少 watchdog 内存占用
exec .venv/bin/flet run -d -r \
  --web \
  --host 0.0.0.0 \
  --port 45678 \
  --ignore-dirs .git,.venv,__pycache__,build,storage,.ruff_cache,.mypy_cache,.pytest_cache,assets,model,control \
  "$@"

