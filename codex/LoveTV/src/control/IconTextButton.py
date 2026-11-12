# @File    : IconTextButton.py
# @Time    : 2026/11/06 13:32:18
# @Author  : JogFeelingVI
# @Email   : glifelse#gmail.com
# @Desc    : icon + text

import logging

import flet as ft

from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.IconTextButton")


class IconTextButton(ft.Container):
    def __init__(
        self,
        name,
        icon: ft.IconData = ft.Icons.HISTORY,
        navigate=None,
        route=None,
        **kwds,
    ):
        self.route = route
        self.navigate = navigate
        self.lable = ft.Text(
            name,
            color=theme.primary,
            size=18,
        )
        self.icon = ft.Icon(icon, size=18, color=theme.primary)
        super().__init__(
            padding=ft.Padding.symmetric(vertical=10, horizontal=5),
            content=ft.Row(
                controls=[self.icon, self.lable],
                alignment=ft.Alignment.CENTER,
                spacing=5,
            ),
            on_hover=self._handle_hover,
            on_click=self._handle_click,
            **kwds,
        )

    async def _handle_click(self, e):
        if self.route and self.navigate:
            await self.navigate(self.route)
            log.info(f"route {self.route}")

    def _handle_hover(self, e):
        if e.data:
            self.lable.color = theme.primary_container
            self.icon.color = theme.primary_container
        else:
            self.lable.color = theme.primary
            self.icon.color = theme.primary
        self.update()
