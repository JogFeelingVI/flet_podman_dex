# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-22 16:21:36
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-22 17:29:51

from .DraculaTheme import DraculaColors, RandColor
import re
import random
import flet as ft

__version__ = "0.1.0"


# region paditem
class paditem(ft.Container):
    def __init__(self, text: str):
        super().__init__()
        self.userColor = RandColor(mode="Morandi")
        self.padding = ft.Padding(10, 5, 10, 5)
        # self.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, self.userColor))
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
                elif _n == "m":
                    _n = "w"
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
        self.data = "__quickpad__"
        self.userColor = RandColor(mode="Morandi")
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

    def pop_item(self, index: int = -1):
        self.conten_row.controls.pop(index)
        self.conten_row.update()

    def all_command(self):
        """获取所有项目的指令"""
        cmds = []
        for item in self.conten_row.controls:
            if isinstance(item, paditem):
                cmds.append(item.command())
        return " ".join(cmds)

    def replacement(self, text: str = None):
        """替换所有项目的指令"""
        if "{" in text and "}" in text:
            return text
        subs = re.compile(r"(--)([a-zA-Z0-9]+)|(\d+(?:,\d+)+)|(\d+)")

        def replace_func(match):
            # 1. 处理 --w012789 模式
            if match.group(1):
                return f"{match.group(1)}{{{match.group(2)}}}"

            # 2. 处理 4,5,6 这种逗号序列模式
            elif match.group(3):
                return f"{{{match.group(3)}}}"

            # 3. 处理单个数字模式
            elif match.group(4):
                return f"{{{match.group(4)}}}"

            return match.group(0)

        return subs.sub(replace_func, text)

    def add_item(self, text: str):
        """添加项目"""
        if not text and not self.running:
            raise ValueError("Item must be an instance of flet.Control")
        temp = paditem(text=self.replacement(text))
        self.conten_row.controls.append(temp)
        self.conten_row.update()


# endregion
