#!/bin/bash
# @Author: JogFeelingVI
# @Date:   2026-01-01 08:45:26
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-01 08:54:21

flet run -d --web --port 56789 --ignore ".venv, __pycache__, build, storage, .ruff_cache, assets, storage" "$@"