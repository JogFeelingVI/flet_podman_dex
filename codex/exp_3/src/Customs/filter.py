# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-27 05:21:21

from .ColorTokenizer import Tokenizer, spiltfortarget
from .jackpot_core import filterFunc
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
import flet as ft
import os
import json
import asyncio
import hashlib

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")
# jackpot_filers = os.path.join(app_data_path, "jackpot_filters.dict")


# class UserdirButton(ft.TextButton):
#     def __init__(
#         self,
#     ):
#         super().__init__()
#         self.showimg = ft.Image(
#             src="filter.png",
#             fit=ft.BoxFit.FIT_HEIGHT,
#             width=328 * 0.45,
#             height=112 * 0.45,
#         )
#         self.content = ft.Container(
#             content=self.showimg,
#             # 设置缩放动画：200毫秒，减速曲线
#             animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
#         )
#         self.user_dir = app_data_path

#     def animate_filter(self, flg: int = 1):
#         # 动画逻辑：例如点击后放大并改变颜色
#         scale = 1.2 if flg == 1 else 1.0
#         self.showimg.scale = scale  # 改变颜色
#         self.page.update()
#         # print(f"animate is runing.{self.content.scale} {flg=}")

#     def setting(self, save, load):
#         self.save_funx = save
#         self.load_funx = load

#     def did_mount(self):
#         self.ads = self.ad()
#         self.page.overlay.append(self.ads)
#         self.runing = True
#         self.content.on_long_press = self.handle_long_press

#     def will_unmount(self):
#         self.runing = False

#     async def select_dir(self):
#         stored_dir = await ft.SharedPreferences().get("user_dir")
#         if stored_dir:
#             self.user_dir = stored_dir
#             return self.user_dir

#         if not self.page.web:
#             picked_dir = await ft.FilePicker().get_directory_path(
#                 dialog_title="Please select a directory?"
#             )
#             if picked_dir:
#                 await ft.SharedPreferences().set("user_dir", picked_dir)
#                 self.user_dir = picked_dir
#                 return self.user_dir

#         return self.user_dir

#     def handle_long_press(self):
#         self.animate_filter(1)
#         self.page.run_task(self.select_dir)
#         self.ads.open = True
#         self.page.update()

#     def ad(self):
#         return ft.AlertDialog(
#             title=ft.Text("Filter settings saved"),
#             content=ft.Text("Do you need to save or load jackpot_filters.dict?"),
#             actions=[
#                 ft.TextButton("Save", on_click=self.handle_save),
#                 ft.TextButton(
#                     "Load",
#                     on_click=self.handle_load,
#                 ),
#             ],
#             on_dismiss=lambda _: self.animate_filter(0),
#             actions_alignment=ft.MainAxisAlignment.END,
#         )

#     def handle_save(self):
#         # print(f"{self.user_dir=}")
#         try:
#             if self.save_funx:
#                 self.save_funx(self.user_dir)
#         finally:
#             self.ads.open = False
#             self.page.update()

#     def handle_load(self):
#         # print(f"{self.user_dir=}")
#         try:
#             if self.load_funx:
#                 self.load_funx(self.user_dir)
#         finally:
#             self.ads.open = False
#             self.page.update()


# class AI_Auto_input(ft.TextField):
#     def __init__(self):
#         super().__init__()
#         self.border = ft.InputBorder.UNDERLINE
#         self.expand = True
#         self.on_change = self.on_change_input

#     def did_mount(self):
#         self.runing = True
#         return super().did_mount()

#     def will_unmount(self):
#         self.runing = False
#         return super().will_unmount()

#     def on_change_input(self, e):
#         # print(f"uset input: {self.value}")
#         return
#         self.page.run_task(self.ai_sugguest_set)

