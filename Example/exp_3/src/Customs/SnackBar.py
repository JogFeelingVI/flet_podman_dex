# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-02 02:37:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-17 01:33:46

from .DraculaTheme import DraculaColors
import flet as ft


def get_snack_bar(Text: str, flg: str = "info"):
    _sbar = ft.SnackBar(content=ft.Text(f"{Text}", color=DraculaColors.FOREGROUND))
    match flg:
        case "info":
            _sbar.bgcolor = DraculaColors.COMMENT
        case "error":
            _sbar.bgcolor = DraculaColors.RED
        case "warning":
            _sbar.bgcolor = DraculaColors.ORANGE
    return _sbar
