# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-10 15:23:07

import asyncio
import hashlib
import os

import flet as ft

from .adbox import adbx
from .asyncredis import RedisAPI
from .byterfiles import BinaryConverter as bc
from .DraculaTheme import DraculaColors, HarmonyColors, RandColor
from .env_manager import env_manager
from .jackpot_core import filterFunc
from .loger import logr
from .pad import quickpad
from .Savedialogbox import CustomSwitch, promptdlg


# region FilterChipV2
class FilterChipV2(ft.Container):
    """高度定制 chip"""

    fontSize = 14

    def __init__(self, scd: dict, ondelete=None, onclick=None):
        self.selectColor = RandColor(mode="neon")
        self.bgc = HarmonyColors(
            base_hex_color=self.selectColor, harmony_type="split", mode="neon"
        )
        super().__init__(data=scd)
        self.padding = 5
        self.content = self.__build__content(scd)
        self.bgcolor = self.ColorOpx(0.1)
        self.border_radius = 8
        # 2. 设置边框：宽度和颜色
        self.border = ft.Border(left=ft.BorderSide(5, self.ColorOpx(0.3)))
        # self.animate = ft.Animation(300, ft.AnimationCurve.EASE)
        self.ondelete = ondelete
        self.onclick = onclick
        # self.on_hover = self.handle_hover

    def handle_right_hover(self, e):
        if e.data:
            self.Cright.content = ft.Icon(
                ft.Icons.DELETE_FOREVER, color=self.ColorOpx(1)
            )
        else:
            self.Cright.content = ft.Icon(ft.Icons.DELETE, color=self.ColorOpx(0.3))
        # self.Cright.update()

    def handle_left_hover(self, e):
        if e.data:
            self.border = ft.Border(left=ft.BorderSide(5, self.ColorOpx(0.9)))
            # self.bgcolor = self.ColorOpx(0.4)
        else:
            self.border = ft.Border(left=ft.BorderSide(5, self.ColorOpx(0.3)))
            # self.bgcolor = self.ColorOpx(0.1)
        # self.Cleft.update()

    def handle_left_click(self, e):
        e.control = self
        if self.onclick:
            self.onclick(e)

    def handle_right_click(self, e):
        e.control = self
        if self.ondelete:
            self.ondelete(e)

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def ColorOpx(self, opacity: float = 1.0):
        return ft.Colors.with_opacity(opacity, self.selectColor)

    def __build__content(self, scd: dict):
        contents = ft.Row(
            tight=True,
            spacing=0,
            controls=[
                left := ft.Container(
                    padding=0,
                    content=ft.Column(
                        tight=True,
                        spacing=0,
                        controls=[
                            ft.Text(
                                value=f"{scd['func']} {scd['target']}",
                                size=self.fontSize,
                                weight="bold",
                                color=self.selectColor,
                            ),
                            ft.Text(
                                value=f"{scd['condition']}",
                                size=self.fontSize - 2,
                                color=self.selectColor,
                            ),
                        ],
                    ),
                    on_click=self.handle_left_click,
                    on_hover=self.handle_left_hover,
                ),
                right := ft.Container(
                    padding=0,
                    on_hover=self.handle_right_hover,
                    on_click=self.handle_right_click,
                    content=ft.Icon(ft.Icons.DELETE, color=self.ColorOpx(0.3)),
                ),
            ],
        )
        self.Cleft = left
        self.Cright = right
        return contents


# endregion


