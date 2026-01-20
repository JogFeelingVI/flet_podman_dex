# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-15 13:31:31
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-15 13:33:33

import flet as ft
import flet.canvas as cv


class CanvasTextListRecorder(ft.Stack):
    def __init__(
        self, text_list, width=400, height=500, line_height=40, bg_color=ft.colors.BLACK
    ):
        super().__init__()
        self.text_list = text_list
        self.canvas_width = width
        self.canvas_height = height
        self.line_height = line_height
        self.bg_color = bg_color

        # 构建 Canvas 形状
        self.shapes = [cv.Rect(0, 0, width, height, paint=ft.Paint(color=bg_color))]
        self._build_text_shapes()

        # 初始化核心组件
        self.canvas = cv.Canvas(
            width=self.canvas_width, height=self.canvas_height, shapes=self.shapes
        )
        self.screenshot = ft.Screenshot(content=self.canvas)
        self.controls = [self.screenshot]

    def _build_text_shapes(self):
        """内部方法：计算坐标并生成文字形状"""
        start_y = 20
        start_x = 20
        for i, text in enumerate(self.text_list):
            self.shapes.append(
                cv.Text(
                    x=start_x,
                    y=start_y + (i * self.line_height),
                    text=text,
                    style=ft.TextStyle(
                        size=16,
                        color=ft.colors.WHITE,
                        font_family="Consolas",  # 2026年常用等宽字体
                    ),
                )
            )

    async def save_to_file(self, file_path="output.png"):
        """导出方法：截取当前 Canvas 并保存"""
        try:
            img_bytes = await self.screenshot.capture()
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
