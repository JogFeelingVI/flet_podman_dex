# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-30 10:54:49
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-04 23:59:50

from dataclasses import dataclass
from enum import Enum


class StatusEnum(str, Enum):
    IDLE = "idle"
    CALCULATING = "calculating"
    DONE = "done"
    TIMEOUT = "timeout"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class StatueData:
    status: StatusEnum
    elapsed_time: float


@dataclass
class HostMap:
    """
    服务器地址结构类
    Attributes:
        host (str): 服务器主机地址
        port (int): 服务器端口号
    address (str): 服务器完整地址，格式为 "http://{host}:{port}/sse"
    """

    host: str
    port: int

    @property
    def address(self):
        return f"http://{self.host}:{self.port}/sse"


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
        self.status = StatueData(StatusEnum.IDLE, 0.0)
        self.timeout = 60
        self.settings = dict()
        self.filters = []
        self.results = []
        self.elapsed_time = 0.0
        self.hostmap = HostMap(host="0.0.0.0", port=8000)
        self.logs = []  # 用于存储系统日志的列表

    @property
    def check_status(self):
        return self.status

    @property
    def server_address(self) -> str:
        return self.hostmap.address

    @property
    def get_last_100_lines_of_log(self) -> str:
        """获取系统日志的最后100行，返回为字符串格式"""
        return self.logs[-100:]

    def setting_host(self, host: str):
        self.hostmap.host = host
        self.logs.append(f"Host updated to {host}")

    def setting_port(self, port: int):
        self.hostmap.port = port
        self.logs.append(f"Port updated to {port}")

    def updatehostmap(self, hostmap: HostMap):
        self.hostmap = hostmap

    async def background_calculation_worker(self, name: str, timeout: int):
        # 这里是计算逻辑的占位符
        # 实际实现中会根据 self.settings 中的规则进行计算，并定期更新 self.status 和 self.elapsed_time
        self.logs.append(
            f"Started background calculation for {name} with timeout {timeout} seconds."
        )
        return


def main():
    print("Hello, World!")
    lm = LotteryManager()
    print(f"{lm.server_address['address']}")


if __name__ == "__main__":
    main()
