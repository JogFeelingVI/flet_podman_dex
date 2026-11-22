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
        self._mount = False
        self.selected = False
        self.text_field = ft.TextField(
            value=value,
            password=password,
            can_reveal_password=can_reveal_password,
            color=theme.on_surface,
            border=ft.NoInputBorder(),
            hint_text=hint,
            col={"xs": 7, "sm": 7, "md": 8, "lg": 9, "xl": 9, "xxl": 9},
            on_focus=self.select,
            on_blur=self.deselect,
        )
        self.label = label
        super().__init__(
            bgcolor=theme.surface_bright,
            padding=ft.Padding(10, 5, 10, 5),
            border_radius=10,
            opacity=0.65,
            content=ft.ResponsiveRow(
                controls=[
                    ft.Text(
                        self.label,
                        size=16,
                        color=theme.on_surface_variant,
                        text_align=ft.TextAlign.RIGHT,
                        col={"xs": 5, "sm": 5, "md": 4, "lg": 3, "xl": 3, "xxl": 3},
                    ),
                    self.text_field,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
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

    def did_mount(self):
        self._mount = True
        return super().did_mount()

    def will_unmount(self):
        self._mount = False
        return super().will_unmount()

    @property
    def text(self) -> str:
        return self.text_field.value

    @text.setter
    def text(self, new_value: str):
        self.text_field.value = new_value
        if self._mount:
            self.text_field.update()
