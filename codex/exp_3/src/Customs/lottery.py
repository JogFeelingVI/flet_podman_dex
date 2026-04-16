# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-13 06:22:54


import asyncio
import random
import re
import time

import flet as ft
import requests

from .byterfiles import BinaryConverter as bc
from .DraculaTheme import DraculaColors, HarmonyColors, RandColor
from .jackpot_core import calculate_lottery_rdffp, initialization
from .loger import logr
from .Savedialogbox import Lotterpng, joblibdlg, operates, tadbx
from .svgbase64 import check_select, svgimage


# region itemC2plus
class itemC2plus(ft.Container):
    def __init__(self, Calculation_Results: str = None):
        super().__init__()
        self.timeout = 60
        self.running = False
        self.Itemc2_remove = None
        self.fontSize = 25
        self.selected = False
        self.calc_task_running = False  # 控制后台计算任务是否在运行
        self.state_exp = (
            "init"  # 状态: init, calculating, done, timeout, error, stopped
        )
        self.elapsed_time = 0.0  # 记录已消耗时间
        self.tempd = None  # 记录计算结果
        # print(f'{self.tempd=}')
        self.start_time = 0.0
        self.rdffp = None
        # 参数
        self.userColor = RandColor(mode="neon")
        self.bgc = HarmonyColors(
            base_hex_color=self.userColor, harmony_type="split", mode="neon"
        )
        self.adjust_position = None
        self.CALCR = ""
        self.padding = 8
        self.border_radius = 10
        self.gradient = ft.LinearGradient(
            colors=[ft.Colors.with_opacity(0.2, x) for x in self.bgc]
        )
        self.content = self.__build_content()
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE)

        if Calculation_Results:
            self.state_exp = "done"
            self.tempd = Calculation_Results
            self.CALCR = "SELECT"

    # region generate_data_background

    def load_rdffp(self, Forced: bool = False):
        if not self.rdffp or Forced:
            logr.info(f"initialization rdffp. Forced is {Forced}.")
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            settings = bc.from_base64(settings)
            filters = bc.from_base64(filters)
            self.rdffp = initialization(settings, filters)

    # 定义一个内部逻辑协程
    async def calculation_loop(self):
        while self.state_exp == "calculating":
            tempd, state = await asyncio.to_thread(calculate_lottery_rdffp, *self.rdffp)
            if state:
                self.tempd = tempd
                self.state_exp = "done"
                break
            self.elapsed_time = time.time() - self.start_time
            await asyncio.sleep(0.3)

    async def generate_data_background(self, name: str):
        if self.calc_task_running:
            return  # 如果已经在后台计算了，就不重复启动

        # logr.info(f"Start Data Generation {name}")
        self.calc_task_running = True
        self.state_exp = "calculating"
        self.start_time = time.time()

        try:
            await asyncio.wait_for(self.calculation_loop(), timeout=self.timeout)
        except asyncio.TimeoutError:
            logr.warning("Data generation timed out.")
            self.state_exp = "timeout"

        except Exception as e:
            logr.error(f"Error in background data generation: {str(e)}", exc_info=True)
            self.state_exp = "error"
        finally:
            self.calc_task_running = False

    # endregion

    # region update ui
    async def ui_update_loop(self):
        # 只要页面在显示（mounted），就持续轮询刷新UI
        while self.running:
            self.sync_ui_to_state()

            # 如果状态已经结束，刷新最后一次后跳出UI轮询
            if self.state_exp in ["done", "timeout", "error", "stopped"]:
                break

            await asyncio.sleep(0.3)  # UI 刷新频率

    # ==========================================
    # 辅助方法：根据当前状态渲染界面
    # ==========================================
    def sync_ui_to_state(self):
        # 安全检查：防止在 unmount 的瞬间调用更新
        if not self.running:
            return

        self.buildBadge.content.value = f"{self.elapsed_time:.2f}"
        self.buildBadge.update()
        # logr.info(f'update time {self.elapsed_time:.2f}')

        last_state = getattr(self, "_last_state_exp", None)
        if self.state_exp == last_state:
            # 如果状态没有发生改变 则直接跳出
            return

        if self.state_exp == "calculating":
            self.showNumber.controls = self.displayshow("Please wait...").controls
            if self.ref_stop.content.icon != ft.Icons.STOP:
                self.ref_stop.content = ft.Icon(ft.Icons.STOP, color=DraculaColors.RED)
                self.ref_stop.update()

        elif self.state_exp == "done":
            self.showNumber.controls = self.displayNumbersv2(self.tempd).controls
            if self.ref_stop.content.icon != ft.Icons.REFRESH:
                self.ref_stop.content = ft.Icon(ft.Icons.REFRESH, color=self.userColor)
                self.ref_stop.update()

        elif self.state_exp == "timeout":
            self.showNumber.controls = self.displayshow(
                f"Timeout after {self.elapsed_time:.2f}s"
            ).controls
            if self.ref_stop.content.icon != ft.Icons.REFRESH:
                self.ref_stop.content = ft.Icon(ft.Icons.REFRESH, color=self.userColor)
                self.ref_stop.update()

        elif self.state_exp == "error":
            self.showNumber.controls = self.displayshow(
                "TProgram execution error."
            ).controls
            if self.ref_stop.content.icon != ft.Icons.REFRESH:
                self.ref_stop.content = ft.Icon(ft.Icons.REFRESH, color=self.userColor)
                self.ref_stop.update()

        elif self.state_exp == "stopped":
            self.showNumber.controls = self.displayshow(
                f"Stopped at {self.elapsed_time:.2f}s"
            ).controls
            if self.ref_stop.content.icon != ft.Icons.REFRESH:
                self.ref_stop.content = ft.Icon(ft.Icons.REFRESH, color=self.userColor)
                self.ref_stop.update()

        self._last_state_exp = self.state_exp

        if self.CALCR == "SELECT":
            e_temp = ft.Event(name="click", control=self.check, data="sync_ui_to_state")
            self.handle_Selected(e_temp)

        self.update()

    # endregion

    def displayshow(self, msg: str, size=35):
        text = ft.Text(
            value=f"{msg}",
            size=size * 0.5,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.with_opacity(0.7, RandColor(mode="neon")),
        )
        row = ft.Row(
            wrap=False,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=5,
            controls=[text],
        )
        return row

    def displayNumbersv2(self, text: str, size: int = 35):
        result = re.findall(r"\d+|\+", text)
        row = ft.Row(
            wrap=False,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=2,
        )
        colors = ["#aab1ee", "#eab425"]
        uc = colors[0]
        for key in result:
            if key == "+":
                uc = colors[1]
                continue
            item = ft.Image(
                src=svgimage(key),
                width=size,
                height=size,
                color=uc,
            )
            row.controls.append(item)
        return row

    def setting_adjust_position(self, adjustposition: None):
        self.adjust_position = adjustposition
        # logr.info(f"setting adjustposition.")

    # region did_mount
    def did_mount(self):
        # if not self.running and not self.is_refreshing and self.state_exp != "done":
        #     # self.refresh(name="did_mount")
        #     self.page.run_task(self.SearchForData, name="did_mount")
        self.running = True

        # 1. 启动后台计算任务（如果还没启动，且当前还没计算完成）
        if (
            not self.calc_task_running
            and self.state_exp
            not in [
                "done",
                "timeout",
                "error",
            ]
            and not self.tempd
        ):
            self.load_rdffp()
            self.state_exp = "calculating"
            self.page.run_task(self.generate_data_background, name="background_task")

        # 2. 页面重新显示时，无条件进行一次UI强同步，保证不漏掉后台已经在算的结果
        # self.sync_ui_to_state()
        # 3. 如果后台还在计算中，启动 UI 刷新轮询
        # if self.state_exp == "calculating":
        self.page.run_task(self.ui_update_loop)

    def will_unmount(self):
        self.running = False

    # endregion

    def __build__badge(self, size: int = 20, text: str = "0"):
        self.buildBadge = ft.Container(
            content=ft.Text(
                f"{text}",
                size=size * 0.5,
                weight="bold",
                color=DraculaColors.FOREGROUND,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.Padding(8, 5, 8, 5),
        )
        return self.buildBadge

    def handle_Selected(self, e):
        if self.state_exp != "done":
            return
        self.selected = not self.selected
        imgcolor = "#d1d1d1" if not self.selected else "#3CFA40"
        self.check.content = ft.Image(
            src=check_select(color=imgcolor), height=30, width=30
        )
        rows: ft.Column = self.content
        rows.controls[1].visible = not self.selected
        if self.selected:
            self.border = ft.Border(
                left=ft.BorderSide(5, ft.Colors.with_opacity(1, self.userColor)),
            )
        else:
            self.border = None
        if self.adjust_position and self.selected:
            self.adjust_position(self)
        self.update()

    def __build_check(self, size: int = 30):
        self.check = ft.Container(
            padding=0,
            bgcolor=ft.Colors.TRANSPARENT,
            content=ft.Image(
                src=check_select(color="#9E9E9E"), height=size, width=size
            ),
            on_click=self.handle_Selected,
        )
        return self.check

    def __build_Butter(self, size=30, icon=ft.Icons.REFRESH, onclick=None):
        butter = ft.Container(
            # padding=5,
            content=ft.Icon(icon, color=self.userColor, size=size),
            on_click=onclick,
        )
        return butter

    def __build_content(self):
        conter = ft.Column(
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=1,
                    controls=[
                        shownumber := self.displayshow("initialization"),
                        self.__build_check(),
                    ],
                ),
                ft.Row(
                    expand=1,
                    spacing=5,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        # self.__build_tips(),
                        self.__build__badge(text="0"),
                        ref_setop := self.__build_Butter(
                            26, ft.Icons.REFRESH, self.handle_refresh_data
                        ),
                        self.__build_Butter(
                            26, ft.Icons.DELETE_FOREVER, self.handle_delete
                        ),
                    ],
                ),
            ],
        )
        self.ref_stop = ref_setop
        self.showNumber = shownumber
        return conter

    def setting_Itemc2_Remove(self, itemc2remove=None):
        self.Itemc2_remove = itemc2remove

    def refresh(self, name: str = "None"):
        if self.calc_task_running or self.selected:
            return
        self.state_exp = "calculating"
        self.ref_stop.content = ft.Icon(ft.Icons.STOP)
        self.load_rdffp(Forced=True)
        self.page.run_task(self.generate_data_background, name=name)
        self.sync_ui_to_state()
        # 3. 如果后台还在计算中，启动 UI 刷新轮询
        if self.state_exp == "calculating":
            self.page.run_task(self.ui_update_loop)

    def handle_refresh_data(self, e):
        """右滑逻辑：刷新数据"""
        # logr.info("向右滑动：正在刷新数据...")
        match self.ref_stop.content.icon:
            case ft.Icons.REFRESH:
                self.refresh(name="handle_refresh_data")
            case ft.Icons.STOP:
                self.state_exp = "stopped"

    def handle_delete(self, e):
        if self.calc_task_running or self.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)


