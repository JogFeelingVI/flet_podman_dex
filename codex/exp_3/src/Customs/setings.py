# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-19 07:52:10

from .lotteryballs import LotteryBalls
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .jackpot_core import randomData
import flet as ft
import json
import os
import re
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

Lotter_Data = {
    "🔴双色球": {
        "description": "🇨🇳百万富翁缔造者",
        "SA": [1, 33],
        "SB": [1, 16],
        "SA_K": 6,
        "SB_K": 1,
    },
    "⚪快乐8": {
        "description": "🇨🇳你的快乐就是他的快乐",
        "PA": [1, 80],
        "PA_K": 10,
    },
    "✨超级大乐透": {
        "description": "🇨🇳体育大乐透",
        "PA": [1, 35],
        "PB": [1, 12],
        "PA_K": 5,
        "PB_K": 2,
    },
    "🇨🇳排列3/5": {
        "description": "🇨🇳体育排列3/5",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
    },
    "✨七星彩": {
        "description": "🇨🇳体育七星彩",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PF": [0, 9],
        "PG": [0, 14],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
        "PF_K": 1,
        "PG_K": 1,
    },
    "🇺🇸Powerball": {
        "description": "🇺🇸USA Powerball",
        "PA": [1, 69],
        "PB": [1, 26],
        "PA_K": 5,
        "PB_K": 1,
    },
    "🇹🇼威力彩": {
        "description": "🇺🇸台湾省销售最好的彩票",
        "PA": [1, 38],
        "PB": [1, 8],
        "PA_K": 6,
        "PB_K": 1,
    },
}


class input_user_rule(ft.Card):
    def __init__(self, callback=None):
        super().__init__()
        self.visible = False
        self.content = self.__build_card()
        self.callback = callback
        self.row_name_char = 65
        self.templejson = {
            "randomData": {
                "note": "🇨🇳体育排列3/5",
                "PA": {"enabled": True, "range_start": 0, "range_end": 9, "count": 1},
            }
        }

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def openCard(self):
        self.visible = True
        self.update()

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.ADD_BOX,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.WINDOW,
                    content="Apply",
                    on_click=self.handle_Apply,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.CANCEL,
                    content="Cancel",
                    on_click=self.handle_Cancel,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def __get_note(self):
        return ft.TextField(
            label="Note",
            hint_text="Rule Settings Instructions",
            expand=1,
            border=ft.InputBorder.UNDERLINE,
        )

    def __get_range_count(self, name="a"):
        name = name.upper()
        return ft.Row(
            controls=[
                ft.TextField(
                    label=f"P{name.upper()}",
                    expand=2,
                    hint_text="min,max",
                    data=f"{name}_Max",
                    border=ft.InputBorder.UNDERLINE,
                ),
                ft.TextField(
                    label="Count",
                    expand=1,
                    data=f"{name}_K",
                    border=ft.InputBorder.UNDERLINE,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            data=name,
        )

    def __build_card(self):
        return ft.Container(
            padding=12,
            # expand=True,
            # opacity=0.65,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.PINK),
            border_radius=10,
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text("Add new game rules.", size=25),
                    self.__get_note(),
                    self.__get_range_count("a"),
                    self.__command_button(),
                ],
            ),
        )

    def handle_add(self):
        self.row_name_char += 1
        new_row = self.__get_range_count(f"{chr(self.row_name_char)}")
        temp_len = len(self.content.content.controls)
        self.content.content.controls.insert(temp_len - 1, new_row)

    def handle_Cancel(self):
        self.visible = False
        self.update()

    async def handle_Apply(self):
        temp = self.templejson.copy()
        rows = self.content.content.controls
        for _item in rows:
            if isinstance(_item, ft.TextField):
                temp["randomData"]["note"] = _item.value or "Jackptot lotter apk"
                continue
            if isinstance(_item, ft.Row):
                label = ""
                label_value = {}
                for _child_item in _item.controls:
                    if not isinstance(_child_item, ft.TextField):
                        continue
                    if _child_item.label.startswith("P"):
                        label = _child_item.label
                        label_value.update(self.Convert_to_list(_child_item.value))
                    if _child_item.label.startswith("C"):
                        count = (
                            int(_child_item.value) if _child_item.value.isdigit() else 0
                        )
                        label_value.update({"count": count})
                if label == "" or not label_value["enabled"]:
                    continue
                temp["randomData"][label] = label_value
        global jackpot_seting
        print(f"bind temple dict {temp} {jackpot_seting}")
        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(temp, f, indent=4, ensure_ascii=False)
        self.page.session.store.set("settings", temp)
        if self.callback:
            self.callback()
        self.handle_Cancel()

    def Convert_to_list(self, lable_value: str):
        """处理用户输入"""
        if lable_value in [None, ""]:
            return {"enabled": False}
        mathch = re.findall(r"(\d+)", lable_value)
        if mathch:
            value = [int(x) for x in mathch if x.isdigit()]
            range_start = min(value)
            range_end = max(value)
            if range_start == range_end:
                range_start = 0
            return {"range_start": range_start, "range_end": range_end, "enabled": True}
        return {"enabled": False}


