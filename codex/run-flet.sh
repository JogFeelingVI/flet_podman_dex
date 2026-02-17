#!/bin/bash
# @Author: JogFeelingVI
# @Date:   2026-01-01 08:45:26
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-17 11:07:07

flet run -d --web --port 45678 --ignore ".venv, __pycache__, build, storage, .ruff_cache, assets, storage" "$@"