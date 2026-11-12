# @File    : Author.py
# @Time    : 2026/11/09 09:00:41
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 这是一个作者信息页面

import flet as ft


def build(page: ft.Page, state: dict, navigate) -> ft.View:
    async def open_player():
        await navigate("/player")
        
    author_view = ft.View(
        route="/author",
        controls=[
            ft.Text("lifelse##outlook.com"),
        ],
    )
    return author_view
