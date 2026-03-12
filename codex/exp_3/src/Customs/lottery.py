# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-10 07:42:36


from .Savedialogbox import savedialog, tadbx
from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor, HarmonyColors
from .loger import logr
import flet as ft
import os
import asyncio
import time
import re
import random
import requests

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


# region itemC2plus
class itemC2plus(ft.Container):
    def __init__(self):
        super().__init__()
        self.timeout = 60
        self.is_refreshing = False
        self.running = False
        self.Itemc2_remove = None
        self.fontSize = 25
        self.selected = False
        self.calc_task_running = False  # 控制后台计算任务是否在运行
        self.state_exp = "init"  # 状态: init, calculating, done, timeout, error
        self.elapsed_time = 0.0  # 记录已消耗时间
        self.tempd = None  # 记录计算结果
        self.start_time = 0.0
        # 参数
        self.userColor = RandColor(mode="neon")
        self.bgc = HarmonyColors(
            base_hex_color=self.userColor, harmony_type="split", mode="neon"
        )
        self.padding = 8
        self.border_radius = 10
        self.gradient = ft.LinearGradient(
            colors=[ft.Colors.with_opacity(0.2, x) for x in self.bgc]
        )
        self.content = self.__build_content()
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE)

    # region generate_data_background
    async def generate_data_background(self, name: str):
        if self.calc_task_running:
            return  # 如果已经在后台计算了，就不重复启动

        logr.info(f"Start Data Generation {name}")
        self.calc_task_running = True
        self.state_exp = "calculating"
        self.start_time = time.time()

        try:
            while self.state_exp == "calculating":
                # 后台计算数据
                tempd, state = await asyncio.to_thread(self.calculate_lottery)
                current_time = time.time()
                self.elapsed_time = current_time - self.start_time

                if state:
                    # 计算成功
                    self.tempd = tempd
                    self.state_exp = "done"
                    break  # 退出计算循环
                else:
                    # 超时判断
                    if self.elapsed_time >= self.timeout:
                        self.state_exp = "timeout"
                        break
                await asyncio.sleep(0.3)  # 给CPU喘息的机会

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
            if self.state_exp in ["done", "timeout", "error"]:
                break

            await asyncio.sleep(0.3)  # UI 刷新频率

    # ==========================================
    # 辅助方法：根据当前状态渲染界面
    # ==========================================
    def sync_ui_to_state(self):
        # 安全检查：防止在 unmount 的瞬间调用更新
        if self.running == False:
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

        elif self.state_exp == "done":
            self.showNumber.controls = self.displayNumbers(self.tempd).controls

        elif self.state_exp == "timeout":
            self.showNumber.controls = self.displayshow(
                f"Timeout after {self.elapsed_time:.2f}s"
            ).controls

        elif self.state_exp == "error":
            self.showNumber.controls = self.displayshow(
                f"TProgram execution error."
            ).controls

        self._last_state_exp = self.state_exp

        self.showNumber.update()

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

    def displayNumbers(self, text: str, size: int = 35):
        """用环形标示 标识出数字"""
        result = re.findall(r"\d+|\+", text)
        row = ft.Row(
            wrap=False,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=5,
        )
        colors = [["#d9dbdf", "#747fdf"], ["#eab425", "#fbbf24"]]
        quan, shuzi = colors[0]
        for key in result:
            if key == "+":
                quan, shuzi = colors[1]
                continue
            item = ft.Container(
                content=ft.Text(
                    value=f"{key}",
                    size=size * 0.5,  # 字体大小约为容器的一半
                    weight=ft.FontWeight.BOLD,
                    color=shuzi,  # 文字建议也用金色系或对比色
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ft.Colors.TRANSPARENT,  # 背景透明
                border=ft.Border.all(1, quan),
                width=size,
                height=size,
                border_radius=size / 2,
                alignment=ft.Alignment.CENTER,
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
        if not self.calc_task_running and self.state_exp not in [
            "done",
            "timeout",
            "error",
        ]:
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

    def __build_check(self, size: int = 30):
        def toggle_icon(e):
            # 切换选中状态
            if self.state_exp != "done":
                return
            # e.control.selected = not e.control.selected
            # e.control.update()
            self.selected = not self.selected
            self.check.bgcolor = (
                ft.Colors.with_opacity(0.6, RandColor(mode="neon", hue="Green"))
                if self.selected
                else None
            )
            rows: ft.Column = self.content
            rows.controls[1].visible = not self.selected
            if self.selected:
                self.border = ft.Border(
                    left=ft.BorderSide(5, ft.Colors.with_opacity(1, self.userColor)),
                )
            else:
                # self.border_radius = 10
                self.border = None

            if self.adjust_position and self.selected:
                self.adjust_position(self)
                logr.info("adjust_position is self.")
            self.update()
            # end

        self.check = ft.Container(
            padding=5,
            content=ft.Icon(
                ft.Icons.CHECK, color=DraculaColors.FOREGROUND, size=size * 0.6
            ),
            width=size,
            height=size,
            border_radius=size / 2,
            alignment=ft.Alignment.CENTER,
            on_click=toggle_icon,
        )
        return self.check

    def __build_Butter(self, size=30, icon=ft.Icons.REFRESH, onclick=None):
        butter = ft.Container(
            # padding=5,
            content=ft.Icon(icon, color=self.userColor, size=size),
            # width=size,
            # height=size,
            # border_radius=size / 2,
            # alignment=ft.Alignment.CENTER,
            on_click=onclick,
        )
        return butter

    def __build_content(self):
        content = ft.Column(
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
                        self.__build_Butter(
                            26, ft.Icons.REFRESH, self.handle_refresh_data
                        ),
                        self.__build_Butter(
                            26, ft.Icons.DELETE_FOREVER, self.handle_delete
                        ),
                    ],
                ),
            ],
        )
        self.showNumber = shownumber
        return content

    def setting_Itemc2_Remove(self, itemc2remove=None):
        self.Itemc2_remove = itemc2remove

    def refresh(self, name: str = "None"):
        if self.calc_task_running or self.selected:
            return
        # logr.info(f"markdata is running. {name}")
        self.state_exp = "calculating"
        self.page.run_task(self.generate_data_background, name=name)
        self.sync_ui_to_state()

        # 3. 如果后台还在计算中，启动 UI 刷新轮询
        if self.state_exp == "calculating":
            self.page.run_task(self.ui_update_loop)

    def calculate_lottery(self):
        settings = self.page.session.store.get("settings")
        filters = self.page.session.store.get("filters")
        if settings:
            rd = randomData(seting=settings["randomData"])
        else:
            return ("No settings", False)
        result = rd.get_pabc()
        if not filters:
            return (rd.get_exp(result), True)
        filter_jp = filter_for_pabc(filters=filters)
        if filter_jp.handle(result) == False:
            return (rd.get_exp(result), False)
        return (rd.get_exp(result), True)

    def handle_refresh_data(self, e):
        """右滑逻辑：刷新数据"""
        # logr.info("向右滑动：正在刷新数据...")
        self.refresh(name="refresh_data")
        self.page.show_dialog(ft.SnackBar(f"handle refresh data."))

    def handle_delete(self, e):
        if self.is_refreshing or self.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)
        self.page.show_dialog(ft.SnackBar(f"handle delete."))


