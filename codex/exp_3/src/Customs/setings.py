# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-26 14:46:02

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
    def __init__(self):
        super().__init__()
        self.visible = False
        self.content = self.__build_card()
        self.render_filters = None
        self.row_name_char = 65
        self.templejson = {
            "randomData": {
                "note": "🇨🇳体育排列3/5",
                "PA": {"enabled": True, "range_start": 0, "range_end": 9, "count": 1},
            }
        }

    def setting_render_filters(self, render_filters=None):
        self.render_filters = render_filters

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
        if self.render_filters:
            self.render_filters()
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
    __name__ = "showRule"

    def __init__(self):
        super().__init__()
        self.content = self.__build_card()

    def did_mount(self):
        self.running = True
        try:
            self.updateCard()
        except Exception as e:
            print(f"{self.__name__} running error {e}.")
        finally:
            print(f"{self.__name__} running over.")

    def will_unmount(self):
        self.running = False

    def updateCard(self):
        self.page.run_task(self.__update_card)

    def get_lottery_text(self, exp: str):
        spans = []
        before, sep, after = exp.partition("+")
        # print([before.strip(), sep.strip(), after.strip()])
        # 2. 匹配逻辑
        match [before.strip(), sep.strip(), after.strip()]:
            # 情况 A: 刚好两组数据（如 6+1 模式）
            case [b, s, a] if len(b) > len(a) and s == "+":
                # 第一组（红球）
                spans.append(
                    ft.TextSpan(
                        b,
                        ft.TextStyle(
                            color=DraculaColors.RED, weight=ft.FontWeight.W_900
                        ),
                    )
                )
                # 分隔符
                spans.append(
                    ft.TextSpan(
                        f" {s} ",
                        ft.TextStyle(color=DraculaColors.PURPLE, weight="W_900"),
                    )
                )
                # 第二组（紫/蓝球）
                spans.append(
                    ft.TextSpan(
                        a,
                        ft.TextStyle(color=DraculaColors.PURPLE, weight="W_900"),
                    )
                )

            # 情况 B: 多组数据（3组或更多）
            case [b, s, a] if s == a == "" and b != a:
                spans.append(
                    ft.TextSpan(
                        b, ft.TextStyle(color=DraculaColors.RED, weight="W_900")
                    )
                )
        return ft.Text(
            size=20,
            spans=spans,
        )

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
        # textlist = [LotteryBalls(example, 32, "LE"), ft.Divider()]
        textlist = [self.get_lottery_text(example), ft.Divider()]
        for key, item in randomDatax.items():
            if key == "note":
                textlist.append(
                    ft.Text(
                        f"{item}",
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
            border=ft.Border.all(2, DraculaColors.ORANGE),
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

    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        # self.apply_rule = {}
        self.render_filters = None
        self.add_rule = None

    def setting_add_rule(self, add_rule=None):
        self.add_rule = add_rule

    def setting_render_filters(self, render_filters=None):
        self.render_filters = render_filters

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
                bgcolor=DraculaColors.GREEN,
                color=DraculaColors.BACKGROUND,
                icon=ft.Icons.RULE,
                content="new rule",
                tooltip=ft.Tooltip(message="new game rule"),
                on_click=self.handle_add_rule,
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
        if self.render_filters:
            self.render_filters()

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

    __name__ = "UserDirectory"

    def __init__(self):
        super().__init__()
        self.file_picker = ft.FilePicker()
        self.stored_dir = None
        self.tips = ft.Text(
            "💡 Tip: Set the user directory to store filter files and saved images.",
            color=DraculaColors.FOREGROUND,
            size=16,
            max_lines=2,
            # overflow=ft.TextOverflow.ELLIPSIS,
            no_wrap=False,
        )
        self.select_dir = ft.Button(
            "User Directory",
            icon=ft.Icons.FOLDER_OFF,
            bgcolor=DraculaColors.ORANGE,
            color=DraculaColors.BACKGROUND,
            on_click=lambda _: self.page.run_task(self.select_user_dir),
        )
        self.select_dir_done = False
        self.content = self.__build_card()
        self.count = 10

    def did_mount(self):
        self.running = True
        try:
            if not self.select_dir_done:
                self.page.run_task(self.Checking_user_dir)
        except Exception as e:
            print(f"{self.__name__} running error {e}.")
        finally:
            print(f"{self.__name__} running over.")

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
                    self.select_dir,
                ],
                spacing=5,
                wrap=True,
                # tight=True,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    async def update_tips_value(self, text: str = None):
        if not text:
            return
        self.tips.value = f"{text}"
        self.tips.update()
        await asyncio.sleep(2)

    async def Checking_user_dir(self):
        if self.running:
            await asyncio.sleep(0.5)  # 初始延迟，确保页面加载完成

            temp = await self.getuser_dir()
            if temp:
                await self.update_tips_value(
                    f"Using directory ../{os.path.basename(os.path.normpath(temp))}"
                )
                self.select_dir.visible = False
                self.select_dir.update()
                self.select_dir_done = True

    # async def import_configs(self, path: str):
    #     """Do you want to import the configuration file?"""
    #     default_files = {"jackpot_settings.json":"","jackpot_filters.dict":""}
    #     with os.scandir(path) as entries:
    #         for entry in entries:
    #             if entry.name.lower() in default_files and entry.is_file():
    #                 # 使用 os.access 检查当前用户是否有读取权限 (R_OK)
    #                 try:
    #                     # 尝试直接读取，而不是先检查权限
    #                     with open(entry.path, "rb") as f:
    #                         _ = f.read(1024)
    #                     default_files[entry.name] = entry.path
    #                     await self.update_tips_value(f"{entry.name} read successfully.")
    #                 except Exception as e:
    #                     name = entry.name
    #                     path = entry.path
    #                     ext = os.path.splitext(name)[1].lstrip(".").lower()
    #                     pickFile = await self.file_picker.pick_files(
    #                         dialog_title=f'Select a "{name}" file',
    #                         initial_directory=os.path.dirname(path),
    #                         allowed_extensions=[ext] if ext else None
    #                     )
    #                     if pickFile:
    #                         default_files[entry.name] = pickFile[0].path
    #     if all(v!="" for _,v in default_files.items()):
    #         await ft.SharedPreferences().set("Lotter_File", json.dumps(default_files))
    #         await self.update_tips_value(f"File path update complete.")

    async def getuser_dir(self):
        """获取用户目录"""
        await self.update_tips_value("Check the user directory.")
        if self.page.web:
            temp = app_data_path
            await self.update_tips_value("web mode, using system path.")
            return temp
        else:
            temp = await ft.SharedPreferences().get("user_dir")
            await self.update_tips_value("using SharedPreferences path.")
            return temp

    async def select_user_dir(self):
        if not self.page.web:
            picked_dir = await self.file_picker.get_directory_path(
                dialog_title="Please select a directory?"
            )
            if picked_dir:
                await ft.SharedPreferences().set("user_dir", picked_dir)
                await self.Checking_user_dir()


class SetingsPage:
    """设置页面类"""

    def __init__(self, page: ft.Page):
        self.page = page

        self.rule_mode_show = showRule()
        self.uese_input_mode = input_user_rule()
        self.default_setings = DefaultSettings()
        self.User_Directory = UserDirectory()
        self.apply_rule = {}

        self.uese_input_mode.setting_render_filters(self.render_filters)
        self.default_setings.setting_add_rule(self.open_dialog)
        self.default_setings.setting_render_filters(self.render_filters)
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
                self.User_Directory,
                self.default_setings,
                self.uese_input_mode,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
