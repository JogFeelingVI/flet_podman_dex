# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-16 10:11:33

import flet as ft
from Customs.DraculaTheme import DraculaColors, RandColor
from Customs.env_manager import env_manager
from Customs.filter import FilterPage
from Customs.loadfonts import FontManager, fsp_fonts
from Customs.loger import logr
from Customs.lottery import LotteryPage
from Customs.setings import SetingsPage


async def main(page: ft.Page):
    page.title = "Jackpot App lotter"
    # page.theme = Dracula_Theme
    # 设置移动端适配的内边距
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.Padding.only(top=20)
    page.bgcolor = DraculaColors.BACKGROUND
    # page.run

    # fsp = FastSourcePicker()
    # fsp_fonts = fsp.get_fastest_json()
    # fsp_fonts = FontManager()
    page.fonts = fsp_fonts.fonts_map()
    for name, path in page.fonts.items():
        logr.info(f"Registered fonts: {name} {path}")

    # --- 4. 预定义底部图标引用 (方便后续动态修改 Badge) ---
    lottery_icon = ft.Icon(
        ft.Icons.DATA_EXPLORATION_OUTLINED,
        color=RandColor(mode="Glass"),
        # 初始赋值：如果大于 0 就显示，否则 None
        # badge=str(initial_count) if initial_count > 0 else None,
    )

    logr.info("Initialization complete.")

    view_map = {
        0: SetingsPage(),
        1: FilterPage(),
        2: LotteryPage(),
    }

    view_map_index = 0

    # --- 页面逻辑控制 ---
    def on_navigation_change(e):
        index = e.control.selected_index
        nonlocal view_map, view_map_index

        # 2. 切换内容
        if index in view_map and index != view_map_index:
            content_area.content = view_map[index].view
            # 3. 关键优化：只 update 这个容器，不要 page.update()！
            content_area.update()
            view_map_index = index

    # --- 2. 界面组件定义 ---
    # 中间显示区域容器
    content_area = ft.Container(
        content=view_map[view_map_index].view,  # 默认显示设置页
        expand=True,
        padding=5,
    )

    # 底部 NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=RandColor(mode="Glass")),
                selected_icon=ft.Icons.SETTINGS,
                label="Setting",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icon(
                    ft.Icons.FILTER_LIST_OUTLINED, color=RandColor(mode="Glass")
                ),
                selected_icon=ft.Icons.FILTER_LIST,
                label="Filter",
            ),
            ft.NavigationBarDestination(
                icon=lottery_icon,
                selected_icon=ft.Icons.DATA_EXPLORATION,
                label="Lotter",
            ),
        ],
        on_change=on_navigation_change,
    )

    # 将内容添加到页面
    page.add(content_area)


if __name__ == "__main__":
    # multiprocessing.freeze_support()
    # 运行应用，使用环境管理器中的路径
    ft.run(main, upload_dir=env_manager.temp_path, assets_dir=env_manager.assets_dir)