class showRule(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()

    def did_mount(self):
        self.running = True
        self.updateCard()

    def will_unmount(self):
        self.running = False

    def updateCard(self):
        self.page.run_task(self.__update_card)

    async def __update_card(self):
        if not self.running:
            return
        await asyncio.sleep(0.5)
        apply_rule = self.page.session.store.get("settings")
        if not apply_rule:
            return
        randomDatax = apply_rule.get("randomData", None)
        if not randomDatax:
            return
        example = randomData(seting=randomDatax).get_exp()
        textlist = [LotteryBalls(example, 32, "LE"), ft.Divider()]
        for key, item in randomDatax.items():
            if key == "note":
                textlist.append(
                    ft.Text(
                        f"🚩Note: {item}",
                        size=15,
                        weight="bold",
                        color=DraculaColors.ORANGE,
                        max_lines=2,
                    )
                )
                continue
            # print(f'{key} {item} ==-==')
            count_range = f"{item['range_start']} - {item['range_end']}"
            count = item["count"]

            textlist.append(
                ft.Text(
                    f"Section [ {key} ].  Choose {count} number from {count_range}.",
                    max_lines=2,
                    color=DraculaColors.PURPLE,
                    size=15,
                )
            )
        self.content.content.controls = textlist
        self.update()

    def __build_card(self):
        print("bulid card is running.")
        return ft.Container(
            padding=12,
            # expand=True,
            # opacity=0.65,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Column(
                tight=True,
                controls=[
                    # LotteryBalls(exp, align="LE"),
                    # ft.Divider(),
                    # *textlist,
                    ft.Text(
                        "💡Please add game rules. You can customize them using [new rule] or use the preset options."
                    ),
                ],
            ),
        )


class DefaultSettings(ft.Card):
    """默认设置指示器"""

    def __init__(self, add_rule=None, callback=None):
        super().__init__()
        self.content = self.__build_card()
        # self.apply_rule = {}
        self.callback = callback
        self.add_rule = add_rule

    def did_mount(self):
        self.running = True
        self.page.run_task(self.__Lotter_Data)

    def will_unmount(self):
        self.running = False

    async def __Lotter_Data(self):
        """加载彩票预设数据并生成按钮"""
        # --- 构造按钮列表 ---
        if self.running:
            await asyncio.sleep(0.5)

            add_rule = ft.Button(
                icon=ft.Icons.RULE,
                content="new rule",
                tooltip=ft.Tooltip(message="new game rule"),
                on_click=self.handle_add_rule,
                # style=ft.ButtonStyle(
                #     shape=ft.RoundedRectangleBorder(radius=2),
                #     color=DraculaColors.FOREGROUND,
                #     bgcolor=DraculaColors.COMMENT,
                #     overlay_color=DraculaColors.PINK,
                #     side=ft.BorderSide(
                #         1,
                #         DraculaColors.FOREGROUND,
                #         ft.BorderSideStrokeAlign.INSIDE,
                #         ft.BorderStyle.SOLID,
                #     ),
                # ),
            )
            button_list = [add_rule]

            # 注意：Lotter_Data 应该在函数外部定义或作为参数传入
            for k, item in Lotter_Data.items():
                description = item.get("description", "")
                button_list.append(
                    ft.TextButton(
                        content=f"{k}",
                        tooltip=ft.Tooltip(message=description),
                        # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                        on_click=lambda e,
                        name=k,
                        data=item,
                        desc=description: self.save_preset_to_file(name, data, desc),
                    )
                )
            self.content.content.controls = button_list
            self.update()

    def handle_add_rule(self, e):
        if self.add_rule:
            self.add_rule()

    def save_preset_to_file(self, name: str, preset_data: dict, desc: str):
        """将处理后的预设数据写入 json 文件"""
        # 1. 构造符合你要求的嵌套格式
        valid_json = {
            "randomData": {
                "note": f"{desc}",
            }
        }

        # 2. 解析 Lotter_Data 项并转换格式
        # 我们需要找到像 SA, SB, PA 这样的键，并匹配对应的 _K 键
        keys = preset_data.keys()
        for k in list(keys):
            # 过滤掉描述字段和数量字段(_K)，只处理 SA, SB, PA 等
            if k == "description" or k.endswith("_K"):
                continue

            count_key = f"{k}_K"
            if count_key in keys:
                # 转换键名：将 SA 转换为 PA, SB 转换为 PB (或者保持原样，取决于你的 UI 需求)
                # 这里假设你的 UI 统一使用 PA, PB, PC，我们做一个简单的映射
                target_key = k.replace("SA", "PA").replace("SB", "PB")

                valid_json["randomData"][target_key] = {
                    "enabled": True,
                    "range_start": preset_data[k][0],
                    "range_end": preset_data[k][1],
                    "count": preset_data[count_key],
                }

        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(valid_json, f, indent=4, ensure_ascii=False)
            # self.page.show_dialog(
            #     get_snack_bar(f"Preset '{name}' has been applied and saved.")
            # )
        self.page.session.store.set("settings", valid_json)
        if self.callback:
            self.callback()

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Row(
                controls=[],
                spacing=2,
                run_spacing=2,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
            ),
        )


