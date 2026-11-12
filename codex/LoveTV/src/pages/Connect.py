# @File    : Connect.py
# @Time    : 2026/11/12 07:43:42
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 请在此处输入文件描述

import flet as ft


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def open_player():
        await navigate("/player")

    author_view = ft.View(
        route="/connect",
        controls=[
            ft.Text("lifelse##outlook.com"),
        ],
    )
    return author_view