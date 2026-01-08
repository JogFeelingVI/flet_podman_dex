# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-03 09:49:02

from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import json
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class DataPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = self.get_data_view()

    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Data",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=Dracula_colors.COMMENT,
                ),
                ft.Text("显示筛选后的结果", color=Dracula_colors.FOREGROUND),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID", color=Dracula_colors.FOREGROUND)),
                        ft.DataColumn(ft.Text("结果", color=Dracula_colors.FOREGROUND)),
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text("1", color=Dracula_colors.FOREGROUND)
                                ),
                                ft.DataCell(
                                    ft.Text("数据 A", color=Dracula_colors.FOREGROUND)
                                ),
                            ]
                        ),
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Text("2", color=Dracula_colors.FOREGROUND)
                                ),
                                ft.DataCell(
                                    ft.Text("数据 B", color=Dracula_colors.FOREGROUND)
                                ),
                            ]
                        ),
                    ],
                    heading_text_style=ft.TextStyle(
                        color=Dracula_colors.PURPLE, weight=ft.FontWeight.BOLD
                    ),
                    data_text_style=ft.TextStyle(color=Dracula_colors.FOREGROUND),
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
