# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-08 05:18:38

from .jackpot_core import randomData, filter_for_pabc
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import json
import os
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def calculate_lottery(setings: dict, filters: list):
    if setings:
        rd = randomData(seting=setings)
    else:
        return ("No Numbers", False)
    result = rd.get_pabc()
    if not filters:
        return (rd.get_exp(result), True)
    filter_jp = filter_for_pabc(filters=filters)
    if filter_jp.handle(result) == False:
        return [rd.get_exp(result), False]
    return (rd.get_exp(result), True)


class listext_onlong(ft.ListTile):
    def __init__(self):
        super().__init__()
        self.title = ft.Text(
            f"{randomData.generate_secure_string()}",
            color=Dracula_colors.COMMENT,
            size=11,
        )
        self.data = "No Number"
        self.leading = ft.Icon(ft.Icons.GENERATING_TOKENS, color=Dracula_colors.ORANGE)
        self.subtitle = ft.Text(
            f"{self.data}", weight="bold", size=18, color=Dracula_colors.PURPLE
        )
        self.on_long_press = lambda _: self.get_data(1, True)
        self.runing = True

    def setting_args(self, setting: dict, filter: list):
        self.setting = setting
        self.filers = filter

    def did_mount(self):
        self.get_data(0)

    def will_unmount(self):
        self.runing = False

    def get_data(self, state: int = 1, onoff=False):
        if state == 0 and self.runing:
            self.page.run_task(self.refresh)
        if state == 1 and onoff:
            self.page.run_task(self.refresh)

    async def refresh(self):
        isok = False
        note_error = 0
        while isok == False:
            tempd, state = calculate_lottery(setings=self.setting, filters=self.filers)
            if state:
                self.data = tempd
                self.subtitle = ft.Text(
                    f"{self.data}", weight="bold", size=18, color=Dracula_colors.PURPLE
                )
                isok = state
            else:
                if note_error >= 100:
                    self.subtitle = ft.Text(
                        "Filter settings are incorrect.",
                        weight="bold",
                        size=18,
                        color=Dracula_colors.RED,
                    )
                    self.page.update()
                    break
                note_error += 1
                self.data = tempd
                self.subtitle = ft.Text(
                    f"{self.data}", weight="bold", size=18, color=Dracula_colors.PURPLE
                )
            self.page.update()
            await asyncio.sleep(0.1)


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.set_Lotter_buttons()
        self.lottery_items_column = ft.Column(spacing=5)
        self.view = self.get_data_view()

    def set_Lotter_buttons(self):
        Lottery_item_count_data = {"2": 2, "5": 5, "10": 10, "15": 15}
        button_list = []
        for key, item in Lottery_item_count_data.items():
            button_list.append(
                ft.Button(
                    f"{key} items",
                    tooltip=ft.Tooltip(
                        message=f"Set the number of lottery tickets to obtain to {key}."
                    ),
                    # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                    on_click=lambda e, data=item: self.save_Lottery_item(data),
                )
            )
        return button_list

    def save_Lottery_item(self, data: int):
        self.page.session.store.set("Lottery_item_count", data)
        self.page.show_dialog(get_snack_bar(f"setting item count {data}"))

    def Get_Lottery_data(self, index: int):
        try:
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            lic = self.page.session.store.get("Lottery_item_count") or 5
            self.lottery_items_column.controls.clear()
            for _ in range(lic):
                listext = listext_onlong()
                listext.setting_args(settings["randomData"], filters)
                self.lottery_items_column.controls.append(listext)
            # self.lottery_items_column.cilcked(settings["randomData"], filters=filters)
        except Exception:
            self.page.show_dialog(
                get_snack_bar("Failed to retrieve settings data.", "error")
            )

    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Lottery",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=Dracula_colors.COMMENT,
                ),
                ft.Button(
                    "Get lottery results",
                    icon=ft.Icons.SHOW_CHART,
                    on_click=lambda _: self.Get_Lottery_data(-1),
                ),
                ft.Divider(),
                ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                ft.Divider(),
                ft.Column(
                    self.lottery_items_column,
                    scroll=ft.ScrollMode.HIDDEN,
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