#     async def ai_sugguest_set(self):
#         """已经废弃不可食用"""
#         await asyncio.sleep(0.3)
#         # if not self.runing:
#         #     return
#         # if not self.value:
#         #     self.suggestions = []
#         #     self.update()
#         #     return
#         # self.suggestions = AI_gen_sugguest_re(self.value)
#         # self.update()


# class Decrement_Button(ft.Container):
#     """圆形按钮"""

#     def __init__(
#         self,
#         ball_size: int = 32,
#         WH: float = 0.0,
#         Start_Value=1,
#         Loop_Value=20,
#         bgcolor=DraculaColors.RED,
#         onClickOutside=None,
#         onLongPressOutside=None,
#     ):
#         super().__init__()
#         self.data = Start_Value
#         self.Start_Value = Start_Value
#         self.Loop_Value = Loop_Value
#         self.text = f"{self.data}"
#         self.ball_size = ball_size
#         self.content = ft.Text(
#             value=self.text,
#             color=DraculaColors.FOREGROUND,
#             size=self.ball_size * 0.45,
#             weight=ft.FontWeight.BOLD,
#         )
#         self.width = self.ball_size * WH if WH > 0 else self.ball_size
#         self.height = self.ball_size
#         self.bgcolor = bgcolor
#         self.border_radius = self.ball_size / 2
#         self.alignment = ft.Alignment.CENTER
#         self.shadow = ft.BoxShadow(
#             spread_radius=1,
#             blur_radius=4,
#             color="#42000000",
#             offset=ft.Offset(0, 2),
#         )
#         self.onClickOutside_callback = onClickOutside
#         self.onLongPressOutside_callback = onLongPressOutside
#         self.on_click = self.handle_click
#         self.on_long_press = self.handle_long_press

#     def handle_click(self, e):
#         value = self.data
#         value += 1
#         if value > self.Loop_Value:
#             value = 1
#         self.data = value
#         self.content.value = f"{self.data}"
#         print(f"{self.data=} {self.content.value=}")
#         self.update()
#         if self.onClickOutside_callback:
#             self.onClickOutside_callback(e)

#     def handle_long_press(self, e):
#         value = self.data
#         value -= 2
#         if value < self.Start_Value:
#             value = self.Loop_Value
#         self.data = value
#         self.content.value = f"{self.data}"
#         print(f"{self.data=} {self.content.value=}")
#         self.update()
#         if self.onLongPressOutside_callback:
#             self.onLongPressOutside_callback(e)


# class select_fang(ft.Container):
#     def __init__(self, name: str = "1", size=32, on_select=None):
#         super().__init__()
#         self.block_size = size
#         self.content = ft.Text(str(name), size=self.block_size * 0.55)
#         self.width = self.block_size
#         self.height = self.block_size
#         self.border_radius = 5
#         self.alignment = ft.Alignment.CENTER
#         self.animate = ft.Animation(300, ft.AnimationCurve.DECELERATE)  # 颜色切换动画
#         self.bgcolor = DraculaColors.CURRENT_LINE
#         self.on_click = self.handle_click
#         self.name = name
#         self.selected = False
#         self.on_select_callback = on_select

#     def handle_click(self, e):
#         self.selected = not self.selected
#         self.bgcolor = (
#             DraculaColors.PURPLE if self.selected else DraculaColors.CURRENT_LINE
#         )
#         self.update()

#         if self.on_select_callback:
#             self.on_select_callback(e)


