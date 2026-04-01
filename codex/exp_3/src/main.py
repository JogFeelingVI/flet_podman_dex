# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-30 05:49:32

import os

import flet as ft
from Customs.DraculaTheme import DraculaColors, RandColor
from Customs.filter import FilterPage
from Customs.jackpot_core import randomData
from Customs.loadfonts import FontManager
from Customs.loger import logr
from Customs.lottery import LotteryPage
from Customs.setings import SetingsPage

# 获取系统标示
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
app_assets_dir = os.getenv("FLET_ASSETS_DIR")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

os.environ["FLET_SECRET_KEY"] = randomData.generate_secure_string(16)


async def main(page: ft.Page):
    page.title = "Jackpot App lotter"
    # page.theme = Dracula_Theme
    # 设置移动端适配的内边距
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.Padding.only(top=20)
    page.bgcolor = DraculaColors.BACKGROUND

    # fsp = FastSourcePicker()
    # fsp_fonts = fsp.get_fastest_json()
    fsp_fonts = FontManager()
    page.fonts = fsp_fonts.get_fonts()
    logr.info(f"Registered fonts: {page.fonts}")

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
    # page.update()
    # mcp_server = mcpserver(page.platform)
    # mcp_server.run_mcp_server()


if __name__ == "__main__":
    # multiprocessing.freeze_support()
    # 运行应用
    ft.run(main, upload_dir=app_temp_path, assets_dir=app_assets_dir)
