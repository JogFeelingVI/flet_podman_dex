# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-02 02:37:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-02 02:39:04

import flet as ft


def get_snack_bar(Text: str):
    return ft.SnackBar(
        content=ft.Text(
            f"{Text}",
            style=ft.TextStyle(color="WHITE"),
        ),
        bgcolor="PINK",
    )