# class tary(ft.Row):
#     def __init__(self):
#         super().__init__()
#         self.command = ""
#         self.com_args = {0: 1, 1: 1}
#         self.opet_command = ""
#         self.opet_args = {0: 1, 1: 1}
#         self.weic_comd = ""
#         self.weic_args = []
#         self.gui_size_font = 10
#         self.showcommand = ft.Text(
#             value="wait...", color=DraculaColors.COMMENT, size=12
#         )
#         self.uc_haed = ft.CupertinoSlidingSegmentedButton(
#             thumb_color=DraculaColors.RED,
#             selected_index=0,
#             controls=[
#                 ft.Text("null", size=self.gui_size_font),
#                 ft.Text("bitX", size=self.gui_size_font),
#                 ft.Text("bitX,Y", size=self.gui_size_font),
#                 ft.Text("modX", size=self.gui_size_font),
#             ],
#             on_change=lambda _: self.uc_haed_change(),
#         )
#         self.uc_opet = ft.CupertinoSlidingSegmentedButton(
#             thumb_color=DraculaColors.RED,
#             selected_index=0,
#             controls=[
#                 ft.Text(">", size=self.gui_size_font),
#                 ft.Text("<", size=self.gui_size_font),
#                 ft.Text("range", size=self.gui_size_font),
#             ],
#             on_change=lambda _: self.uc_opet_change(),
#         )
#         self.uc_weic = ft.CupertinoSlidingSegmentedButton(
#             thumb_color=DraculaColors.RED,
#             selected_index=0,
#             controls=[
#                 ft.Text("#", size=self.gui_size_font),
#                 ft.Text("Z", size=self.gui_size_font),
#                 ft.Text("H", size=self.gui_size_font),
#                 ft.Text("J", size=self.gui_size_font),
#                 ft.Text("O", size=self.gui_size_font),
#                 ft.Text("M3", size=self.gui_size_font),
#                 ft.Text("W", size=self.gui_size_font),
#             ],
#             on_change=lambda _: self.uc_weic_change(),
#         )
#         self.uc_haed_row = ft.Row(
#             expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
#         )
#         self.uc_opet_row = ft.Row(
#             expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
#         )
#         self.uc_weic_row = ft.Row(
#             expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
#         )
#         # she zhi
#         self.visible = False
#         self.controls = [
#             #
#             ft.Column(
#                 spacing=5,
#                 controls=[
#                     ft.Divider(),
#                     ft.Row(
#                         controls=[self.uc_haed],
#                         expand=True,
#                     ),
#                     self.uc_haed_row,
#                     ft.Row(
#                         controls=[self.uc_opet],
#                         expand=True,
#                     ),
#                     self.uc_opet_row,
#                     ft.Row(
#                         controls=[self.uc_weic],
#                         expand=True,
#                     ),
#                     self.uc_weic_row,
#                     ft.Row(
#                         controls=[self.showcommand],
#                         expand=True,
#                     ),
#                     ft.Divider(),
#                 ],
#                 expand=True,
#             ),
#         ]
#         # self.tight = True

#     def did_mount(self):
#         self.uc_haed_change()
#         self.uc_opet_change()
#         self.uc_weic_change()
#         return super().did_mount()

#     def buil_command(self):
#         """格式化命令行"""
#         command = ""
#         match self.command:
#             case "bitX":
#                 command = f"bit{self.com_args[0]}"
#             case "bitX,Y":
#                 command = f"bit{self.com_args[0]},{self.com_args[1]}"
#             case "modX":
#                 command = f"mod{self.com_args[0]}"
#             case _:
#                 pass

#         command_opet = ""
#         match self.opet_command:
#             case ">":
#                 command_opet = f">{self.opet_args[0]}"
#             case "<":
#                 command_opet = f"<{self.opet_args[0]}"
#             case "range":
#                 command_opet = f"range {self.opet_args[0]},{self.opet_args[1]}"
#             case _:
#                 pass

#         command_weic = ""
#         match self.weic_comd:
#             case "--z":
#                 command_weic = "--z"
#             case "--h":
#                 command_weic = "--h"
#             case "--j":
#                 command_weic = "--j"
#             case "--o":
#                 command_weic = "--o"
#             case "--m3":
#                 if self.weic_args:
#                     command_weic = f"--m3{''.join(map(str, self.weic_args))}"

#             case "--w":
#                 if self.weic_args:
#                     command_weic = f"--w{''.join(map(str, self.weic_args))}"

