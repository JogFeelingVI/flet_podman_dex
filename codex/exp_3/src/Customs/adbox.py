# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-07 11:39:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-12 05:00:48


from .DraculaTheme import DraculaColors, RandColor, HarmonyColors
import flet as ft


class adbx(ft.AlertDialog):
    def __init__(self, uc: str, content: ft.Control):
        self.userColor = uc if uc else RandColor(mode="neon")
        self.shape = ft.RoundedRectangleBorder(
            radius=10,
            side=ft.BorderSide(1, self.userColor),  # 宽度为2，颜色为蓝色
        )
        self._ucontent = content
        self.running = False
        self.did_mount_callback = None

        super().__init__(
            content=self.__build_conter(),
            content_padding=0,
            title_padding=0,
            actions_padding=0,
            modal=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )

    def setting_did_mount_callback(self, didcallback=None):
        self.did_mount_callback = didcallback

    def did_mount(self):
        self.running = True
        if self.did_mount_callback:
            self.page.run_task(self.did_mount_callback)

    def will_unmount(self):
        self.running = False

    def __build_conter(self):
        shadow_color = HarmonyColors(
            base_hex_color=self.userColor, harmony_type="analogous", mode="neon"
        )
        conter = ft.Container(
            padding=12,
            width=400,
            blur=ft.Blur(sigma_x=5, sigma_y=5, tile_mode=ft.BlurTileMode.MIRROR),
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.3, shadow_color[0])),
            bgcolor=ft.Colors.TRANSPARENT,
            shadow=ft.BoxShadow(
                spread_radius=1,  # 阴影扩散范围
                blur_radius=8,  # 模糊程度（数值越大光越柔和）
                color=ft.Colors.with_opacity(0.2, shadow_color[1]),  # 阴影颜色
                offset=ft.Offset(0, 0),  # 阴影偏移
            ),
        )
        conter.content = self._ucontent if self._ucontent else None
        return conter
