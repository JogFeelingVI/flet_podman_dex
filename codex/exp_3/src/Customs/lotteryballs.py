# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-10 06:05:07
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-17 01:33:36

from .DraculaTheme import DraculaColors
import flet as ft


class LotteryBalls(ft.Row):
    """_summary_

    Args:
        align (str): CE or LE
    """

    def __init__(self, numbers_str: str, ball_size=32, align="CE"):
        super().__init__()
        self.numbers_str = numbers_str
        self.ball_size = ball_size
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 5  # 球与球之间的间距
        # self.expand = True
        match align:
            case "CE":
                self.align = ft.Alignment.CENTER
            case "LE":
                self.align = ft.Alignment.CENTER_LEFT
            case _:
                self.align = ft.Alignment.CENTER
        self.wrap = True

        # 初始化时构建界面
        self.build_balls()

    def build_balls(self):
        # 1. 解析字符串
        # 假设输入格式为 "01 04 05 06 19 20 + 16"
        number_split = self.numbers_str.split("+")
        if number_split.__len__() == 2:
            main_part, special_part = number_split
            red_numbers = main_part.strip().split()
            blue_numbers = special_part.strip().split()
        elif number_split.__len__() >= 3:
            red_numbers = [x.strip() for x in number_split]
            blue_numbers = []
        else:
            red_numbers = self.numbers_str.strip().split()
            blue_numbers = []

        # 2. 生成红球 (前区)
        for num in red_numbers:
            self.controls.append(self.create_ball(num, ft.Colors.RED))

        # 3. 如果有蓝球部分，添加一个 "+" 符号
        # if blue_numbers:
        #     self.controls.append(
        #         ft.Text(
        #             "+", color=ft.Colors.WHITE70, size=16, weight=ft.FontWeight.BOLD
        #         )
        #     )

        # 4. 生成蓝球 (后区)
        for num in blue_numbers:
            # 这里如果你想统一红色，可以继续传 RED，如果是标准彩票通常蓝球用蓝色
            # 根据你要求“红色的球”，这里我也设为红色
            self.controls.append(self.create_ball(num, ft.Colors.BLUE_700))

    def create_ball(self, text, bg_color):
        """创建单个球体的辅助函数"""
        if bg_color == "red":
            gradient_colors = [
                ft.Colors.RED_ACCENT,
                ft.Colors.RED_700,
                ft.Colors.RED_900,
            ]
        else:
            gradient_colors = [
                ft.Colors.BLUE_ACCENT,
                ft.Colors.BLUE_700,
                ft.Colors.BLUE_900,
            ]
        return ft.Container(
            content=ft.Text(
                value=text,
                color="#FFD700",  # 金色数字 (Gold)
                size=self.ball_size * 0.45,
                weight=ft.FontWeight.BOLD,
            ),
            width=self.ball_size,
            height=self.ball_size,
            bgcolor=bg_color,
            border_radius=self.ball_size / 2,  # 圆球
            alignment=ft.Alignment.CENTER,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color="#42000000",
                offset=ft.Offset(0, 2),
            ),
            gradient=ft.RadialGradient(
                center=ft.Alignment(-0.3, -0.3),  # 光源位于左上角
                radius=1.2,
                colors=gradient_colors,
            ),
        )
