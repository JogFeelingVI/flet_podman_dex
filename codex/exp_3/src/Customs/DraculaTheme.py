# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 04:20:46
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-09 02:33:55
from typing import Final
import random
import colorsys


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


def RandColor():
    h = random.random()  # 色相 (Hue)
    s = random.uniform(0.4, 1.0)  # 饱和度 (Saturation)
    l = random.uniform(0.4, 0.8)  # 亮度 (Lightness)，避免过黑或过白

    # 2. HSL 转换为 RGB (colorsys 中使用 HLS，顺序略有不同)
    # 注意：colorsys.hls_to_rgb 接收的顺序是 (h, l, s)
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # 3. 将 0-1 范围的 RGB 转换为 0-255 并转为 Hex 格式
    hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    return hex_color