# endregion


# region itemsList
class itemsList(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.max_item = 10
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
        self.max_item = 10 if is_mobile_or_web else 1000

    def adjust_position(self, item: itemC2plus):
        if not item:
            return
        control: ft.Column = self.content
        control.controls.remove(item)
        control.controls.insert(0, item)
        control.update()
        logr.info("adjust_position is Done.")

    def add_itemc2(self, itemc2remove=None):
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"add_item type {type(control)}")
            return
        itemc2_len = [
            x
            for x in control.controls
            if isinstance(x, itemC2plus) and x.selected == False
        ].__len__()
        if itemc2_len < self.max_item:
            temp = itemC2plus()
            temp.setting_adjust_position(self.adjust_position)
            temp.setting_Itemc2_Remove(itemc2remove)
            control.controls.append(temp)
            self.update()

    async def all_refresh(self):
        """全部刷新"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        itemc2_all = [x for x in control.controls if isinstance(x, itemC2plus)]
        for item in itemc2_all:
            if item.selected == False:
                item.refresh(name="all_refresh")
                await asyncio.sleep(0.2)

    def get_item_exp(self):
        """"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        exp_all = [
            x.tempd
            for x in control.controls
            if isinstance(x, itemC2plus) and x.selected
        ]
        return exp_all

    def remove_item(self, item: itemC2plus):
        control = self.content
        if not isinstance(control, ft.Column):
            return
        if item:
            control.controls.remove(item)
            self.update()

    def __build_card(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            # wrap=True,
            controls=[],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )


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

    def __build_butter(self, size=70, icon=ft.Icons.ABC, name="ABC", oncilck=None):
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
            # Event(name='hover', data=True)
            handle_hover(ft.Event(name="hover", control=conter, data=False))

        # end
        uColor = RandColor(mode="Morandi")
        conter = ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, uColor)),
            border_radius=8,
            animate=ft.Animation(300, ft.AnimationCurve.EASE),
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
        )
        return conter

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                self.__build_butter(
                    icon=ft.Icons.INSERT_EMOTICON, name="ADD", oncilck=self.handle_add
                ),
                self.__build_butter(
                    icon=ft.Icons.SCIENCE, name="TEST", oncilck=self.handle_test
                ),
                self.__build_butter(
                    icon=ft.Icons.REFRESH, name="REFRESH", oncilck=self.handle_refresh
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
        sdb = savedialog()
        sdb.seting_get_all_exp(self.get_exp_all)
        self.page.show_dialog(sdb.adb)

    def handle_add(self, e):
        """执行add"""
        if self.item_list_add and self.itemc2remove:
            self.item_list_add(self.itemc2remove)

    def handle_refresh(self, e):
        if self.all_refresh:
            self.page.run_task(self.all_refresh)


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
