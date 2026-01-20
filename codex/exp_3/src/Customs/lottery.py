# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-17 14:52:44

import asyncio
from .jackpot_core import randomData
from .lotteryballs import LotteryBalls
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .dismiss import dism
import flet as ft
import json
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class gdbug(ft.GestureDetector):
    def __init__(
        self,
        icon: ft.Icon,
        initialize=None,
        on_tap_handler=None,
        on_long_press_handler=None,
    ):
        super().__init__()
        # 保存回调
        self.initialize_task = initialize
        self.on_tap_handler = on_tap_handler
        self.on_long_press_handler = on_long_press_handler

        # 标志位防止重复初始化
        self._is_running = False

        # 构建 UI
        self.mouse_cursor = ft.MouseCursor.CLICK
        self.content = self._build_content(icon)

        # 绑定内部处理函数，实现点击动画
        self.on_tap = self._handle_tap
        self.on_long_press_start = self._handle_long_press

    def _build_content(self, icon):
        return ft.Container(
            content=icon,
            padding=15,
            bgcolor=DraculaColors.ORANGE,
            width=56,
            height=56,
            border_radius=16,
            alignment=ft.Alignment.CENTER,
            # 增加动画属性，让按钮“活”起来
            animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )

    def did_mount(self):
        # 只有在第一次挂载且有初始化任务时执行
        if self.initialize_task and not self._is_running:
            self.page.run_task(self.initialize_task)
            self._is_running = True
        return super().did_mount()

    # --- 内部手势处理，增加动画反馈 ---

    async def _handle_tap(self, e):
        # 模拟物理按压效果：缩小 -> 恢复
        self.content.scale = 0.85
        self.content.update()

        # 执行外部传入的点击逻辑
        if self.on_tap_handler:
            if asyncio.iscoroutinefunction(self.on_tap_handler):
                await self.on_tap_handler(e)
            else:
                self.on_tap_handler(e)

        # 弹回正常大小
        self.content.scale = 1.0
        self.content.update()

    async def _handle_long_press(self, e):
        # 长按反馈：轻微放大
        self.content.scale = 1.15
        self.content.update()

        # 执行长按逻辑
        if self.on_long_press_handler:
            if asyncio.iscoroutinefunction(self.on_long_press_handler):
                await self.on_long_press_handler(e)
            else:
                self.on_long_press_handler(e)

        # 恢复大小
        self.content.scale = 1.0
        self.content.update()