#             case _:
#                 command_weic = ""

#         all_command = [command, command_opet, command_weic]
#         self.showcommand.value = " ".join(all_command)

#     def loop_number_click(self, e, command, com_args):
#         value = e.control.data
#         self.command = command
#         self.com_args[com_args] = value
#         self.buil_command()

#     def loop_number_long(self, e, command, com_args):
#         value = e.control.data
#         self.command = command
#         self.com_args[com_args] = value
#         self.buil_command()

#     def uc_haed_change(self):
#         select_index = self.uc_haed.selected_index
#         flg_text = self.uc_haed.controls[select_index].value
#         new_row = []
#         match flg_text:
#             case "null":
#                 self.uc_haed_row.visible = False
#             case "bitX":
#                 new_row = [
#                     ft.Text("bit"),
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e,
#                         c=f"bitX",
#                         ca=0: self.loop_number_click(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="bitX",
#                         ca=0: self.loop_number_long(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=20,
#                     ),
#                 ]
#             case "bitX,Y":
#                 new_row = [
#                     ft.Text("bit"),
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e,
#                         c=f"bitX,Y",
#                         ca=0: self.loop_number_click(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="bitX,Y",
#                         ca=0: self.loop_number_long(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=20,
#                     ),
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.COMMENT,
#                         onClickOutside=lambda e,
#                         c=f"bitX,Y",
#                         ca=1: self.loop_number_click(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="bitX,Y",
#                         ca=1: self.loop_number_long(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=20,
#                     ),
#                 ]
#             case "modX":
#                 new_row = [
#                     ft.Text("mod"),
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e,
#                         c=f"modX",
#                         ca=0: self.loop_number_click(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="modX",
#                         ca=0: self.loop_number_long(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=20,
#                     ),
#                 ]
#         self.uc_haed_row.controls = new_row
#         self.uc_haed_row.visible = True
#         self.command = flg_text
#         self.buil_command()
#         self.update()

#     def select_opt_change(self, e, opet, i):
#         value = e.control.data
#         self.opet_command = opet
#         self.opet_args[i] = value
#         self.buil_command()
#         # print(f"select opt {e.control.value}")

