# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 04:20:46
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-10 01:56:11

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


def RandColor(mode="def", is_dark_theme=True, hue=None):
    """
    针对移动端深色背景优化的颜色生成器
    :param mode: 颜色风格 (Morandi, Neon, Glass, def)
    :param is_dark_theme: 如果为 True, 将确保颜色足够亮以在深色背景下显示
    :param hue: 色相控制。可传入字符串(如"blue", "red")、具体浮点数(0.0~1.0)，或None(使用全局随机)
    """
    global _last_h

    # 预设的色相区间字典 (H 的范围是 0.0 - 1.0)
    # 注意：红色跨越了 1.0 到 0.0 的边界
    HUE_MAP = {
        "red": (0.95, 1.05),
        "orange": (0.05, 0.12),
        "yellow": (0.12, 0.20),
        "green": (0.25, 0.45),
        "cyan": (0.45, 0.55),
        "blue": (0.55, 0.70),
        "purple": (0.70, 0.85),
        "pink": (0.85, 0.95),
    }

    # 1. 确定色相 H 的值
    if hue is not None:
        if isinstance(hue, str) and hue.lower() in HUE_MAP:
            # 根据提供的颜色名称，在区间内随机生成色相
            h_min, h_max = HUE_MAP[hue.lower()]
            h = random.uniform(h_min, h_max) % 1.0
        elif isinstance(hue, (int, float)):
            # 如果提供了具体的数字，给一个非常小的随机偏移(±0.03)，避免每次颜色一模一样
            h = (hue + random.uniform(-0.03, 0.03)) % 1.0
        else:
            h = random.random()
    else:
        # 如果没有指定 hue，继续使用原本的黄金分割率全局循环，保证颜色分散均匀
        _last_h = (_last_h + 0.618033988749895) % 1.0
        h = _last_h

    # 2. 根据色相调整初始亮度补偿 (保留你原有的优秀逻辑)
    # 蓝色 (0.55-0.7) 和紫色 (0.7-0.8) 需要更高的亮度补偿
    hue_step = 0.0
    if 0.5 <= h <= 0.85:  # 蓝色到紫色区间
        hue_step = 0.15
    elif h < 0.1 or h > 0.9:  # 红色区间
        hue_step = 0.05

    # 3. 根据模式确定饱和度(S)和亮度(L)
    match mode.lower():
        case "morandi":
            s = random.uniform(0.25, 0.45)  # 稍微提高一点点饱和度下限
            l = random.uniform(0.65, 0.8) + hue_step
        case "neon":
            s = random.uniform(0.8, 1.0)
            l = random.uniform(0.6, 0.75) + hue_step
        case "glass":
            s = random.uniform(0.4, 0.6)
            l = random.uniform(0.7, 0.85) + hue_step
        case _:
            s = random.uniform(0.5, 0.9)
            l = random.uniform(0.6, 0.8) + hue_step

    # 4. 最终约束：确保亮度不会超过 0.95 导致变白，也不会低于 0.6/0.2 导致看不清
    l = max(0.65 if is_dark_theme else 0.2, min(l, 0.95))

    # 5. HLS 转换为 RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    return hex_color


def get_hue_from_hex(hex_color: str) -> float:
    """
    工具函数：将 Hex 颜色 (如 '#ff6600') 转换回色相 H (0.0 - 1.0)
    """
    hex_color = hex_color.lstrip("#")
    # 转换为 0.0 - 1.0 的 RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    # rgb_to_hls 返回 (hue, lightness, saturation)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h


def HarmonyColors(base_hex_color: str, harmony_type="split", **kwargs):
    """
    根据基础颜色，计算并生成协调的搭配色
    :param base_hex_color: 基础 Hex 颜色 (如 RandColor 生成的颜色)
    :param harmony_type: 搭配模式
                         "split" (分裂互补色, 推荐, 2个颜色)
                         "complementary" (直接互补色, 1个颜色)
                         "analogous" (相邻色, 2个颜色)
                         "triadic" (三角色, 2个颜色)
    :param kwargs: 透传给 RandColor 的参数，如 mode="Neon", is_dark_theme=True
    :return: 搭配颜色的 Hex 列表
    """
    # 1. 提取基础色相
    base_h = get_hue_from_hex(base_hex_color)

    target_hues = []

    # 2. 根据色彩理论计算目标色相 (H 的范围是 0.0~1.0，相当于 360 度)
    match harmony_type:
        case "split":
            # 分裂互补色：原色相 + 150度 和 + 210度
            target_hues = [(base_h + 150 / 360) % 1.0, (base_h + 210 / 360) % 1.0]

        case "complementary":
            # 互补色：原色相 + 180度
            target_hues = [(base_h + 180 / 360) % 1.0]

        case "analogous":
            # 相邻色：原色相 ± 30度
            target_hues = [(base_h + 30 / 360) % 1.0, (base_h - 30 / 360) % 1.0]

        case "triadic":
            # 三角色：原色相 + 120度 和 + 240度
            target_hues = [(base_h + 120 / 360) % 1.0, (base_h + 240 / 360) % 1.0]

    # 3. 通过 RandColor 生成最终颜色
    # 由于你的 RandColor 接收到 float 类型的 hue 时，会自带 ±0.03 的微小随机偏移
    # 这会让生成的颜色不那么死板，充满设计感
    harmony_colors = [RandColor(hue=h, **kwargs) for h in target_hues]

    return harmony_colors