class sbbdismiss(ft.Column):
    """自主读取savelist"""

    def __init__(self, data: list):
        """data = 01 02 03 | 04 05 06"""
        super().__init__()
        self.External_data = data
        self.items = []

    def did_mount(self):
        self.running = True
        self.load_data()

    def load_data(self):
        lines = []
        while len(lines) < 5 and len(self.External_data) > 0:
            item = self.External_data.pop(0)
            self.items.append(item)
            lines.append(self.__build_row(item))
        self.controls = lines
        self.update()

    def __build_row(self, item: list):
        return ft.Dismissible(
            content=ft.Container(
                content=LotteryBalls(item, ball_size=29, align="LE"),
                padding=2,
            ),
            background=ft.Container(
                bgcolor=DraculaColors.RED,
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.DELETE_OUTLINE,
                            color=DraculaColors.FOREGROUND,
                        ),
                        ft.Text(
                            "Delete",
                            color=DraculaColors.FOREGROUND,
                            weight="bold",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=ft.Padding.only(left=20),
                border_radius=5,
            ),
            dismiss_direction=ft.DismissDirection.START_TO_END,
            on_confirm_dismiss=lambda e, lb=item: self.page.run_task(
                self.handle_data_row_dismiss, e, lb
            ),  # 传递当前 LotteryBalls 实例
        )

    async def handle_data_row_dismiss(self, e, lb):
        await e.control.confirm_dismiss(True)
        self.External_data.append(lb)
        self.items.remove(lb)
        self.controls.remove(e.control)
        print(f"handle_data_row_dismiss {lb}")
        if len(self.External_data) > 0:
            nlb = self.External_data.pop(0)
            self.items.append(nlb)
            self.controls.append(self.__build_row(nlb))
        self.update()


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_dir = app_data_path
        self.buttons = self.set_Lotter_buttons()
        self.lottery_icon = ft.Icon(
            icon=ft.Icons.MONEY,
            color=DraculaColors.FOREGROUND,
            badge=ft.Badge(
                label="0",
                bgcolor=DraculaColors.COMMENT,
                text_color=DraculaColors.FOREGROUND,
                label_visible=False,
            ),
        )

        self.Fab = gdbug(
            icon=self.lottery_icon,
            initialize=self.initialize_data,
            on_tap_handler=lambda _: self.Get_Lottery_data(-1),
            on_long_press_handler=self.inisatll_save_dig,
        )

        # self.Fab = ft.GestureDetector(
        #     content=ft.Container(
        #         content=self.lottery_icon,
        #         padding=15,
        #         bgcolor=DraculaColors.ORANGE,
        #         width=56,
        #         height=56,
        #         border_radius=ft.border_radius.all(16),  # 圆形
        #         alignment=ft.Alignment.CENTER,
        #         # 添加阴影，使其看起来像悬浮按钮
        #         shadow=ft.BoxShadow(
        #             spread_radius=1,
        #             blur_radius=10,
        #             color="#42000000",
        #             offset=ft.Offset(0, 2),
        #         ),
        #     ),
        #     mouse_cursor=ft.MouseCursor.CLICK,
        #     on_tap=lambda _: self.Get_Lottery_data(-1),
        #     on_long_press=self.inisatll_save_dig,
        # )

        self.lottery_items_column = ft.Column(
            spacing=1, scroll=ft.ScrollMode.HIDDEN, expand=True
        )
        self.view = self.get_data_view()

        # self.page.run_task(self.initialize_data)

    async def inisatll_save_dig(self, e):
        raw_json = await self.page.shared_preferences.get("save_data_list")
        saved_data = json.loads(raw_json) if raw_json else []
        print(f"kaishi Save. {saved_data=}")
        if saved_data.__len__() == 0:
            self.page.show_dialog(get_snack_bar("No data to save.", "error"))
            return
        sbms = sbbdismiss(saved_data)
        saved_data = sbms.External_data
        items = sbms.items

        async def handle_save(e):
            e.control.disabled = True
            self.page.update()
            path = await self.select_dir()
            if not path:
                print("No directory was selected; saving cancelled.")
                e.control.disabled = False
                self.page.update()
                return
            print(f"select dir is {self.user_dir=}")
            await self.save_screenshot(sc, path, genid)
            nonlocal items
            items.clear()
            # await self.initialize_data()
            await asyncio.sleep(0.5)
            self.Badge_number(0)
            e.control.disabled = False
            BottomSheet.open = False
            # self.page.update()

        def handle_cancel(e):
            BottomSheet.open = False
            self.page.update()

        def handle_clear(e):
            print("Clear all saved data.")
            nonlocal items
            items.clear()
            self.Badge_number(0)
            BottomSheet.open = False

        genid = randomData.generate_secure_string(8)

        sc = ft.Screenshot(
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    opacity=1.0,
                    controls=[
                        # ft.Text(
                        #     value="JackPot",
                        #     size=30,
                        #     weight=ft.FontWeight.W_900,
                        #     color=DraculaColors.PINK,
                        # ),
                        # ? 添加图片
                        ft.Row(
                            controls=[
                                ft.Image(
                                    src="jackpot.png",
                                    fit=ft.BoxFit.FIT_HEIGHT,
                                    width=397 * 0.45,
                                    height=127 * 0.45,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Divider(color=DraculaColors.PURPLE),
                        sbms,
                        ft.Row(
                            controls=[
                                ft.Text(
                                    value=f"GENID: {genid}",
                                    size=15,
                                    weight=ft.FontWeight.W_100,
                                    color=DraculaColors.BACKGROUND,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,  # 关键点：主轴对齐到末尾
                        ),
                    ],
                ),
                bgcolor=DraculaColors.CURRENT_LINE,
                padding=20,
                width=400,
                # height=680,
                alignment=ft.Alignment.TOP_CENTER,
            )
        )
        savebut = ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextButton(
                        content="Save",
                        on_click=handle_save,
                    ),
                    ft.TextButton(
                        content="Cancel",
                        on_click=handle_cancel,
                    ),
                    ft.TextButton(
                        content="Clear All",
                        on_click=handle_clear,
                    ),
                ],
            ),
            padding=ft.Padding(top=0, bottom=20, left=20, right=20),
            width=400,
        )

        BottomSheet = ft.BottomSheet(
            # scrollable=True,
            bgcolor=DraculaColors.CURRENT_LINE,
            content=ft.Column(
                controls=[
                    sc,
                    savebut,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            on_dismiss=lambda _, data=items: self.handle_dismiss_save(data),
        )
        self.page.show_dialog(BottomSheet)

        await self.page.shared_preferences.set("save_data_list", json.dumps(saved_data))
        await self.initialize_data()

    async def select_dir(self):
        stored_dir = await self.page.shared_preferences.get("user_dir")
        if stored_dir:
            self.user_dir = stored_dir
            return self.user_dir

        if not self.page.web:
            picked_dir = await ft.FilePicker().get_directory_path(
                dialog_title="Please select a directory?"
            )
            if picked_dir:
                await self.page.shared_preferences.set("user_dir", picked_dir)
                self.user_dir = picked_dir
                return self.user_dir
        return self.user_dir

    async def save_screenshot(self, screenshot: ft.Screenshot, path, genid=""):
        image = await screenshot.capture()
        print(f"image data size: {len(image)} bytes")

        obj_path = os.path.join(path, f"jackpot_{genid}.png")
        print(f"saving screenshot to: {obj_path}")
        with open(obj_path, "wb") as f:
            f.write(image)

    def handle_dismiss_save(self, data: list):
        self.page.run_task(self.dismiss_save_data, data)

    async def dismiss_save_data(self, data: list):
        raw_json = await self.page.shared_preferences.get("save_data_list")
        saved_data = json.loads(raw_json) if raw_json else []
        saved_data.extend(data)
        await self.page.shared_preferences.set("save_data_list", json.dumps(saved_data))
        self.page.run_task(self.initialize_data)
        # print(f'dismiss_save_data {saved_data=}')
        self.Badge_number(len(saved_data))

    async def initialize_data(self):
        """异步加载初始数据并渲染"""
        try:  # 确保这是一个异步函数
            raw_json = await self.page.shared_preferences.get("save_data_list")
            saved_data = json.loads(raw_json) if raw_json else []
            initial_count = len(saved_data)
            self.lottery_icon.badge.label = f"{initial_count}"
            if self.lottery_icon.badge.label == "0":
                self.lottery_icon.badge.label_visible = False
            else:
                self.lottery_icon.badge.label_visible = True

        except Exception as e:
            print(f"Waiting for interface initialization...: {e}")
        finally:
            self.Fab.update()

    def Badge_number(self, lens: int = 0):
        self.page.run_task(self.initialize_data)
        for nbar in self.page.navigation_bar.destinations:
            if isinstance(nbar, ft.NavigationBarDestination) and nbar.label == "Lotter":
                if lens != 0:
                    nbar.icon.badge = str(lens)
                else:
                    nbar.icon.badge = None
        self.page.update()

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
        print(f"Get_Lottery_data is runing {index=}")
        try:
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            lic = self.page.session.store.get("Lottery_item_count") or 5
            for isdism in self.lottery_items_column.controls:
                if not isdism:
                    continue
                if isinstance(isdism, dism):
                    if isdism.is_refreshing:
                        self.page.show_dialog(
                            get_snack_bar(
                                "The DISM tasks were not all completed.", "error"
                            )
                        )
                        return

            self.lottery_items_column.controls.clear()
            for _ in range(lic):
                # listext = listext_onlong()
                listext = dism()
                listext.setting_args(settings["randomData"], filters, self.Badge_number)
                self.lottery_items_column.controls.append(listext)
            # self.lottery_items_column.cilcked(settings["randomData"], filters=filters)
        except Exception as e:
            self.page.show_dialog(
                get_snack_bar("Failed to retrieve settings data.", "error")
            )

    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Image(
                    src="lotter.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=288 * 0.45,
                    height=131 * 0.45,
                ),
                # ft.Text(
                #     value="Lottery",
                #     size=25,
                #     weight=ft.FontWeight.BOLD,
                #     color=DraculaColors.COMMENT,
                # ),
                # ft.Button(
                #     "Get lottery results",
                #     icon=ft.Icons.SHOW_CHART,
                #     on_click=lambda _: self.Get_Lottery_data(-1),
                # ),
                ft.Divider(),
                ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                ft.Divider(),
                # ft.Column(
                #     self.lottery_items_column,
                #     scroll=ft.ScrollMode.HIDDEN,
                #     expand=True,
                # ),
                self.lottery_items_column,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
