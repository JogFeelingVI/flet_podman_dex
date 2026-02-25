# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 04:20:46
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-25 03:05:46
from typing import Final
import random
import colorsys

_last_h = random.random()


class DraculaColors:
    """定义德古拉配色方案"""

    BACKGROUND: Final[str] = "#282a36"
    CURRENT_LINE: Final[str] = "#44475a"
    FOREGROUND: Final[str] = "#f8f8f2"
    COMMENT: Final[str] = "#6272a4"
    PURPLE: Final[str] = "#bd93f9"
    PINK: Final[str] = "#ff79c6"
    CYAN: Final[str] = "#8be9fd"
    GREEN: Final[str] = "#50fa7b"
    ORANGE: Final[str] = "#ffb86c"
    RED: Final[str] = "#ff5555"
    YELLOW: Final[str] = "#f1fa8c"
    CRADBG: Final[str] = "#1e293b"


def RandColor(mode="def", is_dark_theme=True):
    """
    针对移动端深色背景优化的颜色生成器
    is_dark_theme: 如果为 True，将确保颜色足够亮以在深色背景下显示
    """
    global _last_h
    _last_h = (_last_h + 0.618033988749895) % 1.0
    h = _last_h  # 色相 (0.0 - 1.0)

    # 根据色相调整初始亮度补偿
    # 蓝色 (0.55-0.7) 和紫色 (0.7-0.8) 需要更高的亮度补偿
    hue_step = 0.0
    if 0.5 <= h <= 0.85:  # 蓝色到紫色区间
        hue_step = 0.15
    elif h < 0.1 or h > 0.9:  # 红色区间
        hue_step = 0.05

    match mode:
        case "Morandi":
            s = random.uniform(0.25, 0.45)  # 稍微提高一点点饱和度下限
            # 深色模式下，Morandi 需要更高的亮度才能透出来
            l = random.uniform(0.65, 0.8) + hue_step
        case "Neon":
            s = random.uniform(0.8, 1.0)
            l = random.uniform(0.6, 0.75) + hue_step
        case "Glass":
            s = random.uniform(0.4, 0.6)
            l = random.uniform(0.7, 0.85) + hue_step
        case _:
            s = random.uniform(0.5, 0.9)
            l = random.uniform(0.6, 0.8) + hue_step

    # 最终约束：确保亮度不会超过 0.95 导致变白，也不会低于 0.6 导致看不清
    l = max(0.65 if is_dark_theme else 0.2, min(l, 0.95))

    # HLS 转换为 RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    return hex_color
