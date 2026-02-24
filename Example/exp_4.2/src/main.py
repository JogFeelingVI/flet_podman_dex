# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-22 01:48:50
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-22 16:21:27

import random
import colorsys
import re
import flet as ft


def RandColor(mode="def"):
    """生成随机颜色, mode 可选 'def'（默认）或 'Morandi' 'Neon' 'Glass'"""
    h = random.random()  # 色相 (Hue)
    s = random.uniform(0.4, 1.0)  # 饱和度 (Saturation)
    l = random.uniform(0.4, 0.8)  # 亮度 (Lightness)，避免过黑或过白

    match mode:
        case "Morandi":
            s = random.uniform(0.2, 0.5)  # Morandi 色系通常较柔和，饱和度较低
            l = random.uniform(0.5, 0.7)  # Morandi 色系亮度适中
        case "Neon":
            s = random.uniform(0.7, 1.0)  # Neon 色系通常非常鲜艳，饱和度较高
            l = random.uniform(0.5, 0.7)  # Neon 色系亮度适中，避免过暗
        case "Glass":
            s = random.uniform(0.3, 0.6)  # Glass 色系通常较柔和，饱和度适中
            l = random.uniform(0.5, 0.8)  # Glass 色系亮度较高，模拟玻璃质感
        case _:
            pass  # 使用默认的 HSL 范围

    # 2. HSL 转换为 RGB (colorsys 中使用 HLS，顺序略有不同)
    # 注意：colorsys.hls_to_rgb 接收的顺序是 (h, l, s)
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # 3. 将 0-1 范围的 RGB 转换为 0-255 并转为 Hex 格式
    hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    return hex_color


# region paditem
class paditem(ft.Container):
    def __init__(self, text: str):
        super().__init__()
        self.userColor = RandColor()
        self.padding = ft.Padding(10, 5, 10, 5)
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, self.userColor))
        self.border_radius = 5
        self.bgcolor = ft.Colors.with_opacity(0.1, self.userColor)
        self.content = self.__build_content_row()
        self.tokens = []
        self.initialization(text)

    def initialization(self, text: str):
        """构建行中的项目
        kwargs 可包含：
            text:
                >{n}
                <{n}
                range {n,n}
                mod{n}
                {n+}
                bit{n}
                bit{n,n}
                --w{n}
                --j
                --o
                --z
                --h
                --m3{n}
        """
        pattern = r"\{[^}]+\}|[a-zA-Z]+|."
        result = re.findall(pattern, text)
        if result == []:
            result = ["Noempty"]
        print(f"Parsing text: '{text}' -> {result}")
        for part in result:
            if part.startswith("{") and part.endswith("}"):
                _n = part[1:-1]
                print(f"_n {_n} -> {part}")
                if _n == "n":
                    _n = random.randint(0, 9)
                elif _n == "n+":
                    _n = "4,5,6,7,8,9"
                black, show, edit = self.__build_editable_unit(init_val=f"{_n}")
                self.tokens.append({"type": "variable", "control": show})
                self.content.controls.append(black)

            else:
                self.tokens.append({"type": "text", "value": part})
                self.content.controls.append(
                    ft.Text(part, size=15, color=self.userColor)
                )

    def __build_content_row(self):
        return ft.Row(
            spacing=2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        )

    def __build_editable_unit(self, init_val: str):
        kids_width = 45
        show = ft.Text(
            init_val,
            size=15,
            color=self.userColor,
            weight="bold",
            text_align="center",
        )
        edit = ft.TextField(
            value=init_val,
            cursor_height=15,
            text_size=15,
            visible=False,
            color=self.userColor,
            dense=True,
            width=kids_width,
            content_padding=ft.Padding.all(0),
            border=ft.InputBorder.NONE,
            text_align="center",
            on_blur=lambda _: self.handle_blur(show, edit, black),
            on_change=lambda _: self.handle_change(show, edit),
        )
        black = ft.Container(
            height=25,
            padding=ft.Padding(5, 1, 5, 1),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, self.userColor)),
            border_radius=3,
            bgcolor=ft.Colors.with_opacity(0.1, self.userColor),
            content=ft.Stack(alignment=ft.Alignment.CENTER, controls=[show, edit]),
            on_click=lambda _: self.handle_click(show, edit, black),
        )
        return black, show, edit

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def command(self):
        """获取编辑后的指令"""
        cmd = []
        for token in self.tokens:
            if token["type"] == "text":
                cmd.append(token["value"])
            elif token["type"] == "variable":
                cmd.append(token["control"].value)
        return "".join(cmd)

    def handle_click(self, show: ft.Text, edit: ft.TextField, black: ft.Container):
        show.visible = False
        edit.visible = True
        black.update()

    def handle_blur(self, show: ft.Text, edit: ft.TextField, black: ft.Container):
        show.visible = True
        edit.visible = False
        black.update()
        cmd = self.command()
        print(f"Command after edit: {cmd}")

    def handle_change(self, show: ft.Text, edit: ft.TextField):
        show.value = edit.value


# endreion


# region quickpad
class quickpad(ft.Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userColor = RandColor()
        self.width = float("inf")  # 设置宽度为无限，充满父容器
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, self.userColor))
        self.border_radius = 10
        self.padding = 12
        self.bgcolor = ft.Colors.with_opacity(0.1, self.userColor)
        self.content = self.__build_content_row()

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_content_row(self):
        spacing = 2
        self.conten_row = ft.Row(
            wrap=True,
            spacing=spacing,
            run_spacing=spacing,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        return self.conten_row

    def clear_items(self):
        """清理项目"""
        self.conten_row.controls.clear()
        self.conten_row.update()

    def add_item(self, text: str):
        """添加项目"""
        if not text and not self.running:
            raise ValueError("Item must be an instance of flet.Control")
        temp = paditem(text=text)
        self.conten_row.controls.append(temp)
        self.conten_row.update()


# endregion


def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)
    quickpad_instance = quickpad()
    commands = [
        ">{n}",
        "<{n}",
        "range {n},{n}",
        "mod{n}",
        "{n+}",
        "bit{n}",
        "bit{n},{n} --w{n}",
        "--{m}",
        "--m3{n}",
    ]

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        try:
            text = commands.pop(0)
            quickpad_instance.add_item(text)
        except IndexError:
            quickpad_instance.add_item("error: no more commands.")

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=ft.Column(
                    controls=[counter, quickpad_instance],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
            ),
        )
    )


ft.run(main)
