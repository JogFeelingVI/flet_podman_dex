# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-08 12:09:45

from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
from .jackpot_core import randomData
import flet as ft
import json
import os
import re

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

Lotter_Data = {
    "SSQ": {
        "description": "🇨🇳福利彩票双色球",
        "SA": [1, 33],
        "SB": [1, 16],
        "SA_K": 6,
        "SB_K": 1,
    },
    "KL8": {
        "description": "🇨🇳福利彩票快乐8",
        "PA": [1, 80],
        "PA_K": 10,
    },
    "Lotter52": {
        "description": "🇨🇳体育彩票大乐透",
        "PA": [1, 35],
        "PB": [1, 12],
        "PA_K": 5,
        "PB_K": 2,
    },
    "Array3/5": {
        "description": "🇨🇳体育彩票排列3/5",
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
    "🇺🇸Powerball": {
        "description": "🇺🇸Powerball",
        "PA": [1, 69],
        "PB": [1, 26],
        "PA_K": 5,
        "PB_K": 1,
    },
}


class SetingsPage:
    """设置页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.load_Lotter_Data()
        self.add_button_row = ft.Row(
            controls=[
                ft.Button("Add Row", icon=ft.Icons.ADD, on_click=self.handle_add_click)
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        self.note_text = ft.TextField(
            label="Note", hint_text="Rule Settings Instructions", dense=True
        )
        self.selection_container = ft.Column(
            controls=[
                self.note_text,
                self.get_Selection_line("A"),
                self.add_button_row,
            ],
            tight=True,
            spacing=10,
        )
        self.apply_rule = {}
        self.filter_items_column = ft.Column(spacing=10)
        self.dlg = self.get_dlg()
        self.view = self.get_seting_view()

    def load_Lotter_Data(self):
        """加载彩票预设数据并生成按钮"""
        # --- 构造按钮列表 ---
        button_list = []
        # 注意：Lotter_Data 应该在函数外部定义或作为参数传入
        for k, item in Lotter_Data.items():
            button_list.append(
                ft.Button(
                    f"{k}",
                    tooltip=ft.Tooltip(message=item.get("description", "")),
                    # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                    on_click=lambda e, name=k, data=item: self.save_preset_to_file(
                        name, data
                    ),
                )
            )
        return button_list

    def save_preset_to_file(self, name: str, preset_data: dict):
        """将处理后的预设数据写入 json 文件"""
        # 1. 构造符合你要求的嵌套格式
        valid_json = {
            "randomData": {
                "note": "save setings from preset buttons",
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
            self.page.show_dialog(
                get_snack_bar(f"Preset '{name}' has been applied and saved.")
            )
        self.apply_rule = valid_json
        self.render_filters()

    def get_Selection_line(self, Selection_name: str):
        name = f"P{Selection_name}"
        return ft.Row(
            controls=[
                ft.TextField(
                    label=name, expand=2, hint_text="min,max", data=f"{name}_Max"
                ),
                ft.TextField(label="Count", expand=1, data=f"{name}_K"),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            data=name,
        )

    def Processing_user_input(self, cdvalue: str):
        """处理用户输入"""
        if cdvalue in [None, ""]:
            return None
        mathch = re.findall(r"(\d+)", cdvalue)
        if mathch:
            val = [int(x) for x in mathch if x.isdigit()]
            return val if len(val) == 2 else val[0]
        return None

    def handle_apply(self):
        # 获取所有输入行的数据逻辑
        Rows_data = {"note": self.note_text.value or "setting game rule"}
        for control in self.selection_container.controls:
            if not hasattr(control, "data"):
                continue  # 只有输入行有 data 属性
            tag = control.data  # 提取标签名 P...
            Rows_data[tag] = {}
            try:
                for _child in control.controls:
                    if not isinstance(_child, ft.TextField):
                        continue
                    _cd = _child.data
                    _cd_val = _child.value
                    _cd_val = self.Processing_user_input(_cd_val)
                    if _cd_val is None:
                        continue
                    if _cd.endswith("_Max"):
                        if isinstance(_cd_val, list) and len(_cd_val) == 2:
                            Rows_data[tag]["range_start"] = _cd_val[0]
                            Rows_data[tag]["range_end"] = _cd_val[1]
                        elif isinstance(_cd_val, int):
                            Rows_data[tag]["range_start"] = 1
                            Rows_data[tag]["range_end"] = _cd_val
                    if _cd.endswith("_K"):
                        Rows_data[tag]["count"] = _cd_val
                    Rows_data[tag]["enabled"] = True
            except Exception:
                self.page.show_dialog(get_snack_bar("Rule settings error.", "error"))
        Rows_data = {k: v for k, v in Rows_data.items() if v not in [None, {}]}
        json_data = {"randomData": Rows_data.copy()}
        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        self.page.show_dialog(get_snack_bar(f"Game rules have been set."))
        self.apply_rule = json_data
        self.dlg.open = False
        self.render_filters()
        self.page.update()

    def handle_add_click(self, e):
        # 计算当前已有多少个输入行 (排除掉底部的 Add 按钮行)
        # 减 1 是因为最后一行是按钮行
        current_count = len(self.selection_container.controls) - 2
        # 字母排序 A, B, C...
        new_name = chr(65 + current_count)  # 65 是 'A'
        # 创建新行
        new_line = self.get_Selection_line(new_name)

        # 【关键】将新行插入到倒数第一位（即 Add 按钮的上方）
        self.selection_container.controls.insert(
            len(self.selection_container.controls) - 1, new_line
        )
        # 【关键】刷新容器，让新行显示出来
        self.selection_container.update()

    def render_filters(self):
        """渲染过滤器列表"""
        self.filter_items_column.controls.clear()
        self.page.session.store.set("settings", self.apply_rule)
        for key, item in self.apply_rule.get("randomData", {}).items():
            if key == "note":
                rd = randomData(seting=self.apply_rule["randomData"])
                exp = rd.get_exp()
                filter_control = ft.ListTile(
                    leading=ft.Icon(ft.Icons.ASSIGNMENT_ADD, color=Dracula_colors.ORANGE),
                    title=ft.Text(
                        f"🎉 This is an example. 🎉", color=Dracula_colors.COMMENT
                    ),
                    subtitle=ft.Text(
                        f"✨ {exp} ✨", color=Dracula_colors.COMMENT, weight="bold"
                    ),
                )
                self.filter_items_column.controls.append(filter_control)
                continue
            count_range = f"{item['range_start']} ~ {item['range_end']}"
            count = item["count"]
            filter_control = ft.ListTile(
                leading=ft.Icon(ft.Icons.RULE, color=Dracula_colors.COMMENT),
                title=ft.Text(
                    f"Section [ {key} ] Settings",
                    text_align=ft.TextAlign.LEFT,
                    color=Dracula_colors.PURPLE,
                ),
                subtitle=ft.Text(
                    f"Choose {count} numbers from {count_range}.",
                    text_align=ft.TextAlign.LEFT,
                    color=Dracula_colors.COMMENT,
                ),
            )
            self.filter_items_column.controls.append(filter_control)
        self.page.update()

    def close_dlg(self):
        self.dlg.open = False
        self.page.update()

    def get_dlg(self):
        dlg = ft.AlertDialog(
            title=ft.Text("add new game rules", color=Dracula_colors.COMMENT),
            content=ft.Container(
                content=self.selection_container,
                width=300,  # 锁定宽度防止抖动
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dlg()),
                ft.Button(
                    "Apply",
                    bgcolor=Dracula_colors.RED,
                    color=Dracula_colors.FOREGROUND,
                    on_click=lambda _: self.handle_apply(),
                ),
            ],
        )
        return dlg

    def get_seting_view(self):
        self.page.overlay.append(self.dlg)

        def open_dialog():
            self.dlg.open = True
            self.page.update()

        return ft.Column(
            controls=[
                ft.Text(
                    "Setting", size=25, weight="bold", color=Dracula_colors.COMMENT
                ),
                ft.Button(
                    "Add game rules",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: open_dialog(),
                ),
                # 这里可以添加更多的设置控件
                ft.Divider(),
                ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                ft.Divider(),
                ft.Column(
                    self.filter_items_column,
                    scroll=ft.ScrollMode.HIDDEN,
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