# region FiltersList
class FiltersList(ft.Container):
    def __init__(
        self,
    ):
        super().__init__()
        self.content = self.__command_button()
        self.editItemCallback = None
        self.add_closed_stat = None
        self.filtersAll_change = "none"  # add none del edit
        self.filtersAll = []
        self.filterSeed = set()
        self.bgcolor = ft.Colors.TRANSPARENT
        self.width = float("inf")
        self.padding = 10
        self.border_radius = 10
        self.startedit = False
        self.upstash = None
        self.config_id = "async_jackpot_settings"
        self.local_last_update = 0
        self.upredis_api = None
        self.sync_lock = asyncio.Lock()
        self.needs_update_run = False

    def setting_edit_Callback(self, edit_item_callback=None):
        self.editItemCallback = edit_item_callback

    def setting_command_stat(self, add_closed_stat: None):
        self.add_closed_stat = add_closed_stat

    def givefilterall(self):
        return self.filtersAll

    def did_mount(self):
        self.running = True
        self.page.run_task(self.load_upstash_confing)

    def will_unmount(self):
        self.running = False

    def addFilter(self, scriptd: dict, redis_async: bool = False):
        _scd = scriptd.copy()
        if "" in _scd.values():
            logr.info(f"add filter error {_scd}.")
            return
        if not isinstance(self.content, ft.Row):
            return

        # hash 确认
        def hashcode(scr: dict, cmd: str = "is"):
            scr_obj = f"{scr['func']}{scr['target']}{scr['condition']}"
            scr_hash = hashlib.sha256(scr_obj.encode("utf-8"))
            match cmd.lower().strip():
                case "is":
                    if scr_hash.hexdigest() not in self.filterSeed:
                        self.filterSeed.add(f"{scr_hash.hexdigest()}")
                        return True
                    else:
                        return False
                case "del":
                    if scr_hash.hexdigest() in self.filterSeed:
                        self.filterSeed.remove(scr_hash.hexdigest())
                case _:
                    pass

        if not hashcode(_scd, "is"):
            return

        controls = self.content.controls

        def deleteForE(e):
            if not isinstance(e.control, ft.Container):
                return
            e_chip = e.control
            e_script = e.control.data
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            self.filtersAll_change = "del"
            self.filter_data_task()

        def editForE(e):
            if self.startedit:
                return
            if not isinstance(e.control, ft.Container):
                return
            e_chip = e.control
            e_script = e.control.data
            # logr.info(f"edit {e_chip.data}")
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            if self.editItemCallback:
                self.editItemCallback(e_script)
                self.startedit = True
            if self.add_closed_stat:
                self.add_closed_stat()
            e_chip.update()
            self.filtersAll_change = "edit"
            self.filter_data_task()

        self.filtersAll.append(_scd)
        controls.append(
            # region addend chip
            # FilterChip(_scd, deleteForE, editForE)
            FilterChipV2(_scd, deleteForE, editForE)
            # endregion
        )
        self.startedit = False
        self.filtersAll_change = "add" if not redis_async else "none"
        self.content.update()
        if not redis_async:
            self.filter_data_task()

    def filter_data_task(self):
        b64str = bc.to_base64(self.filtersAll)
        if b64str:
            self.page.session.store.set("filters", b64str)

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            wrap=True,
            controls=[
                ft.Row(
                    width=float("inf"),
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.Text(
                            "Automatic save filter.",
                            size=16,
                            color=DraculaColors.COMMENT,
                            italic=True,
                        ),
                        CustomSwitch(on_change=self.handle_switch),
                    ],
                ),
                # "Various filter commands can be added to narrow down the massive pool of phone numbers."
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )

    def clear_all(self):
        """清空 filter 设置"""
        row = self.content
        if not isinstance(row, ft.Row):
            return
        rows = [x for x in row.controls if isinstance(x, ft.Row)]
        row.controls = rows
        self.filtersAll.clear()
        self.filterSeed.clear()
        row.update()

    def handle_switch(self, e):
        self.page.run_task(self.auto_save, e, 10)

    # region auto_save
    async def auto_save(self, sw: CustomSwitch, time: int = 10):
        _time = time
        # 使用 while True 更符合你周期性重置时间的逻辑
        while sw.value:
            # 建议将 sleep 改为 1 秒，2秒倒计时在 UI 上体验会有一点卡顿感
            await asyncio.sleep(1)

            # 🔴 关键修复：醒来后的第一件事，必须先检查开关是否已经被关闭！
            # 如果关闭了，直接退出，绝对不要再去碰 sw.badge
            if not sw.value:
                sw.setingbadge(-1)
                break

            # 正常倒计时逻辑
            _time -= 1
            sw.setingbadge(_time)

            # 时间到了触发保存
            if _time <= 0:
                await self.perform_full_sync()
                _time = time  # 重置时间，开启下一轮

            # 统一在这里更新 UI
            if self.running:
                sw.update()

    async def perform_full_sync(self):
        """执行完整的同步流程：本地保存 + 云端检测/上传"""
        logr.info(f"run is perform_full_sync. {self.filtersAll_change}")
        if self.sync_lock.locked():
            logr.warning("Sync is already in progress, skipping...")
            return

        async with self.sync_lock:
            try:
                # 1. 首先确保本地数据落盘
                await self._save_to_local()

                # 2. 如果开启了同步，处理云端逻辑
                if self.upstash and self.upstash.get("sync"):
                    await self._sync_with_cloud()
            except Exception as e:
                logr.error(f"Error during sync process: {e}", exc_info=True)

    async def _save_to_local(self) -> bool:
        """核心逻辑：本地保存"""
        if self.filtersAll_change == "none":
            return True  # 没有变动不需要保存

        # 获取存储路径
        stored_id_b64 = await ft.SharedPreferences().get("storedid")
        config_info = bc.from_base64(stored_id_b64)

        if not config_info or "path" not in config_info:
            logr.error("Local save path not found.")
            return False

        if self.filtersAll_change == "none":
            logr.info("Data does not need to be saved.")
            return

        # 保存到磁盘 (MsgPack)
        if bc.save(config_info["path"], self.filtersAll):
            # 更新 Session 缓存
            self.page.session.store.set("filters", bc.to_base64(self.filtersAll))
            logr.info("Local configuration saved. [Local]")
            return True
        return False

    async def _sync_with_cloud(self):
        """核心逻辑：云端同步 (Upstash)"""
        if not self.upredis_api:
            self.upredis_api = RedisAPI(
                url=self.upstash["url"], token=self.upstash["token"]
            )

        # 1. 检查是否有远端更新（避免覆盖别人的更新）
        needs_pull = await self.upredis_api.check_needs_update(
            self.config_id, self.local_last_update
        )

        if needs_pull:
            logr.info("Cloud update detected, pulling...")
            cloud_data = await self.upredis_api.get_sync_data(self.config_id)
            if cloud_data and "data" in cloud_data:
                await self._apply_cloud_data(cloud_data)
                return  # 拉取后不再立即上传，防止冲突

        if self.filtersAll_change in ["none", "cloud"]:
            logr.info("Data does not need to be synchronized. [cloud]")
            return

        # 2. 如果本地是较新的，上传到云端
        settings_b64 = self.page.session.store.get("settings")
        settings = bc.from_base64(settings_b64)

        payload = {"setting": settings, "filters": self.filtersAll}

        # 转换并上传
        payload_b64 = bc.to_base64(payload)
        success, timestamp = await self.upredis_api.save_sync_data(
            self.config_id, payload_b64
        )

        if success:
            self.local_last_update = timestamp
            logr.info(f"Cloud sync completed at {timestamp}")
            self.filtersAll_change = "none"

    async def _apply_cloud_data(self, cloud_raw: dict):
        """将从云端拉取的数据应用到本地 UI 和存储"""
        data = bc.from_base64(cloud_raw.get("data"))
        if not data:
            return

        # 更新本地 Session
        self.page.session.store.set("settings", bc.to_base64(data.get("setting")))
        self.page.session.store.set("filters", bc.to_base64(data.get("filters")))

        # 更新 UI 组件 (注意这里可能会比较耗时)
        self.clear_all()
        for filter_item in data.get("filters", []):
            self.addFilter(filter_item, redis_async=True)
            # 这里的 sleep 可能是为了 UI 渲染，如果 addFilter 很快可以去掉
            await asyncio.sleep(0.05)
        self.filtersAll_change = "cloud"
        self.local_last_update = cloud_raw.get("_updated_at", 0)
        logr.info("Cloud data applied to UI.")

    async def load_upstash_confing(self):
        """界面判断是否已经设置 upstash"""
        b64 = await ft.SharedPreferences().get("upstash")
        self.upstash = bc.from_base64(b64, default={})
        if self.upstash:
            logr.info("Cloud sync config loaded.")

    # endregion


