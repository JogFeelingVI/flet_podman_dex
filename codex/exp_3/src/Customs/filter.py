# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-24 14:20:46


from .pad import paditem, quickpad
from .jackpot_core import filterFunc
from .DraculaTheme import DraculaColors, RandColor
from .loger import logr
import flet as ft
import os
import json
import asyncio
import hashlib


app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


# region FilterChipV2
class FilterChipV2(ft.Container):
    """高度定制 chip"""

    fontSize = 14
    #! f"#{random.randint(0, 0xFFFFFF):06x}"

    def __init__(self, scd: dict, ondelete=None, onclick=None):
        self.selectColor = RandColor()
        super().__init__(data=scd)
        self.padding = 5
        self.content = self.__build__content(scd)
        self.bgcolor = self.ColorOpx(0.1)
        self.border_radius = 8
        # 2. 设置边框：宽度和颜色
        self.border = ft.Border.all(1, self.ColorOpx(0.3))
        # self.on_hover = self.handle_hover
        self.ondelete = ondelete
        self.onclick = onclick

    def handle_right_hover(self, e):
        if e.data:
            self.Cright.content = ft.Icon(
                ft.Icons.DELETE_FOREVER, color=self.ColorOpx(1)
            )
            self.border = ft.Border.all(1, self.ColorOpx(1))
            self.bgcolor = self.ColorOpx(0.4)
        else:
            self.Cright.content = ft.Icon(ft.Icons.DELETE, color=self.ColorOpx(0.3))
            self.border = ft.Border.all(1, self.ColorOpx(0.3))
            self.bgcolor = self.ColorOpx(0.1)

    def handle_left_hover(self, e):
        if e.data:
            self.border = ft.Border.all(1, self.ColorOpx(1))
            self.bgcolor = self.ColorOpx(0.4)
        else:
            self.border = ft.Border.all(1, self.ColorOpx(0.3))
            self.bgcolor = self.ColorOpx(0.1)

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

    def setting_edit_Callback(self, edit_item_callback=None):
        self.editItemCallback = edit_item_callback

    def setting_command_stat(self, add_closed_stat: None):
        self.add_closed_stat = add_closed_stat

    def givefilterall(self):
        return self.filtersAll

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def addFilter(self, scriptd: dict):
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

        if hashcode(_scd, "is") == False:
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
            if self.filtersAll_change == "edit":
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
        self.filtersAll_change = "add"
        self.content.update()
        self.filter_data_task()

    def filter_data_task(self):
        # self.page.session.store.set("filters", fiter_data)
        self.page.session.store.set("filters", self.filtersAll)

    def Custom_Switch(self, onswitch=None):
        """Custom Switch"""
        width = 35
        heigth = 20

        active_color = "#50fa7b"
        default_color = "#a3a3a3"

        def toggle_switch(e):
            if switch.data == "def":
                switch.data = "act"
                switch.alignment = ft.Alignment.CENTER_RIGHT
                switch.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.8, active_color)
                )
                handle.bgcolor = ft.Colors.with_opacity(0.8, active_color)
            else:
                switch.data = "def"
                switch.alignment = ft.Alignment.CENTER_LEFT
                switch.border = ft.Border.all(
                    1, ft.Colors.with_opacity(0.6, default_color)
                )
                handle.bgcolor = ft.Colors.with_opacity(0.8, default_color)
            # end
            if onswitch:
                onswitch(switch)

        handle = ft.Container(
            width=14,
            height=14,
            border_radius=3,
            bgcolor=ft.Colors.with_opacity(0.8, default_color),
        )
        switch = ft.Container(
            data="def",
            width=width,
            height=heigth,
            padding=3,
            border_radius=5,
            alignment=ft.Alignment.CENTER_LEFT,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.6, default_color)),
            animate=ft.Animation(500, "decelerate"),
            bgcolor=ft.Colors.TRANSPARENT,
            content=handle,
            tooltip=ft.Tooltip(message="It saves automatically every 20 seconds."),
            on_click=toggle_switch,
        )

        return switch

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
                        self.Custom_Switch(onswitch=self.handle_switch),
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
        if not isinstance(e, ft.Container):
            return
        if e.data == "def":
            e.badge = None
            return
        self.page.run_task(self.auto_save, e, 10)

    async def auto_save(self, sw: ft.Container, time: int = 10):
        _time = time
        while _time != 0:
            await asyncio.sleep(2)
            _time -= 1
            sw.badge = f"{_time}"
            if self.filtersAll:
                await self.saveTodict()
            if _time == 0:
                _time = time
            if sw.data == "def":
                sw.badge = None
                break
            sw.update()

    async def saveTodict(self):
        if self.filtersAll_change == "none":
            return
        self.page.session.store.set("filters", self.filtersAll)
        stored_id = await ft.SharedPreferences().get("stored_id")
        if not stored_id:
            logr.error("ID not found.")
            return
        try:
            with open(stored_id, "w", encoding="utf-8") as f:
                for item in self.filtersAll:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            logr.info(f"saveTodict is run.")
            self.filtersAll_change = "none"
        except Exception as er:
            logr.info(f"Auto Save error. {er}", exc_info=True)


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
            # border=ft.Border(
            #     top=ft.BorderSide(
            #         1, ft.Colors.with_opacity(0.4, DraculaColors.ORANGE)
            #     ),  # 宽度为 3, 颜色为蓝色
            # ),
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
        return ft.Row(
            data="__load_funxtarget",
            controls=[
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "use ",
                            style=def_text_style,
                        ),
                        ft.TextSpan(
                            "*fun*",
                            style=fun_text_style,
                            on_click=self.handle_func_click,
                        ),
                        ft.TextSpan(" to calculate the target ", style=def_text_style),
                        ft.TextSpan(
                            "*pn*",
                            style=tar_text_style,
                            on_click=self.handle_pn_click,
                        ),
                    ]
                ),
            ],
        )

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
            self.page.show_dialog(ft.SnackBar("pad_data contains null values."))
            return
        if not isinstance(e.control, ft.Chip):
            return
        e.control.label = "Click to add a filter."
        e.control.bgcolor = DraculaColors.GREEN
        # logr.info(f'handle_apply_click {self.pad_data=}')
        if self.applycallback:
            self.applycallback(scriptd=self.pad_data)
        e.control.update()

    def Cratefunc(self, key: str, onclick, iconindex: int = 0):
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
            on_click=lambda _, k=key: onclick(k),
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

    def handle_func_click(self, e):
        def function_click(k):
            if isinstance(e.control, ft.TextSpan):
                e.control.text = f"{k}"
                e.control.data = k
                self.__FT_show.visible = False
                self.pad_data["func"] = f"{k}".strip()
                # self.input_field.value = ""
                self.quickpad.clear_items()

        if self.funcs_dc.__len__() == 0:
            self.funcs_dc = dict(sorted(filterFunc.getFuncName().items()))

        fun_items = []
        for key, item in self.funcs_dc.items():
            fun_items.append(self.Cratefunc(key, function_click))
        self.__FT_show.controls = fun_items
        self.__FT_show.visible = True

    def handle_pn_click(self, e):
        def function_click(k):
            if isinstance(e.control, ft.TextSpan):
                e.control.text = f"{k}"
                e.control.data = k
                self.__FT_show.visible = False
                self.pad_data["target"] = f"{k}".strip()

        try:
            global jackpot_seting
            if not os.path.exists(jackpot_seting):
                return
            with open(jackpot_seting, "r", encoding="utf-8") as f:
                data = json.load(f)
                random_data = data.get("randomData", {})
                self.target_pn = ["all"]
                for key, content in random_data.items():
                    if isinstance(content, dict) and content.get("enabled") is True:
                        self.target_pn.append(key)
            # ? target_pn 已经装载执行下面
            target_pn_items = []
            for key in self.target_pn:
                target_pn_items.append(self.Cratefunc(key, function_click, 1))
            self.__FT_show.controls = target_pn_items
            self.__FT_show.visible = True
        except Exception as e:
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
                self.page.run_task(oncilck, e)
            # Event(name='hover', data=True)
            handle_hover(ft.Event(name="hover",control=conter, data=False))
        # end

        conter = ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, DraculaColors.PURPLE)),
            border_radius=8,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=size * 0.45, color=DraculaColors.PURPLE),
                    ft.Text(
                        value=f"{name.upper()}",
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
        # region update save badge
        async def update_e(e, msg=None):
            e_control: ft.TextButton = e.control
            if not isinstance(e_control, ft.TextButton):
                return
            e_control.badge = f"{msg}"
            e_control.update()
            await asyncio.sleep(3)
            e_control.badge = None
            e_control.update()

        # endregion
        try:
            stored_id = await ft.SharedPreferences().get("stored_id")
            logr.info(f"stored_id: {stored_id}")
            if not stored_id:
                logr.error("ID not found.")
                await update_e(e, "NF")
                return
            save_path = None
            is_mobile_or_web = self.page.web or self.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]

            with open(stored_id, "r", encoding="utf-8") as f:
                content = f.read()
                content_bytes = content.encode("utf-8")
                logr.info(
                    f"content_bytes: {content_bytes.__sizeof__()} open pick -> save_file."
                )
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
                logr.info("Desktop file save complete.")
            await update_e(e, "done")
        except Exception as er:
            logr.error(f"handle_Save error: {save_path}. {er}", exc_info=True)
            await update_e(e, "error")
        finally:
            logr.info(f"Filter saved successfully. {save_path}")

    async def handle_Open(self, e):
        # region update open badge
        async def update_e(e, msg=None):
            e_control: ft.TextButton = e.control
            if not isinstance(e_control, ft.TextButton):
                return
            e_control.badge = f"{msg}"
            e_control.update()
            await asyncio.sleep(1)
            e_control.badge = None
            e_control.update()

        # endregion

        stored_id = await ft.SharedPreferences().get("stored_id")
        if not stored_id:
            logr.error("ID not found.")
            await update_e(e, "NF")
            return

        fiter_data = []
        if self.filter_clear_all:
            self.filter_clear_all()
            await update_e(e, "CA")
        try:
            with open(stored_id, "r", encoding="utf-8") as f:
                for line in f:
                    # 去掉行尾换行符并确保行不为空
                    line = line.strip()
                    if line:
                        # 将每一行的 JSON 字符串转回字典对象
                        item = json.loads(line)
                        fiter_data.append(item)
                        if self.filterAddItem:
                            self.filterAddItem(item)
        except Exception as er:
            await update_e(e, "ER")
        self.page.session.store.set("filters", fiter_data)
        await update_e(e, len(fiter_data))
        logr.info(f"Reading complete. {len(fiter_data)}")

    async def handle_upload(self, e):
        await asyncio.sleep(0.5)
        logr.info(f"handle upload {e}")
        if e.progress == 1.0 and e.error == None:
            filepath = os.path.join(app_temp_path, f"filter/{e.file_name}")
            logr.info(f"upload Fullpath {filepath}")
            fiter_data = []
            if self.filter_clear_all:
                self.filter_clear_all()
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    # 去掉行尾换行符并确保行不为空
                    line = line.strip()
                    if line:
                        # 将每一行的 JSON 字符串转回字典对象
                        item = json.loads(line)
                        fiter_data.append(item)
                        if self.filterAddItem:
                            self.filterAddItem(item)
            self.page.session.store.set("filters", fiter_data)
            logr.info(f"Reading complete. {len(fiter_data)}")
            os.remove(filepath)

    async def handle_Load(self, e):
        # region update open badge
        async def update_e(e, msg=None):
            e_control: ft.TextButton = e.control
            if not isinstance(e_control, ft.TextButton):
                return
            e_control.badge = f"{msg}"
            e_control.update()
            await asyncio.sleep(3)
            e_control.badge = None
            e_control.update()

        # endregion
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
                await update_e(e, "NS")
                return
            is_mobile_or_web = self.page.web or self.page.platform in [
                # ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]
            if is_mobile_or_web:
                uplpads = [
                    ft.FilePickerUploadFile(
                        self.page.get_upload_url(f"filter/{pick_result[0].name}", 600),
                        "PUT",
                        None,
                        pick_result[0].name,
                    )
                ]
                logr.info(uplpads)
                await pick.upload(uplpads)
                await update_e(e, "web done")
            else:
                logr.info(f"{pick_result[0]}")
                fiter_data = []
                if self.filter_clear_all:
                    self.filter_clear_all()
                with open(pick_result[0].path, "r", encoding="utf-8") as r:
                    for line in r:
                        # 去掉行尾换行符并确保行不为空
                        line = line.strip()
                        if line:
                            # 将每一行的 JSON 字符串转回字典对象
                            item = json.loads(line)
                            fiter_data.append(item)
                            if self.filterAddItem:
                                self.filterAddItem(item)
                self.page.session.store.set("filters", fiter_data)
                logr.info(f"Reading complete. {len(fiter_data)}")
                await update_e(e, len(fiter_data))
        except Exception as er:
            await update_e(e, "error")
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