# endregion


# region itemsList
class itemsList(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.max_item = 20
        self.padding = 10
        self.width = float("inf")
        self.bgcolor = ft.Colors.TRANSPARENT

    def did_mount(self):
        self.running = True
        self.find_the_maximum()

    def will_unmount(self):
        self.running = False

    def find_the_maximum(self):
        is_mobile_or_web = self.page.web or self.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        self.max_item = 20 if is_mobile_or_web else 1000

    def adjust_position(self, item: itemC2plus):
        if not item:
            return
        self.mainitems.controls.remove(item)
        self.mainitems.controls.insert(0, item)
        self.mainitems.update()

    def add_itemc2(self, itemc2remove=None, Calculation_Results: str = None):
        itemc2_len = [
            x
            for x in self.mainitems.controls
            if isinstance(x, itemC2plus) and not x.selected
        ].__len__()
        selectlen = self.mainitems.controls.__len__() - itemc2_len
        if itemc2_len < self.max_item and selectlen < self.max_item * 10:
            temp = itemC2plus(Calculation_Results)
            temp.setting_adjust_position(self.adjust_position)
            temp.setting_Itemc2_Remove(itemc2remove)
            self.mainitems.controls.append(temp)
            self.update()

    async def all_refresh(self):
        """全部刷新"""
        itemc2_all = [x for x in self.mainitems.controls if isinstance(x, itemC2plus)]
        for item in itemc2_all:
            if not item.selected:
                item.refresh(name="all_refresh")
                await asyncio.sleep(0.1)

    def get_item_exp(self, max_count: int = 10, data: str = "select") -> list:
        """
        data:
            all
            select [default]
            unselected
        """
        exp_all = []
        reserve = []
        select_flg = []
        match data:
            case "all":
                select_flg = [True, False]
            case "select":
                select_flg = [True]
            case "unselected":
                select_flg = [False]
            case _:
                select_flg = [True]

        # self.state_exp = "calculating"

        for x in self.mainitems.controls:
            # 如果是目标类型 且 已选中 且 提取篮子还没满
            if (
                isinstance(x, itemC2plus)
                and x.selected in select_flg
                and len(exp_all) < max_count
                and x.state_exp != "calculating"
            ):
                exp_all.append(x.tempd)
                # 注意：这里不把 x 放入 reserve，意味着它会被从 UI 中删除
            else:
                # 1. 不是目标类型
                # 2. 或者没被选中
                # 3. 或者已经选满了10个
                # 这些情况统统保留在 UI 中
                reserve.append(x)

        self.mainitems.controls = reserve
        self.mainitems.update()

        return exp_all

    def remove_item(self, item: itemC2plus):
        if item:
            self.mainitems.controls.remove(item)
            self.mainitems.update()

    def __build_card(self):
        """Add, Apply, Cancel"""
        self.mainitems = ft.Column(
            # wrap=True,
            controls=[],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )
        conter = ft.Container(
            padding=0,
            content=self.mainitems,
            on_long_press=self.handle_card_long_press,
        )
        return conter

    def handle_card_long_press(self, e):
        ops = operates()
        ops.setting_callback(self.refresh_callback)
        self.page.show_dialog(ops.adb)

    async def refresh_callback(self, **kwargs):
        logr.info(f"callback data: {kwargs}")
        self.get_item_exp(**kwargs)


# endregion


# region commandList
class commandList(ft.Container):
    def __init__(self):
        super().__init__()
        # self.content = self.__build_card()、
        self.padding = 12
        self.width = float("inf")
        # width=400,
        # self.border=ft.Border.all(1, DraculaColors.COMMENT)
        self.bgcolor = ft.Colors.TRANSPARENT
        # self.border_radius=10
        self.content = self.__command_button()
        # 基本属性
        self.item_list_add = None
        self.itemc2remove = None
        self.all_refresh = None
        self.shot_capture = None
        self.get_exp_all = None

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def setting_get_exp_all(self, getexpall: list = None):
        self.get_exp_all = getexpall

    def setting_shot_capture(self, capture=None):
        self.shot_capture = capture

    def setting_item_list_add(self, itemlistadd=None, itemc2remove=None):
        self.item_list_add = itemlistadd
        self.itemc2remove = itemc2remove

    def setting_all_refresh(self, all_refresh=None):
        self.all_refresh = all_refresh

    def __build_butter(
        self, size=70, icon=ft.Icons.ABC, name="ABC", oncilck=None, onlong=None
    ):
        def handle_hover(e):
            if e.data:
                conter.bgcolor = ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)
                conter.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.4, DraculaColors.PURPLE)
                )
            else:
                conter.bgcolor = None
                conter.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)
                )
            conter.update()

        def handle_onclick(e):
            if oncilck:
                oncilck(e)
            handle_hover(ft.Event(name="hover", control=conter, data=False))

        def handle_long_press(e):
            if onlong:
                self.page.run_task(onlong, e)

        # end
        uColor = RandColor(mode="Morandi")
        conter = ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, uColor)),
            border_radius=8,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=size * 0.45, color=uColor),
                    ft.Text(
                        value=f"{name}",
                        size=size * 0.15,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            on_hover=handle_hover,
            on_click=handle_onclick,
            on_long_press=handle_long_press,
        )
        return conter

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                self.__build_butter(
                    icon=ft.Icons.INSERT_EMOTICON,
                    name="ADD",
                    oncilck=self.handle_add,
                    onlong=self.handle_long_paress,
                ),
                self.__build_butter(
                    icon=ft.Icons.SCIENCE, name="TEST", oncilck=self.handle_test
                ),
                self.__build_butter(
                    icon=ft.Icons.REFRESH,
                    name="REFRESH",
                    oncilck=self.handle_refresh,
                    onlong=self.handle_refresh_long_press,
                ),
                self.__build_butter(
                    icon=ft.Icons.SAVE_AS, name="Export", oncilck=self.handle_export
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    def handle_test(self, e):
        tdb = tadbx()
        self.page.show_dialog(tdb.adb)

    def handle_export(self, e):
        # if self.shot_capture:
        #     self.page.run_task(self.shot_capture)
        # sdb = savedialog()
        # sdb.seting_get_all_exp(self.get_exp_all)
        # sdb.setting_cancel(self.export_callback)
        # self.page.show_dialog(sdb.adb)
        lotter = Lotterpng()
        lotter.seting_get_all_exp(self.get_exp_all)
        self.page.show_dialog(lotter.adb)

    def export_callback(self, exp: list = None):
        if not exp:
            return
        if self.item_list_add and self.itemc2remove:
            for _e in exp:
                self.item_list_add(self.itemc2remove, _e)

    def handle_add(self, e):
        """执行add"""
        if self.item_list_add and self.itemc2remove:
            self.item_list_add(self.itemc2remove)

    async def handle_long_paress(self, e):
        jobadb = joblibdlg()
        jobadb.setting_add_remove(self.item_list_add, self.itemc2remove)
        self.page.show_dialog(jobadb.adb)

    def handle_refresh(self, e):
        if self.all_refresh:
            self.page.run_task(self.all_refresh)

    async def handle_refresh_long_press(self, e):
        ops = operates()
        ops.setting_callback(self.refresh_callback)
        self.page.show_dialog(ops.adb)

    async def refresh_callback(self, **kwargs):
        logr.info(f"callback data: {kwargs}")
        if self.get_exp_all:
            self.get_exp_all(**kwargs)


# endregion


# region luck_tips
class lucktips(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.TRANSPARENT
        self.width = float("inf")
        self.padding = 10
        self.content = self.__build_tips()
        self.cooldown_seconds = 900

    def fetch_random_quote(self):
        """同步方法：负责请求数据和解析数据"""
        # 优化2：将 API URL 和对应的解析逻辑封装在一起，方便扩展
        api_sources = [
            {
                "name": "Hitokoto",
                "url": "https://v1.hitokoto.cn",
                # 解析 hitokoto 的 JSON
                "parse": lambda d: (
                    f"{d.get('hitokoto', 'no motto')} —— {d.get('from_who') or 'Unknown'}"
                ),
            },
            {
                "name": "DummyJSON (英文)",
                "url": "https://dummyjson.com/quotes/random",
                "parse": lambda d: (
                    f"{d.get('quote', 'No content')} —— {d.get('author', 'Unknown')}"
                ),
            },
            {
                "name": "ZenQuotes (英文)",
                "url": "https://zenquotes.io/api/random",
                "parse": lambda d: (
                    f"{d[0].get('q', 'No content')} —— {d[0].get('a', 'Unknown')}"
                    if isinstance(d, list) and len(d) > 0
                    else "Parse Error"
                ),
            },
        ]

        # 随机选择一个 API
        source = random.choice(api_sources)
        logr.info(f"Selected Quote API: {source['name']} - URL: {source['url']}")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(source["url"], headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            # 使用对应 API 的解析函数提取文字
            return source["parse"](data)

        except Exception as ex:
            logr.error(f"Quote API Error ({source['name']}): {ex}")
            # 请求失败时返回默认兜底文案
            return "愿你所有的好运都不期而遇，愿你所有的努力都有岁月的温柔回馈。✨"

    def did_mount(self):
        self.running = True
        self.page.run_task(self.motto_loop)

    def will_unmount(self):
        self.running = False

    async def motto_loop(self):
        """异步循环任务：更新数据并等待 15 分钟"""
        await asyncio.sleep(1)
        while self.running:
            last_fetch_time = self.page.session.store.get("lucktips_last_time") or 0
            cached_quote = self.page.session.store.get("lucktips_last_text")
            current_time = time.time()
            elapsed_time = current_time - last_fetch_time
            if elapsed_time >= self.cooldown_seconds or not cached_quote:
                # 触发真实网络请求
                info = await asyncio.to_thread(self.fetch_random_quote)

                # 更新 Session 缓存（记录新的时间和内容）
                self.page.session.store.set("lucktips_last_time", time.time())
                self.page.session.store.set("lucktips_last_text", info)
            else:
                # 时间没到，直接使用缓存的句子
                info = cached_quote

            # 直接更新文本控件并刷新组件
            self.motto.value = info
            self.motto.update()
            last_fetch_time = self.page.session.store.get("lucktips_last_time")
            remaining_seconds = int(
                (last_fetch_time + self.cooldown_seconds) - time.time()
            )

            # 防止出现负数或 0 死循环
            if remaining_seconds <= 0:
                remaining_seconds = 1

            # 开始倒计时休眠，随时监听 self.running 以便在页面切换时打断休眠
            for _ in range(remaining_seconds):
                if not self.running:
                    return  # 页面被切走，直接结束当前组件的后台循环
                await asyncio.sleep(1)

    def __build_text(self, text: str = "Luck word."):
        self.motto = ft.Text(
            value=f"{text}",
            size=15,
            color=ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND),
            max_lines=2,
        )
        return self.motto

    def __build_tips(self):
        content = ft.Column(
            controls=[
                self.__build_text(
                    "愿你所有的好运都不期而遇，愿你所有的努力都有岁月的温柔回馈。✨"
                )
            ],
        )
        return content


# endregion


# region LotteryPage
class LotteryPage:
    def __init__(self):
        # self.Photograph = Photograph()
        self.itemslist = itemsList()
        self.comandlist = commandList()
        # self.serendipitous_Capture = serendipitousCapture()

        # self.Photograph.setting_get_exp_all(self.itemslist.get_item_exp)
        self.comandlist.setting_item_list_add(
            self.itemslist.add_itemc2, self.itemslist.remove_item
        )
        self.comandlist.setting_get_exp_all(self.itemslist.get_item_exp)
        # self.comandlist.setting_shot_capture(self.Photograph.schot_exp_capture)
        self.comandlist.setting_all_refresh(self.itemslist.all_refresh)
        self.luckTips = lucktips()
        self.view = self.get_data_view()

    # region get_data_view
    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Lotter",
                    size=25,
                    weight="bold",
                    color=DraculaColors.COMMENT,
                    font_family="RacingSansOne-Regular",
                ),
                ft.Divider(),
                self.luckTips,
                self.itemslist,
                self.comandlist,
                # self.Photograph,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    # endregion


# endregion