# region InputPad
class InputPad(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgx = RandColor()
        self.applycallback = None
        self.__FT_show = self.__load_FT_show()
        self.funcs_dc = {}
        self.target_pn = ["all"]
        self.pad_data = {"func": "", "target": "", "condition": ""}
        self.search_pos = 0
        self.visible = False
        self.padding = 0
        self.width = float("inf")
        # self.width = 400
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.4, self.bgx))
        self.bgcolor = ft.Colors.with_opacity(0.3, self.bgx)
        self.border_radius = 10
        self.content = self.__Pad()

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def settingApplyCallback(self, applycallback=None):
        self.applycallback = applycallback

    def openPad(self):
        """新增加模式"""
        if not self.running:
            return
        self.visible = not self.visible
        self.update()

    def editePad(self, script: dict):
        """编辑模式"""
        func_target: list = self.inputpad.content.controls
        for item in func_target:
            match item.data:
                case "__load_funxtarget":
                    if not isinstance(item, ft.Row):
                        continue
                    if not isinstance(item.controls[0], ft.Text):
                        continue
                    text_spans = item.controls[0].spans
                    text_spans[1].text = script["func"]
                    text_spans[3].text = script["target"]
                    self.pad_data["func"] = script["func"]
                    self.pad_data["target"] = script["target"]
                    self.pad_data["condition"] = script["condition"]
                case "__quickpad__":
                    if not isinstance(item, quickpad):
                        continue
                    self.quickpad.clear_items()
                    self.quickpad.add_item(script["condition"])
                    # item.value = script["condition"]
                case "__apply_text":
                    if not isinstance(item, ft.Row):
                        continue
                    if not isinstance(item.controls[0], ft.Chip):
                        continue
                    item.controls[0].label = "Click to finish editing."
                    item.controls[0].bgcolor = DraculaColors.ORANGE
                case _:
                    pass
        self.visible = True
        self.update()

    # region quick input
    def __quick_input(self):
        quick = {
            ">": ">{n}",
            "<": "<{n}",
            "bit1": "bit{n}",
            "bit1,2": "bit{n},{n}",
            "mod": "mod{n}",
            "range": "range {n},{n}",
            "list": "{n+}",
            "--": "--{m}",
            "DEL": "DEL",
        }

        def handle_tap(item: str):
            if item == "DEL":
                self.quickpad.pop_item(-1)
            else:
                self.quickpad.add_item(item)

        spans = []
        for key, item in quick.items():
            spans.append(
                ft.Container(
                    key=f"quick_{key}",
                    content=ft.Text(f"{key}", size=17, color=RandColor()),
                    padding=ft.Padding(5, 2, 5, 2),
                    on_click=lambda _, item=item: handle_tap(item),
                )
            )
        self.quick_input = ft.Row(
            spacing=5, expand=True, scroll=ft.ScrollMode.HIDDEN, controls=spans
        )
        return self.quick_input
        # endregion

    def __Pad(self):
        """Add, Apply, Cancel"""
        self.builder_list = []
        self.builder = ft.Container(
            padding=12,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.4, DraculaColors.CRADBG),
            width=float("inf"),
            content=ft.Row(
                spacing=5,
                run_spacing=5,
                wrap=True,
                controls=self.builder_list,
            ),
        )
        self.quickpad = quickpad()
        self.inputpad = ft.Container(
            padding=12,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.6, DraculaColors.CRADBG),
            width=float("inf"),
            content=ft.Column(
                controls=[
                    self.__load_funxtarget(),
                    self.__FT_show,
                    self.quickpad,
                    # self.__command_input(),
                    self.__quick_input(),
                    # ft.Divider(),
                    self.__apply_text(),
                ],
            ),
        )
        return ft.Column(
            data="__Pad",
            spacing=0,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER_LEFT,
                    padding=ft.Padding(12, 5, 12, 5),
                    width=float("inf"),
                    bgcolor=ft.Colors.TRANSPARENT,
                    content=ft.Text(
                        "💡This is a test plan designed to facilitate rapid data entry for filtering projects.",
                        color=DraculaColors.FOREGROUND,
                        size=12,
                        no_wrap=False,
                    ),
                ),
                self.inputpad,
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def __apply_text(self):
        """Click "Apply" to add the filter."""
        return ft.Row(
            data="__apply_text",
            controls=[
                ft.Chip(
                    label="Click to add a filter.",
                    label_text_style=ft.TextStyle(color=DraculaColors.BACKGROUND),
                    bgcolor=DraculaColors.GREEN,
                    on_click=self.handle_apply_click,
                ),
            ],
        )

    # region TextField
    def __command_input(self):
        def input_change(e):
            if not isinstance(e.control, ft.TextField):
                return
            self.pad_data["condition"] = f"{e.control.value}".strip()
            logr.info(f"input change {self.pad_data=}")

        self.input_field = ft.TextField(
            data="__command_input",
            hint_text="exp: bit1,2 range 1,15 --z",
            bgcolor=ft.Colors.with_opacity(0.2, DraculaColors.COMMENT),
            expand=1,
            border=ft.InputBorder.NONE,
            dense=True,
            content_padding=ft.Padding.all(0),
            on_change=input_change,
        )
        return self.input_field

    # endregion

    def __load_funxtarget(self):
        """Use "avg" to calculate the target "pa"."""
        def_text_style = ft.TextStyle(size=14, color=DraculaColors.COMMENT)
        fun_text_style = ft.TextStyle(size=14, color=DraculaColors.ORANGE)
        tar_text_style = ft.TextStyle(size=14, color=DraculaColors.GREEN)
        row_fun_pn = ft.Row(
            data="__load_funxtarget",
            controls=[
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "use ",
                            style=def_text_style,
                        ),
                        tsp_func := ft.TextSpan(
                            "*fun*",
                            style=fun_text_style,
                            on_click=self.handle_func_click,
                        ),
                        ft.TextSpan(" to calculate the target ", style=def_text_style),
                        tsp_pn := ft.TextSpan(
                            "*pn*",
                            style=tar_text_style,
                            on_click=self.handle_pn_click,
                        ),
                    ]
                ),
            ],
        )
        self.tsp_func = tsp_func
        self.tsp_pn = tsp_pn
        return row_fun_pn

    def __load_FT_show(self):
        return ft.Row(
            data="__load_FT_show",
            controls=[],
            wrap=True,
            spacing=2,
            run_spacing=2,
            visible=False,
        )

    def handle_apply_click(self, e):
        allcmds = self.quickpad.all_command()
        self.pad_data["condition"] = allcmds.strip()
        if "" in self.pad_data.values():
            _pdlg = promptdlg(
                title="warning",
                info="Filter parameters cannot be empty..",
                typecolor="warning",
            )
            self.page.show_dialog(_pdlg.adb)
            return
        if not isinstance(e.control, ft.Chip):
            return
        e.control.label = "Click to add a filter."
        e.control.bgcolor = DraculaColors.GREEN
        # logr.info(f'handle_apply_click {self.pad_data=}')
        if self.applycallback:
            self.applycallback(scriptd=self.pad_data)
        e.control.update()

    def Cratefunc(self, key: str, onclick, type: str, iconindex: int = 0):
        if not key or not onclick:
            return
        userColor = RandColor()
        icon = ft.Container(
            content=ft.Text(
                f"{key[iconindex].upper()}",
                size=10,
                weight="bold",
                color=userColor,
                text_align=ft.TextAlign.CENTER,
            ),
            width=20,
            height=20,
            padding=2,
            bgcolor=ft.Colors.with_opacity(0.5, userColor),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, userColor)),
            border_radius=10,
            alignment=ft.Alignment.CENTER,
        )
        func = ft.Container(
            data=f"{key}",
            padding=5,
            bgcolor=ft.Colors.with_opacity(0.1, userColor),
            border_radius=5,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.4, userColor)),
            on_click=lambda _, t=type, k=key: onclick(t, k),
            content=ft.Row(
                tight=True,
                spacing=2,
                controls=[
                    icon,
                    ft.Text(f"{key}", size=14, color=userColor),
                ],
            ),
        )
        return func

    def function_click(self, type="func", k=None):
        self.__FT_show.visible = False
        self.pad_data[type] = f"{k}".strip()
        match type:
            case "func":
                self.tsp_func.text = f"{k}"
                self.quickpad.clear_items()
            case "target":
                self.tsp_pn.text = f"{k}"
        self.update()

    def handle_func_click(self, e):
        if self.funcs_dc.__len__() == 0:
            self.funcs_dc = dict(sorted(filterFunc.getFuncName().items()))

        fun_items = []
        for key, item in self.funcs_dc.items():
            fun_items.append(self.Cratefunc(key, self.function_click, "func", 1))
        self.__FT_show.controls = fun_items
        self.__FT_show.visible = True

    def handle_pn_click(self, e):
        try:
            if not os.path.exists(env_manager.jackpot_seting):
                return
            settings = bc.load(env_manager.jackpot_seting)
            if settings:
                random_data = settings.get("randomData", {})
                self.target_pn = ["all"]
                for key, content in random_data.items():
                    if isinstance(content, dict) and content.get("enabled") is True:
                        self.target_pn.append(key)
            # ? target_pn 已经装载执行下面
            target_pn_items = []
            for key in self.target_pn:
                target_pn_items.append(
                    self.Cratefunc(key, self.function_click, "target", 1)
                )
            self.__FT_show.controls = target_pn_items
            self.__FT_show.visible = True
        except Exception:
            pass