class UserDirectory(ft.Card):
    """用户目录指示器"""

    def __init__(self):
        super().__init__()
        self.stored_dir = None
        self.tips = ft.Text(
            "💡 Tip: Set the user directory to store filter files and saved images.",
            color=DraculaColors.FOREGROUND,
            size=12,
            max_lines=2,
            # overflow=ft.TextOverflow.ELLIPSIS,
            no_wrap=False,
        )
        self.button = ft.Button(
            "User Directory",
            icon=ft.Icons.FOLDER_OFF,
            on_click=lambda _: self.page.run_task(self.select_user_dif),
            # style=ft.ButtonStyle(
            #     shape=ft.RoundedRectangleBorder(radius=2),
            #     color=DraculaColors.FOREGROUND,
            #     bgcolor=DraculaColors.COMMENT,
            #     overlay_color=DraculaColors.PINK,
            #     # side=ft.BorderSide(
            #     #     1,
            #     #     DraculaColors.FOREGROUND,
            #     #     ft.BorderSideStrokeAlign.INSIDE,
            #     #     ft.BorderStyle.SOLID,
            #     # ),
            # ),
        )
        self.content = self.__build_card()
        self.count = 10

    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_ui)

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            # width=200,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Row(
                controls=[
                    self.tips,
                    self.button,
                ],
                spacing=5,
                wrap=True,
                # tight=True,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    async def update_ui(self):
        if self.running:
            await asyncio.sleep(0.5)  # 初始延迟，确保页面加载完成

            temp = await self.getuser_dir()
            print(f"Checking user directory...{temp=}")
            if temp:
                self.tips.value = f"📂 User Directory: {temp}"
                self.button.visible = False
                self.page.update()

    async def getuser_dir(self):
        """获取用户目录"""
        temp = await self.page.shared_preferences.get("user_dir")
        if self.page.web:
            temp = app_data_path
        print(f"Fetched user directory: {temp=}")
        return temp

    async def select_user_dif(self):
        if not self.page.web:
            picked_dir = await ft.FilePicker().get_directory_path(
                dialog_title="Please select a directory?"
            )
            if picked_dir:
                await self.page.shared_preferences.set("user_dir", picked_dir)
                await self.update_ui()


class SetingsPage:
    """设置页面类"""

    def __init__(self, page: ft.Page):
        self.page = page

        self.rule_mode_show = showRule()
        self.uese_input_mode = input_user_rule(self.render_filters)
        self.default_setings = DefaultSettings(self.open_dialog, self.render_filters)
        self.apply_rule = {}

        self.view = self.get_seting_view()

    def get_Selection_line(self, Selection_name: str):
        name = f"P{Selection_name}"
        return ft.Row(
            controls=[
                ft.TextField(
                    label=name,
                    expand=2,
                    hint_text="min,max",
                    data=f"{name}_Max",
                    border=ft.InputBorder.UNDERLINE,
                ),
                ft.TextField(
                    label="Count",
                    expand=1,
                    data=f"{name}_K",
                    border=ft.InputBorder.UNDERLINE,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            data=name,
        )

    def render_filters(self):
        """渲染过滤器列表"""
        self.rule_mode_show.updateCard()
        self.page.update()

    def open_dialog(self):
        self.uese_input_mode.openCard()
        # self.dlg.open = True
        self.page.update()

    def get_seting_view(self):
        return ft.Column(
            controls=[
                ft.Image(
                    src="setting.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=475 * 0.45,
                    height=135 * 0.45,
                ),
                # ft.Text("Setting", size=25, weight="bold", color=DraculaColors.COMMENT),
                # 这里可以添加更多的设置控件
                ft.Divider(),
                # ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                # ft.Divider(),
                self.rule_mode_show,
                UserDirectory(),
                self.default_setings,
                self.uese_input_mode,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
