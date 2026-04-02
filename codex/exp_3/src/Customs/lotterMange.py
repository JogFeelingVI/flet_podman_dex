# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-30 10:54:49
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-02 12:38:40

import flet as ft
import asyncio

STATUE = ["idle", "calculating", "done", "timeout", "error"]
HOST = "0.0.0.0"
PORT = 8000

# region Lotter_Data
Lotter_Data = {
    "🔴双色球": {
        "description": "🇨🇳百万富翁缔造者",
        "PA": [1, 33],
        "PB": [1, 16],
        "PA_K": 6,
        "PB_K": 1,
    },
    "⚪快乐8": {
        "description": "🇨🇳你的快乐就是他的快乐",
        "PA": [1, 80],
        "PA_K": 10,
    },
    "✨超级大乐透": {
        "description": "🇨🇳体育大乐透",
        "PA": [1, 35],
        "PB": [1, 12],
        "PA_K": 5,
        "PB_K": 2,
    },
    "🇨🇳排列3/5": {
        "description": "🇨🇳体育排列3/5",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
    },
    "✨七星彩": {
        "description": "🇨🇳体育七星彩",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PF": [0, 9],
        "PG": [0, 14],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
        "PF_K": 1,
        "PG_K": 1,
    },
    "🇺🇸Powerball": {
        "description": "🇺🇸USA Powerball",
        "PA": [1, 69],
        "PB": [1, 26],
        "PA_K": 5,
        "PB_K": 1,
    },
    "🇹🇼威力彩": {
        "description": "🇺🇸台湾省销售最好的彩票",
        "PA": [1, 38],
        "PB": [1, 8],
        "PA_K": 6,
        "PB_K": 1,
    },
}
# endregion


class LotteryManager:
    def __init__(self):
        self.calc_task_running = False
        self.status = "idle"
        self.timeout = 60
        self.settings = dict()
        self.filters = []
        self.results = []
        self.elapsed_time = 0.0

    @property
    def check_status(self):
        return self.status

    @property
    def server_address(self):
        host_map = {"address": f"http://{HOST}:{PORT}/sse", "host": HOST, "port": PORT}
        return host_map
    
    def setting_host(self, host: str):
        global HOST
        HOST = host
        
    def setting_port(self, port: int):
        global PORT
        PORT = port


def get_supported_lotteries() -> str:
    """
    获取系统支持的所有彩票类型、描述以及它们的规则（球的范围和抽取个数）。
    当用户询问可以计算哪些彩票，或者想了解特定彩票的玩法时，调用此工具。
    同时支持告知用户可以自定义彩票参数。
    """
    summary = ["### 当前支持的预设彩票类型:"]

    for name, info in Lotter_Data.items():
        desc = info.get("description", "无描述")
        rules = []

        # 1. 自动提取所有符合规则的键 (例如 PA, PB, SA, SB 等)
        # 逻辑：如果键 K 的值是长度为 2 的列表，且存在 K_K，则它是一个球组定义
        # 我们对键进行排序，以保证显示顺序是 A, B, C...
        potential_keys = sorted([k for k in info.keys() if not k.endswith("_K")])

        for key in potential_keys:
            count_key = f"{key}_K"
            if (
                count_key in info
                and isinstance(info[key], list)
                and len(info[key]) == 2
            ):
                r_min, r_max = info[key]
                count = info[count_key]

                # 美化显示：去除 P/S 前缀，保留 A, B, C...
                # 如果 key 是 "PA"，显示 "A组"；如果是 "Custom"，就显示 "Custom组"
                group_name = key[1:] if len(key) > 1 and key[0] in ("P", "S") else key
                rules.append(f"{group_name}组: {r_min}-{r_max} 选 {count} 个")

        rule_str = ", ".join(rules)
        summary.append(f"- **{name}**: {desc}\n  *规则: {rule_str}*")

    summary.append("\n### 自定义能力:")
    summary.append(
        "你可以提供任意数量的球组。只需为每组定义范围 `[min, max]` 和抽取个数 `K`."
    )
    return "\n".join(summary)


def main():
    print("Hello, World!")
    lm = LotteryManager()
    markdown = get_supported_lotteries()
    print(markdown)
    print(f"{lm.server_address['address']}")


if __name__ == "__main__":
    main()