# endregion


# region CommandList
class CommandList(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 12
        self.width = float("inf")
        # width=400,
        # self.border=ft.Border.all(1, DraculaColors.COMMENT)
        self.bgcolor = ft.Colors.TRANSPARENT
        # self.border_radius=10
        self.content = self.__command_button()
        self.addcallback = None
        self.filterAddItem = None
        self.give_data = None
        self.filter_clear_all = None
        self.automatically_save = False

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def setting_filter_clear_all(self, cleal_all: None):
        self.filter_clear_all = cleal_all

    def setting_give_data(self, give_data: None):
        self.give_data = give_data

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

        def handle_long_press(e):
            if onlong:
                self.page.run_task(onlong, e)

        def handle_onclick(e):
            if oncilck:
                self.page.run_task(oncilck, e)
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
            # animate=ft.Animation(300, ft.AnimationCurve.EASE),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=size * 0.45, color=uColor),
                    ft.Text(
                        value=f"{name.upper()}",
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
        command = ft.Row(
            controls=[
                addclose := self.__build_butter(
                    icon=ft.Icons.ADD_CARD,
                    name="ADD",
                    oncilck=self.handle_add,
                ),
                self.__build_butter(
                    icon=ft.Icons.FILE_OPEN,
                    name="open",
                    oncilck=self.handle_Open,
                    onlong=self.handle_long,
                ),
                self.__build_butter(
                    icon=ft.Icons.FILE_DOWNLOAD,
                    name="save",
                    oncilck=self.handle_Save,
                ),
                self.__build_butter(
                    icon=ft.Icons.FILE_UPLOAD,
                    name="load",
                    oncilck=self.handle_Load,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        )
        self.addclose = addclose
        return command

    def setting_edit_stat_open(self):
        # e.control.content = "Add"
        # e.control.icon = ft.Icons.FILTER
        icon, text = self.addclose.content.controls
        if isinstance(icon, ft.Icon):
            icon.icon = ft.Icons.CLOSE
        if isinstance(text, ft.Text):
            text.value = "Closed".upper()

    def setting_add_callback(self, addCallBack=None):
        self.addcallback = addCallBack

    def setting_filte_add_item(self, filterAddItem=None):
        self.filterAddItem = filterAddItem

    async def handle_add(self, e):
        if self.running and self.addcallback:
            self.addcallback()
            icon, text = self.addclose.content.controls
            if isinstance(icon, ft.Icon) and isinstance(text, ft.Text):
                if text.value == "ADD":
                    text.value = "Closed".upper()
                    icon.icon = ft.Icons.CLOSE
                else:
                    text.value = "ADD"
                    icon.icon = ft.Icons.ADD
            self.addclose.update()

    async def handle_Save(self, e):
        filters = self.page.session.store.get("filters")
        _pdlg = promptdlg(
            title="Error", info="read filters is error.", typecolor="error"
        )
        if not filters:
            self.page.show_dialog(_pdlg.adb)
            return
        try:
            is_mobile_or_web = self.page.web or self.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]
            content_bytes = filters.encode("utf-8")
            save_path = await ft.FilePicker().save_file(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["dict"],
                file_name="jackpot_filters.dict",
                src_bytes=content_bytes,
            )
            logr.info(f"save_path: {save_path}")
            if save_path and not is_mobile_or_web:
                with open(save_path, "wb") as f:
                    f.write(content_bytes)
                _pdlg = promptdlg(
                    title="Finish", info=f"{self.page.platform} file save complete."
                )
                self.page.show_dialog(_pdlg.adb)
        except Exception as er:
            _pdlg = promptdlg(
                title="error",
                info=f"{self.page.platform} file save complete.",
                typecolor="error",
            )
            self.page.show_dialog(_pdlg.adb)
        finally:
            logr.info(f"Filter saved {save_path}")

    async def handle_long(self, e):
        def cancel_clear(e):
            self.page.pop_dialog()

        def confirm_clear(e):
            if self.filter_clear_all:
                self.filter_clear_all()
                b64_none = bc.to_base64(None)
                if b64_none:
                    self.page.session.store.set("filters", b64_none)
            self.page.pop_dialog()

        content = ft.Column(
            tight=True,
            width=float("inf"),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Clear all filters",
                            size=18,
                            weight="bold",
                            color=DraculaColors.FOREGROUND,
                        ),
                        ft.IconButton(
                            icon=ft.Icon(
                                ft.Icons.CANCEL, color=DraculaColors.FOREGROUND
                            ),
                            icon_size=20,
                            tooltip=ft.Tooltip(message="Cancel Clear"),
                            on_click=cancel_clear,
                        ),
                    ],
                ),
                ft.Divider(height=1, color=DraculaColors.FOREGROUND),
                ft.Container(
                    padding=ft.Padding(10, 5, 10, 5),
                    margin=ft.Margin(10, 0, 10, 0),
                    width=float("inf"),
                    border_radius=8,
                    bgcolor=DraculaColors.RED,
                    content=ft.Row(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        # vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                value="Yes, Confirm all cleanup!",
                                size=15,
                                color=DraculaColors.FOREGROUND,
                            ),
                        ],
                    ),
                    on_click=confirm_clear,
                ),
            ],
        )
        confirm_dialog = adbx(None, content)
        self.page.show_dialog(confirm_dialog)
        logr.info("long press run cls.")

    async def handle_Open(self, e):
        b64str = await ft.SharedPreferences().get("storedid")
        storedid = bc.from_base64(b64str)
        _pdlg = promptdlg(
            title="tips", info="storedid not found.", typecolor="warning", exittime=3
        )
        if not storedid:
            self.page.show_dialog(_pdlg.adb)
            return

        if self.filter_clear_all:
            self.filter_clear_all()
        try:
            jackpot_setting_content = bc.load(storedid["path"])
            for line in jackpot_setting_content:
                if self.filterAddItem:
                    self.filterAddItem(line)
        except Exception as er:
            _pdlg = promptdlg(
                title="error",
                info=f"File reading error. {er}",
                typecolor="error",
                exittime=5,
            )
            self.page.show_dialog(_pdlg.adb)
            return
        b64str = bc.to_base64(jackpot_setting_content)
        if b64str:
            self.page.session.store.set("filters", b64str)
            _pdlg = promptdlg(
                title="Finish",
                info=f"Reading complete. {len(jackpot_setting_content)}",
                typecolor="info",
            )
            self.page.show_dialog(_pdlg.adb)

    async def handle_upload(self, e):
        await asyncio.sleep(0.5)
        # logr.info(f"handle upload {e}")
        if e.progress == 1.0 and e.error is None:
            filepath = os.path.join(env_manager.app_temp_path, f"filter/{e.file_name}")
            logr.info(f"upload Fullpath {filepath}")
            if self.filter_clear_all:
                self.filter_clear_all()
            with open(filepath, "r", encoding="utf-8") as f:
                temp = f.read()
            load_data = bc.from_base64(temp)
            if not load_data:
                logr.info(f"{load_data} is None.")
                return
            for item in load_data:
                if self.filterAddItem:
                    self.filterAddItem(item)
            self.page.session.store.set("filters", temp)
            os.remove(filepath)

    async def handle_Load(self, e):
        try:
            pick = ft.FilePicker(on_upload=self.handle_upload)
            logr.info("open pick -> pick_files")
            pick_result = await pick.pick_files(
                file_type=ft.FilePickerFileType.CUSTOM,
                allow_multiple=False,
                allowed_extensions=["dict"],
            )
            logr.info(f"selsect file: {pick_result}")
            if not pick_result:
                return
            is_mobile_or_web = (
                self.page.web
                or self.page.platform
                in [
                    # ft.PagePlatform.ANDROID,
                    # ft.PagePlatform.IOS,
                ]
            )
            if is_mobile_or_web:
                uplpads = [
                    ft.FilePickerUploadFile(
                        self.page.get_upload_url(f"filter/{pick_result[0].name}", 600),
                        "PUT",
                        None,
                        pick_result[0].name,
                    )
                ]
                logr.info(f"uplpads: {uplpads}")
                await pick.upload(uplpads)
            else:
                logr.info(f"{pick_result[0]}")
                if self.filter_clear_all:
                    self.filter_clear_all()
                with open(pick_result[0].path, "r", encoding="utf-8") as f:
                    temp = f.read()
                load_data = bc.from_base64(temp)
                if not load_data:
                    return
                for item in load_data:
                    if self.filterAddItem:
                        self.filterAddItem(item)
                self.page.session.store.set("filters", temp)
                logr.info(f"Reading complete. {len(load_data)}")
        except Exception as er:
            logr.error(f"handle_Load error. {er}", exc_info=True)


