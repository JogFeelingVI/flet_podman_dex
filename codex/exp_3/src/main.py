# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-08 11:34:21

from Customs.DraculaTheme import  Dracula_colors
from Customs.setings import SetingsPage
from Customs.filter import FilterPage
from Customs.lottery import LotteryPage
import flet as ft
import json
import os

# 获取系统标示
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def main(page: ft.Page):
    page.title = "Jackpot App"
    # page.theme = Dracula_Theme
    # 设置移动端适配的内边距
    page.padding = ft.Padding.only(top=20)

    # --- 页面逻辑控制 ---
    def on_navigation_change(e):
        index = e.control.selected_index
        # 切换中间的内容区域
        if index == 0:
            content_area.content = setting_class.view
        elif index == 1:
            content_area.content = filter_class.view
        elif index == 2:
            content_area.content = lottery_class.view
        page.update()

    setting_class = SetingsPage(page)

    filter_class = FilterPage(page)

    lottery_class = LotteryPage(page)

    # --- 2. 界面组件定义 ---

    # 中间显示区域容器
    content_area = ft.Container(
        content=setting_class.view,  # 默认显示设置页
        expand=True,
        padding=20,
    )

    # 底部 NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=Dracula_colors.PURPLE),
                selected_icon=ft.Icons.SETTINGS,
                label="Setting",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(
                    ft.Icons.FILTER_LIST_OUTLINED, color=Dracula_colors.PURPLE
                ),
                selected_icon=ft.Icons.FILTER_LIST,
                label="Filter",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(
                    ft.Icons.DATA_EXPLORATION_OUTLINED, color=Dracula_colors.PURPLE
                ),
                selected_icon=ft.Icons.DATA_EXPLORATION,
                label="Lottery",
            ),
        ],
        on_change=on_navigation_change,
    )

    # 将内容添加到页面
    page.add(content_area)
    page.update()


# 运行应用
ft.run(main)
