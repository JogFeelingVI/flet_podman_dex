# @File    : envpath.py
# @Time    : 2026/11/04 20:00:59
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 处理路径

import os
from pathlib import Path

DATA_PATH = Path(os.getenv("FLET_APP_STORAGE_DATA", "./data"))
TEMP_PATH = Path(os.getenv("FLET_APP_STORAGE_TEMP", "./temp"))
CACHE_PATH = Path(os.getenv("FLET_APP_STORAGE_CACHE", "./cache"))


def auth_path() -> Path:
    """
    用户auth登录信息
    """
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    return DATA_PATH / "auth_config.json"


def app_cache_path() -> Path:
    """
    设置全局缓冲目录
    """
    path = CACHE_PATH / "covers"
    path.mkdir(parents=True, exist_ok=True)
    return path
