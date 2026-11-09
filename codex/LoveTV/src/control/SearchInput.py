# @File    : Search.py
# @Time    : 2026/11/06 08:52:37
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : 搜索控件

import logging

import flet as ft

from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.PapaChild")


class SearchInput(ft.Container):
    def __init__(self, /, **kwds):
        self.search_input = ft.TextField(
            hint_text="搜索心动好剧",
            hint_style=ft.TextStyle(
                size=12, color=ft.Colors.with_opacity(0.45, theme.on_surface)
            ),
            width=120,
            text_size=12,
            color=theme.on_surface,
            border=ft.NoInputBorder(),
            dense=True,
            content_padding=0,
            on_focus=self._handle_focus,
            on_blur=self._handle_blur,
        )

        self.search_icon = ft.Icon(
            ft.Icons.SEARCH,
            color=theme.on_surface,
            size=18,
        )
        super().__init__(
            height=36,
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.70, theme.secondary_container),
            padding=ft.Padding.symmetric(vertical=10, horizontal=5),
            alignment=ft.Alignment.CENTER,  # 直接让输入框整体居中
            content=ft.Row(
                controls=[
                    ft.VerticalDivider(width=2, opacity=0.0),
                    self.search_icon,
                    self.search_input,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            clip_behavior=ft.ClipBehavior.NONE,
            **kwds,
        )

    def _handle_focus(self, e):
        self.bgcolor = ft.Colors.with_opacity(1, theme.secondary_container)

    def _handle_blur(self, e):
        self.bgcolor = ft.Colors.with_opacity(0.7, theme.secondary_container)
