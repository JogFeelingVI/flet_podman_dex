# @Author: JogFeelingVI
# @Date:   2026-11-03 08:11:02
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 22:58:06
# @File    : FormInputField.py
# @Time    : 2026/11/03 16:11:07
# @Author  : JogFeelingVI
# @Email   : glifelse@gmail.com
# @Desc    : 这是一个自定义符合控件 标签 输入框

import logging

import flet as ft

from LoveTV.src.themes.default import theme

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app.FormInputField")

"""
FormInputField 是一个自定义的 Flet 控件，用于创建带有标签的
"""


class FormInputField(ft.Container):
    def __init__(
        self,
        label: str,
        value: str = "",
        hint: str = "",
        password: bool = False,
        can_reveal_password: bool = False,
        **kwargs,
    ):
        self.selected = False
        self.text_field = ft.TextField(
            value=value,
            password=password,
            can_reveal_password=can_reveal_password,
            color=theme.on_surface,
            border=ft.NoInputBorder(),
            hint_text=hint,
            expand=3,
            on_focus=self.select,
            on_blur=self.deselect,
        )
        self.label = label
        super().__init__(
            max_width=400,
            bgcolor=theme.surface_bright,
            padding=ft.Padding(10, 5, 10, 5),
            border_radius=10,
            opacity=0.65,
            content=ft.Row(
                controls=[
                    ft.Text(
                        self.label,
                        size=16,
                        color=theme.on_surface_variant,
                        text_align=ft.TextAlign.RIGHT,
                        expand=1,
                    ),
                    self.text_field,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
                expand=True,
            ),
            **kwargs,
            on_hover=self.handle_on_hover,
        )

    # region self.selected
    async def select(
        self,
    ):
        self._set_selected(True)
        await self.text_field.focus()

    def deselect(self):
        self._set_selected(False)

    def _set_selected(self, value: bool):
        self.selected = value
        if value:
            self.opacity = 1.0
            self.shadow = ft.BoxShadow(
                color=ft.Colors.with_opacity(0.45, theme.on_secondary_container),
                blur_radius=10,
                spread_radius=2,
            )
        else:
            self.opacity = 0.65
            self.shadow = None
        self.update()

    # endregion

    def handle_on_hover(self, e):
        # log.debug(f"Hover event: {e.data}, Type: {type(e.data)}")
        if e.data:
            self.opacity = 1.0
            self.shadow = ft.BoxShadow(
                color=ft.Colors.with_opacity(0.45, theme.on_secondary_container),
                blur_radius=10,
                spread_radius=2,
            )
            self.selected = True
        else:
            self.opacity = 0.65
            self.shadow = None
            self.selected = False
        self.update()

    @property
    def text(self) -> str:
        return self.text_field.value

    @text.setter
    def text(self, new_value: str):
        self.text_field.value = new_value
        self.update()
