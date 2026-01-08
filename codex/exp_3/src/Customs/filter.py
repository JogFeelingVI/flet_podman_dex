# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-08 07:17:08

from .jackpot_core import filterFunc
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import os
import json

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")
jackpot_filers = os.path.join(app_data_path, "jackpot_filters.dict")


class FilterPage:
    """筛选页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.filters_list = []
        self.editing_index = -1
        self.last_selected_target = None

        self.filter_items_column = ft.Column(spacing=2)
        # --- 1. 定义 Target 下拉列表 ---
        self.pop_func = ft.PopupMenuButton(
            content=ft.Text(value="func", color=Dracula_colors.GREEN, weight="bold"),
        )
        self.pop_target = ft.PopupMenuButton(
            content=ft.Text(value="all", color=Dracula_colors.COMMENT, weight="bold"),
        )
        self.condition_input = ft.AutoComplete(
            # suggestions=suggestions,
            # placeholder="Enter or select filter criteria.",
            on_select=lambda e: print(f"Selected: {e.selection}"),
        )
        self.dlg = self.get_dlg()
        self.view = self.get_filter_view()

    def close_dlg(self, e):
        self.dlg.open = False
        self.page.update()

    def get_dlg(self):
        dlg = ft.AlertDialog(
            title=ft.Text("Filter Settings", color=Dracula_colors.COMMENT),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            controls=[
                                ft.Text("Select Fun:"),
                                self.pop_func,
                                ft.Text("Target:"),
                                self.pop_target,
                            ],
                            tight=True,
                        ),
                        ft.Text("Conditions:", size=12, color=Dracula_colors.COMMENT),
                        self.condition_input,
                    ],
                    tight=True,
                    spacing=10,
                ),
                width=300,  # 锁定宽度防止抖动
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dlg),
                ft.Button(
                    "Apply",
                    bgcolor=Dracula_colors.RED,
                    color=Dracula_colors.FOREGROUND,
                    on_click=self.handle_apply,
                ),
            ],
        )
        return dlg

    def handle_func_click(self, name: str):
        self.pop_func.content.value = name

    def handle_target_click(self, name: str):
        self.pop_target.content.value = name

    def refresh_target_options(self):
        try:
            global jackpot_seting
            enabled_tags = ["all"]
            if not os.path.exists(jackpot_seting):
                return
            with open(jackpot_seting, "r", encoding="utf-8") as f:
                data = json.load(f)
                random_data = data.get("randomData", {})
                for key, content in random_data.items():
                    if isinstance(content, dict) and content.get("enabled") is True:
                        enabled_tags.append(key)
            if len(enabled_tags) == 1:
                return
            new_pop_items = []
            for key in enabled_tags:
                new_pop_items.append(
                    ft.PopupMenuItem(
                        content=f"{key}",
                        on_click=lambda e, k=key: self.handle_target_click(k),
                    )
                )
            self.pop_target.items = new_pop_items
        except Exception:
            self.page.show_dialog(
                get_snack_bar("refresh target options error.", "error")
            )
        return enabled_tags

    def refresh_func_options(self):
        self.funcs_dict = filterFunc.getFuncName()
        new_pop_items = []
        for key, item in self.funcs_dict.items():
            new_pop_items.append(
                ft.PopupMenuItem(
                    content=f"{key}",
                    on_click=lambda e, k=key: self.handle_func_click(k),
                )
            )
        self.pop_func.items = new_pop_items
        return list(self.funcs_dict.keys())

    def handle_apply(self, e):
        _func = self.pop_func.content.value
        _target = self.pop_target.content.value or "all"
        _condit = self.condition_input.value
        if _func == "func" or _condit == "":
            return

        # 保存本次的选择，以便下次 Add 时默认选中
        self.last_selected_target = _target

        new_data = {
            "func": _func,
            "target": _target,
            "condition": _condit,
        }

        if self.editing_index == -1:
            self.filters_list.append(new_data)
        else:
            self.filters_list[self.editing_index] = new_data

        self.dlg.open = False
        self.render_filters()
        with open(jackpot_filers, "w", encoding="utf-8") as f:
            for item in self.filters_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        self.page.session.store.set("filters", self.filters_list)
        self.page.update()

    def open_dialog(self, index=-1):
        self.editing_index = index
        available_tags = self.refresh_target_options()
        available_func = self.refresh_func_options()

        if index == -1:
            # --- 新增模式 (Add Filter) ---
            # 优先级 1: 如果有上一次记录的选择，且该选择目前依然在启用列表中，则继续使用它
            if self.last_selected_target in available_tags:
                self.pop_target.content.value = self.last_selected_target
            # 优先级 2: 否则，如果列表不为空，默认选择第一项
            elif available_tags:
                self.pop_target.content.value = available_tags[0]
            else:
                self.pop_target.content.value = "all"

            self.condition_input.value = ""  # 新增时清空输入框
        else:
            # --- 编辑模式 (Long Press) ---
            item = self.filters_list[index]
            # 确保保存的值还在当前启用列表中，否则下拉框会显示空白
            self.pop_target.content.value = (
                item["target"] if item["target"] in available_tags else None
            )
            self.pop_func.content.value = (
                item["func"] if item["func"] in available_func else None
            )
            self.condition_input.value = item["condition"]

        self.dlg.open = True
        self.page.update()

    def render_filters(self):
        self.filter_items_column.controls.clear()
        for idx, item in enumerate(self.filters_list):
            self.filter_items_column.controls.append(
                ft.Dismissible(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.FILTER_ALT, color=Dracula_colors.COMMENT
                        ),
                        title=ft.Text(
                            f"Target: {item['target']} Func: {item['func']}",
                            color=Dracula_colors.ORANGE,
                        ),
                        subtitle=ft.Text(
                            f"Condition: {item['condition']}",
                            color=Dracula_colors.PURPLE,
                        ),
                        # bgcolor=Dracula_colors.CURRENT_LINE,
                        on_long_press=lambda _, i=idx: self.open_dialog(i),
                    ),
                    on_dismiss=lambda _, i=idx: self.remove_filter(i),
                    dismiss_direction=ft.DismissDirection.START_TO_END,
                    background=ft.Container(
                        bgcolor=Dracula_colors.RED,
                        content=ft.Text(
                            "Delete", color=Dracula_colors.FOREGROUND, weight="bold"
                        ),
                        alignment=ft.Alignment.CENTER_LEFT,
                        padding=20,
                    ),
                )
            )

    def remove_filter(self, index):
        self.filters_list.pop(index)
        self.render_filters()
        with open(jackpot_filers, "w", encoding="utf-8") as f:
            for item in self.filters_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        self.page.session.store.set("filters", self.filters_list)
        self.page.update()

    def get_filter_view(self):
        self.page.overlay.append(self.dlg)

        return ft.Column(
            controls=[
                ft.Text(
                    "Filter",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=Dracula_colors.COMMENT,
                ),
                ft.Button(
                    "Add filtering rules",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: self.open_dialog(-1),
                ),
                ft.Divider(),
                ft.Column(
                    [self.filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