#     def uc_opet_change(self):
#         select_index = self.uc_opet.selected_index
#         flg_text = self.uc_opet.controls[select_index].value
#         new_row = []
#         #! 在安卓系统下极其难用
#         match flg_text:
#             case ">":
#                 new_row = [
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e, c=f">", ca=0: self.select_opt_change(
#                             e, c, ca
#                         ),
#                         onLongPressOutside=lambda e,
#                         c=">",
#                         ca=0: self.select_opt_change(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=160,
#                     ),
#                 ]
#             case "<":
#                 new_row = [
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e, c=f"<", ca=0: self.select_opt_change(
#                             e, c, ca
#                         ),
#                         onLongPressOutside=lambda e,
#                         c="<",
#                         ca=0: self.select_opt_change(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=160,
#                     ),
#                 ]
#             case "range":
#                 new_row = [
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.CURRENT_LINE,
#                         onClickOutside=lambda e,
#                         c=f"range",
#                         ca=0: self.select_opt_change(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="range",
#                         ca=0: self.select_opt_change(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=160,
#                     ),
#                     Decrement_Button(
#                         ball_size=25,
#                         WH=1.65,
#                         bgcolor=DraculaColors.COMMENT,
#                         onClickOutside=lambda e,
#                         c=f"range",
#                         ca=1: self.select_opt_change(e, c, ca),
#                         onLongPressOutside=lambda e,
#                         c="range",
#                         ca=1: self.select_opt_change(e, c, ca),
#                         Start_Value=1,
#                         Loop_Value=160,
#                     ),
#                 ]
#         self.uc_opet_row.controls = new_row
#         self.uc_opet_row.visible = True
#         self.opet_command = flg_text
#         self.buil_command()
#         self.update()

#     def chip_select(self, e):
#         label_value = e.control.name
#         isSelect = e.control.selected
#         size = e.control.block_size
#         if isSelect:
#             if label_value not in self.weic_args:
#                 self.weic_args.append(label_value)
#         else:
#             if label_value in self.weic_args:
#                 self.weic_args.remove(label_value)
#         self.buil_command()
#         print(f"{label_value} is select {isSelect} {self.weic_args} {size=}")

#     def uc_weic_change(self):
#         select_index = self.uc_weic.selected_index
#         flg_text = self.uc_weic.controls[select_index].value
#         new_row = []
#         match flg_text:
#             case "Z":
#                 self.weic_comd = "--z"
#             case "H":
#                 self.weic_comd = "--h"
#             case "J":
#                 self.weic_comd = "--j"
#             case "O":
#                 self.weic_comd = "--o"
#             case "M3":
#                 self.weic_comd = "--m3"
#                 new_row = [
#                     select_fang(name=i, size=25, on_select=self.chip_select)
#                     for i in [0, 1, 2]
#                 ]
#             case "W":
#                 self.weic_comd = "--w"
#                 new_row = [
#                     select_fang(name=i, size=20, on_select=self.chip_select)
#                     for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#                 ]
#             case _:
#                 self.weic_comd = ""
#         self.uc_weic_row.controls = new_row
#         self.uc_weic_row.visible = True
#         self.weic_args = []
#         self.buil_command()
#         self.update()
#         # print(f"run uc_weic_change done.")


_ = r"""_|_|_|_|  _|  _|    _|                                    _|        _|              _|      
_|            _|  _|_|_|_|    _|_|    _|  _|_|    _|_|_|  _|              _|_|_|  _|_|_|_|  
_|_|_|    _|  _|    _|      _|_|_|_|  _|_|      _|_|      _|        _|  _|_|        _|      
_|        _|  _|    _|      _|        _|            _|_|  _|        _|      _|_|    _|      
_|        _|  _|      _|_|    _|_|_|  _|        _|_|_|    _|_|_|_|  _|  _|_|_|        _|_|  """


class FiltersList(ft.Card):
    def __init__(
        self,
    ):
        super().__init__()
        self.content = self.__build_card()
        self.editItemCallback = None
        self.add_closed_stat = None
        self.filtersAll_change = "none"  # add none del edit
        self.filtersAll = []
        self.filterSeed = set()

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

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.ORANGE),
            border_radius=10,
            content=self.__command_button(),
        )

    def targetspan(self, text: str):
        split_wc = spiltfortarget(text)
        spans = []
        for ttext, color in split_wc:
            spans.append(
                ft.TextSpan(
                    ttext,
                    style=ft.TextStyle(color=color if color else ft.Colors.WHITE),
                )
            )
        return spans

    def tokenspan(self, text: str):
        segments = Tokenizer().Segment(text)
        spans = []
        for text, color in segments:
            spans.append(
                ft.TextSpan(
                    text,
                    style=ft.TextStyle(color=color if color else ft.Colors.WHITE),
                )
            )
        return spans

    def addFilter(self, scriptd: dict):
        _scd = scriptd.copy()
        if "" in _scd.values():
            print(f"add filter error {_scd}")
            return
        if not isinstance(self.content.content, ft.Row):
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

        controls = self.content.content.controls

        def deleteForE(e):
            if not isinstance(e.control, ft.Chip):
                return
            e_chip = e.control
            e_script = e.control.data
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            self.filtersAll_change = "del"

        def editForE(e):
            if not isinstance(e.control, ft.Chip):
                return
            e_chip = e.control
            e_script = e.control.data
            # print(f"edit {e_chip.data}")
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            if self.editItemCallback:
                self.editItemCallback(e_script)
            if self.add_closed_stat:
                self.add_closed_stat()
            e_chip.update()
            self.filtersAll_change = "edit"

        self.filtersAll.append(_scd)
        controls.append(
            ft.Chip(
                data=_scd,
                label=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Text(
                            spans=self.targetspan(f"{_scd['func']} {_scd['target']}"),
                            size=14,
                        ),
                        ft.Text(spans=self.tokenspan(f"{_scd['condition']}"), size=14),
                    ],
                ),
                # leading=ft.Icon(ft.Icons.FILTER_ALT),
                label_padding=ft.Padding.only(left=3),
                padding=3,
                delete_icon=ft.Container(
                    content=ft.Icon(
                        ft.Icons.DELETE_FOREVER,
                        color=DraculaColors.RED,
                        size=20,
                        margin=0,
                    ),
                    margin=ft.Margin.all(0),
                    padding=0,
                ),
                # delete_icon_color=DraculaColors.RED,
                on_delete=deleteForE,
                on_click=editForE,
            )
        )
        self.filtersAll_change = "add"
        self.content.content.update()
        self.filter_data_task()

    def filter_data_task(self):
        # self.page.session.store.set("filters", fiter_data)
        self.page.session.store.set("filters", self.filtersAll)

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            wrap=True,
            controls=[
                ft.Switch(
                    value=False,
                    on_change=self.handle_switch,
                    tooltip=ft.Tooltip(
                        message="It saves automatically every 20 seconds."
                    ),
                ),
                # "Various filter commands can be added to narrow down the massive pool of phone numbers."
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )

    def handle_switch(self, e):
        switch = e.control
        if not isinstance(switch, ft.Switch):
            return
        if not switch.value:
            switch.badge = None
            return
        self.page.run_task(self.auto_save, switch, 10)

    async def auto_save(self, sw: ft.Switch, time: int = 10):
        _time = time
        while _time != 0:
            await asyncio.sleep(2)
            _time -= 1
            sw.badge = f"{_time}"
            if self.filtersAll:
                self.page.run_task(self.saveTodict)
            if _time == 0:
                _time = time
            if not sw.value:
                sw.badge = None
                break
            sw.update()

    async def saveTodict(self):
        if self.filtersAll_change == "none":
            return
        self.page.session.store.set("filters", self.filtersAll)
        filter_path = await ft.SharedPreferences().get("filter_path")
        if self.page.web and not filter_path:
            filter_path = os.path.join(app_data_path, "jackpot_filters.dict")
        elif not filter_path:
            user_dir_path = await ft.SharedPreferences().get("user_dir")
            user_dir_path = user_dir_path if user_dir_path else app_data_path
            filter_path = os.path.join(user_dir_path, "jackpot_filters.dict")
        try:
            with open(filter_path, "w", encoding="utf-8") as f:
                for item in self.filtersAll:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            print(f"saveTodict is run.")
            self.filtersAll_change = "none"
        except Exception as ex:
            print(f'Auto Save error {ex}')