# endregion


# region FilterPage
class FilterPage:
    """筛选页面类"""

    def __init__(self):
        self.Filters_cmd_list = FiltersList()
        self.Input_Pad = InputPad()
        self.Command_List = CommandList()

        self.Input_Pad.settingApplyCallback(
            applycallback=self.Filters_cmd_list.addFilter
        )
        self.Command_List.setting_add_callback(addCallBack=self.Input_Pad.openPad)
        self.Command_List.setting_give_data(
            give_data=self.Filters_cmd_list.givefilterall
        )
        self.Command_List.setting_filte_add_item(
            filterAddItem=self.Filters_cmd_list.addFilter
        )
        self.Command_List.setting_filter_clear_all(self.Filters_cmd_list.clear_all)
        self.Filters_cmd_list.setting_edit_Callback(self.Input_Pad.editePad)
        self.Filters_cmd_list.setting_command_stat(
            add_closed_stat=self.Command_List.setting_edit_stat_open
        )
        # ? new control
        self.view = self.get_filter_view()

    def get_filter_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Filter",
                    size=25,
                    weight="bold",
                    color=DraculaColors.COMMENT,
                    font_family="RacingSansOne-Regular",
                ),
                ft.Divider(),
                self.Filters_cmd_list,
                self.Input_Pad,
                self.Command_List,
                # ft.Column(
                #     [self.filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True
                # ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )


# endregion
