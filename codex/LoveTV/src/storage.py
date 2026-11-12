# @Author: JogFeelingVI
# @Date:   2026-11-03 01:53:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 02:44:43
# @File    : storage.py
# @Time    : 2026/11/03 09:53:31
# @Author  : JogFeelingVI
# @Email   : glifelse@gmail.com
# @Desc    : 存储与读写用户数据

import json
import logging
from typing import Literal

from LoveTV.src.model.envpath import auth_path
from LoveTV.src.model.timezone import isoneweek, timestamp

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.storage")


# region 保存登录信息
def save_login(recode: dict) -> None:
    """
    recode = {'response_code': 200,
    'cookies': 'auth=%257B%2522',
    'base_url': 'http://host.containers.internal:3000',
    'username': 'moon',
    'password': '15972572759'
    }
    """
    recode["login_mode"] = timestamp()
    log.info(f"time stamp {recode['login_mode']}")
    with auth_path().open(mode="w", encoding="utf-8") as wfs:
        json.dump(recode, wfs, indent=4, ensure_ascii=False)


# endregion


# region 获取登录状态
def login_state() -> dict:
    try:
        with auth_path().open(mode="r", encoding="utf-8") as rfs:
            config = json.load(rfs)
        # 使用 bool() 确保强制转换为布尔类型，同时利用 .get() 防止 Key数量不对或为 None
        login_mode = float(config.get("login_mode"))
        recode = {"login_mode": isoneweek(login_mode), "user": config.get("username")}
        return recode
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        log.info(f"ERROR {timestamp()}")
        return {"login_mode": False, "user": ""}


# endregion


# region 获取登录凭证
def load_auth_config(
    retype: Literal["t", "d"] = "t",
) -> tuple[str, str] | dict[str, str]:
    """加载并获取认证配置信息（基础 URL 与 Cookies）.

    Args:
        retype: 返回格式，"t" 为元组，"d" 为字典。
    """
    try:
        with auth_path().open(mode="r", encoding="utf-8") as rfs:
            config = json.load(rfs)

        base_url = config.get("base_url")
        cookies = config.get("cookies")

        if not base_url or not cookies:
            return ()

        match retype.lower():
            case "t":
                return (base_url, cookies)
            case "d":
                return {"base_url": base_url, "cookies": cookies}
            case _:
                return ()

    except (FileNotFoundError, json.JSONDecodeError):
        return ()


# endregion
