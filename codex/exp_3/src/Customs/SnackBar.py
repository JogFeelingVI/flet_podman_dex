# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-02 02:37:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-06 05:44:02

from .DraculaTheme import Dracula_colors
import flet as ft


def get_snack_bar(Text: str, flg: str = "info"):
    _sbar = ft.SnackBar(content=ft.Text(f"{Text}", color=Dracula_colors.FOREGROUND))
    match flg:
        case "info":
            _sbar.bgcolor = Dracula_colors.COMMENT
        case "error":
            _sbar.bgcolor = Dracula_colors.RED
        case "warning":
            _sbar.bgcolor = Dracula_colors.ORANGE
    return _sbar