class InputPad(ft.Card):
    def __init__(self):
        super().__init__()
        self.applycallback = None
        self.visible = False
        self.__FT_show = self.__load_FT_show()
        self.content = self.__build_card()
        self.funcs_dc = {}
        self.target_pn = ["all"]
        self.pad_data = {"func": "", "target": "", "condition": ""}

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
        func_target: list = self.content.content.controls
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
                    # print(f"editPad {self.pad_data=} {text_spans[1].text=}")
                case "__command_input":
                    if not isinstance(item, ft.TextField):
                        continue
                    item.value = script["condition"]
                case "__apply_text":
                    # print('__apply_text.')
                    if not isinstance(item, ft.Row):
                        continue
                    if not isinstance(item.controls[0], ft.Chip):
                        continue
                    item.controls[0].label = "Click to finish editing."
                case _:
                    pass
        self.visible = True
        self.update()

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.PURPLE),
            border_radius=10,
            content=self.__Pad(),
        )

    def __Pad(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            data="__Pad",
            controls=[
                ft.Text(
                    "This is a test plan designed to facilitate rapid data entry for filtering projects.",
                    color=DraculaColors.PURPLE,
                ),
                self.__load_funxtarget(),
                self.__FT_show,
                ft.Divider(),
                self.__command_input(),
                ft.Divider(),
                self.__apply_text(),
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

    def __command_input(self):
        def input_change(e):
            if not isinstance(e.control, ft.TextField):
                return
            self.pad_data["condition"] = f"{e.control.value}".strip()

        return ft.TextField(
            data="__command_input",
            label="Execute the script",
            hint_text="exp: bit1,2 range 1,15 --z",
            expand=1,
            border=ft.InputBorder.UNDERLINE,
            on_change=input_change,
        )

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
        if "" in self.pad_data.values():
            return
        if not isinstance(e.control, ft.Chip):
            return
        e.control.label = "Click to add a filter."
        # print(f'handle_apply_click {self.pad_data=}')
        if self.applycallback:
            self.applycallback(scriptd=self.pad_data)
        e.control.update()

    def handle_func_click(self, e):
        def function_click(k):
            if isinstance(e.control, ft.TextSpan):
                e.control.text = f"{k}"
                e.control.data = k
                self.__FT_show.visible = False
                self.pad_data["func"] = f"{k}".strip()

        if self.funcs_dc.__len__() == 0:
            self.funcs_dc = dict(sorted(filterFunc.getFuncName().items()))

        fun_items = []
        for key, item in self.funcs_dc.items():
            fun_items.append(
                ft.Chip(
                    padding=2,
                    label=f"{key}",
                    data=key,
                    leading=ft.Icon(ft.Icons.FUNCTIONS),
                    on_click=lambda _, k=key: function_click(k),
                )
            )
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
                target_pn_items.append(
                    ft.Chip(
                        padding=2,
                        label=f"{key}",
                        data=key,
                        leading=ft.Icon(ft.Icons.FACE),
                        on_click=lambda _, k=key: function_click(k),
                    )
                )
            self.__FT_show.controls = target_pn_items
            self.__FT_show.visible = True
        except Exception as e:
            pass


class CommandList(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.addcallback = None
        self.filterAddItem = None
        self.give_data = None
        self.automatically_save = False

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def setting_give_data(self, give_data: None):
        self.give_data = give_data

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=self.__command_button(),
        )

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    expand=1,
                    key="add_close",
                    icon=ft.Icons.FILTER,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.SAVE,
                    content="Save",
                    on_click=self.handle_Save,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.FILE_OPEN,
                    content="Open",
                    on_click=self.handle_Open,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def setting_edit_stat_open(self):
        # e.control.content = "Add"
        # e.control.icon = ft.Icons.FILTER
        row_controls = self.content.content.controls
        # 查找 key 为 "btn_add" 的控件
        add_close = next((c for c in row_controls if c.key == "add_close"), None)
        if not isinstance(add_close, ft.TextButton):
            return
        add_close.content = "Closed"
        add_close.icon = ft.Icons.CLOSE

    def setting_add_callback(self, addCallBack=None):
        self.addcallback = addCallBack

    def setting_filte_add_item(self, filterAddItem=None):
        self.filterAddItem = filterAddItem

    def handle_add(self, e):
        # self.row_name_char += 1
        # new_row = self.__get_range_count(f"{chr(self.row_name_char)}")
        # temp_len = len(self.content.content.controls)
        # self.content.content.controls.insert(temp_len - 1, new_row)
        if self.running and self.addcallback:
            self.addcallback()
            if isinstance(e.control, ft.TextButton):
                if e.control.content == "Add":
                    e.control.content = "Closed"
                    e.control.icon = ft.Icons.CLOSE
                else:
                    e.control.content = "Add"
                    e.control.icon = ft.Icons.FILTER
                e.control.update()

    async def handle_Save(self, e):
        if not self.give_data:
            return
        fiter_data = self.give_data()
        if not fiter_data:
            return
        self.page.session.store.set("filters", fiter_data)
        filter_path = await ft.SharedPreferences().get("filter_path")
        if self.page.web and not filter_path:
            filter_path = os.path.join(app_data_path, "jackpot_filters.dict")
            print(f"web mode {filter_path}")
        elif not filter_path:
            user_dir_path = await ft.SharedPreferences().get("user_dir")
            user_dir_path = user_dir_path if user_dir_path else app_data_path
            filter_path = os.path.join(user_dir_path, "jackpot_filters.dict")
            print(f"window linux ios android {filter_path}")
        try:
            with open(filter_path, "w", encoding="utf-8") as f:
                for item in fiter_data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
        except Exception as ex:
            print(f"Default write error, insufficient permissions. {ex}")
            json_lines = "\n".join(
                [json.dumps(item, ensure_ascii=False) for item in fiter_data]
            )
            content_bytes = json_lines.encode("utf-8")
            save_path = await ft.FilePicker().save_file(
                dialog_title="Select the directory to store the jackpot_filters.dict file.",
                allowed_extensions=["dict"],
                file_name="jackpot_filters.dict",
                initial_directory=await ft.SharedPreferences().get("user_dir"),
                src_bytes=content_bytes,
            )
            if save_path:
                await ft.SharedPreferences().set("filter_path", save_path)
                print(f"Filter saved successfully. {save_path}")

    async def handle_Open(self, e):
        filter_path = await ft.SharedPreferences().get("filter_path")
        if self.page.web and not filter_path:
            filter_path = os.path.join(app_data_path, "jackpot_filters.dict")
            print(f"web mode {filter_path}")
        elif not filter_path:
            user_dir_path = await ft.SharedPreferences().get("user_dir")
            user_dir_path = user_dir_path if user_dir_path else app_data_path
            filter_path = os.path.join(user_dir_path, "jackpot_filters.dict")
            print(f"window linux ios android {filter_path}")

        try:
            fiter_data = []
            with open(filter_path, "r", encoding="utf-8") as f:
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
        except Exception as ex:
            print(f"Default read error, insufficient permissions. {ex}")
            select_files = await ft.FilePicker().pick_files(
                dialog_title="Select the directory to store the jackpot_filters.dict file.",
                allowed_extensions=["dict"],
                allow_multiple=False,
                initial_directory=await ft.SharedPreferences().get("user_dir"),
            )
            if select_files:
                newPath = select_files[0].path
                fiter_data = []
                with open(newPath, "r", encoding="utf-8") as f:
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
                await ft.SharedPreferences().set("filter_path", newPath)
                print(f"Reading complete. {len(fiter_data)}")
        # old code
        # if temp:
        #     jackpot_filters = os.path.join(temp, "jackpot_filters.dict")
        #     fiter_data = []
        #     with open(jackpot_filters, "r", encoding="utf-8") as f:
        #         for line in f:
        #             # 去掉行尾换行符并确保行不为空
        #             line = line.strip()
        #             if line:
        #                 # 将每一行的 JSON 字符串转回字典对象
        #                 item = json.loads(line)
        #                 fiter_data.append(item)
        #                 if self.filterAddItem:
        #                     self.filterAddItem(item)
        #     self.page.session.store.set("filters", fiter_data)


#
#
# FilterPage
#
#


class FilterPage:
    """筛选页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
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
        self.Filters_cmd_list.setting_edit_Callback(self.Input_Pad.editePad)
        self.Filters_cmd_list.setting_command_stat(
            add_closed_stat=self.Command_List.setting_edit_stat_open
        )
        # ? new control
        self.view = self.get_filter_view()

    def get_filter_view(self):
        return ft.Column(
            controls=[
                ft.Image(
                    src="filter.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=328 * 0.45,
                    height=112 * 0.45,
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
