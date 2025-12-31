# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-31 20:27:59

import flet as ft
import json
import os

# 获取系统标示
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

class Selectable(ft.Column):
    """setings page setings"""

    def __init__(
        self, text: str="test", range_min: int = 1, range_max: int = 100, onff: bool = True
    ):
        # 1. 初始化控件（去掉末尾逗号！）
        self.base_text = text
        self.counter_value = 5
        self.start = range_min
        self.end = range_max
        self.text_label = ft.Text(f"{self.base_text} {range_min}-{range_max}")
        self.range_slider = ft.RangeSlider(
            min=range_min,
            max=range_max,
            start_value=range_min,
            end_value=range_max,
            label="{value}",
            disabled=not onff,
            expand=True,  # 在 Row 中让 Slider 自动拉伸填满剩余空间
            on_change=self.handle_range_change,
        )
        self.switch_control = ft.Switch(
            label="ON" if onff else "OFF",
            value=onff,
            on_change=self.handle_switch_change,
        )

        # 第三行：计数器控件
        self.num_display = ft.Text(str(self.counter_value), size=20, weight="bold")

        self.counter_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REMOVE,
                    on_click=self.handle_decrement,
                    disabled=not onff,  # 初始状态跟随开关
                ),
                self.num_display,
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    on_click=self.handle_increment,
                    disabled=not onff,  # 初始状态跟随开关
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # 2. 调用父类初始化，直接传入控件列表
        super().__init__(
            controls=[
                # 第一行：标题和开关 左右分布
                ft.Row(
                    controls=[self.text_label, self.switch_control],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # 左右撑开,
                    expand=True,
                ),
                # 第二行：滑动条
                ft.Row(
                    controls=[self.range_slider],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
                ft.Row(controls=[self.counter_row], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=10,  # 行与行之间的间距
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # 内部控件水平拉伸
        )

    # --- 事件处理 ---
    def handle_increment(self, e):
        self.counter_value += 1
        self.num_display.value = str(self.counter_value)
        self.update()

    def handle_decrement(self, e):
        if self.counter_value > 0:
            self.counter_value -= 1
            self.num_display.value = str(self.counter_value)
            self.update()

    def handle_range_change(self, e):
        """当滑动条范围改变时触发"""
        self.start = int(self.range_slider.start_value)
        self.end = int(self.range_slider.end_value)
        # 更新文本显示
        self.text_label.value = f"{self.base_text} {self.start}-{self.end}"
        # 注意：在自定义控件内部修改属性后，需要调用 self.update() 才能看到变化
        self.update()

    def handle_switch_change(self, e):
        """当开关状态改变时触发"""
        e_vale = self.switch_control.value
        self.switch_control.label = "ON" if e_vale else "OFF"
        # 如果开关关闭 (False)，则禁用滑动条 (disabled=True)
        self.range_slider.disabled = not e_vale
        self.counter_row.disabled = not e_vale
        self.update()

    def get_json(self):
        return {
            f"{self.base_text}": {
                "enabled": self.switch_control.value,
                "range_start": int(self.range_slider.start_value),
                "range_end": int(self.range_slider.end_value),
                "count": self.counter_value,
            }
        }
    
    def set_json(self,key:str, json_data_item:dict):
        self.base_text = key
        
        self.switch_control.value = json_data_item["enabled"]
        self.range_slider.disabled = not json_data_item["enabled"]
        self.counter_row.disabled = not json_data_item["enabled"]
            
        s = json_data_item.get("range_start", self.range_slider.min)
        e = json_data_item.get("range_end", self.range_slider.max)
        self.range_slider.start_value = s
        self.range_slider.end_value = e
        
        self.counter_value = json_data_item["count"]
        self.num_display.value = str(self.counter_value) # 必须更新已有控件的 value
            
        # 2. 更新标题文字 (修改已有控件的属性，而不是创建新控件)
        self.text_label.value = f"{self.base_text} {int(s)}-{int(e)}"
        
        return self


def main(page: ft.Page):
    page.title = "Jackpot App"
    page.theme_mode = ft.ThemeMode.DARK
    # 设置移动端适配的内边距
    page.padding = 0


    # --- 页面逻辑控制 ---
    def on_navigation_change(e):
        index = e.control.selected_index
        # 切换中间的内容区域
        if index == 0:
            content_area.content = setting_view
        elif index == 1:
            content_area.content = filter_view
        elif index == 2:
            content_area.content = data_view
        page.update()

    def handle_menu_click(e):
        print(f"Menu clicked: {e.control.data}")
        if e.control.data == "quit":
            page.window_close()

    def read_from_json():
        json_data = {}
        select_pn = []
        try:
            with open(jackpot_seting, "r") as f:
                json_data = json.load(f)
            for k,item in json_data['randomData'].items():
                if k == 'note':
                    continue
                temp=Selectable().set_json(k,item)
                select_pn.append(temp)
        except Exception as e:
            json_data = {}
            
        
        if select_pn.__len__()==0:
            for k in ["PA", "PB", "PC"]:
                select_pn.append(Selectable(k))
        return select_pn
    
    selectPx = read_from_json()

    def save_to_json():
        json_data = {
            "randomData": {"note":"setings json code save_to_json()"}
        }
        for sPn in selectPx:
            json_data['randomData'].update(sPn.get_json())

        with open(jackpot_seting, "w") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        # snack_bar
        snack_bar = ft.SnackBar(
            content=ft.Text(
                f"Settings have been saved successfully.",
                style=ft.TextStyle(color="WHITE"),
            ),
            bgcolor="PINK",
        )
        page.show_dialog(snack_bar)
        page.update()
    

    # Setting 页面
    setting_view = ft.Column(
        controls=[
            ft.Text("Setings", size=25, weight=ft.FontWeight.BOLD),
            *selectPx,
            ft.Divider(height=5),
            ft.Row(
                controls=[
                    ft.Button(
                        "Save Steings",
                        icon=ft.Icons.SAVE,
                        icon_color=ft.Colors.WHITE,
                        color=ft.Colors.WHITE,
                        on_click=save_to_json,
                        style=ft.ButtonStyle(
                            bgcolor="PINK", shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                    )
                ],
                alignment="END",
            ),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # Filter 页面
    filter_view = ft.Column(
        controls=[
            ft.Text("Filter", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("在此添加各种过滤条件："),
            ft.TextField(label="关键词过滤", prefix_icon=ft.Icons.FILTER_2_SHARP),
            ft.Dropdown(
                label="分类筛选",
                options=[
                    ft.dropdown.Option("选项 1"),
                    ft.dropdown.Option("选项 2"),
                ],
            ),
            ft.Checkbox(label="仅显示有效数据"),
        ],
        expand=True,
    )

    # Data 页面
    data_view = ft.Column(
        controls=[
            ft.Text("DataView", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("显示筛选后的结果："),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("结果")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("1")),
                            ft.DataCell(ft.Text("数据 A")),
                        ]
                    ),
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("2")),
                            ft.DataCell(ft.Text("数据 B")),
                        ]
                    ),
                ],
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    # --- 2. 界面组件定义 ---

    # 中间显示区域容器
    content_area = ft.Container(
        content=setting_view,  # 默认显示设置页
        expand=True,
        padding=20,
    )

    # 顶部 AppBar
    page.appbar = ft.AppBar(
        leading=ft.Icon(
            ft.Icons.MONEY_OFF_CSRED_ROUNDED, color=ft.Colors.AMBER
        ),  # 程序图标
        leading_width=40,
        title=ft.Text("jackpot", weight=ft.FontWeight.BOLD),
        center_title=False,
        bgcolor=ft.Colors.BLACK_12,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        "Send",
                        icon=ft.Icons.SEND,
                        data="send",
                        on_click=handle_menu_click,
                    ),
                    ft.PopupMenuItem(
                        "Compo",
                        icon=ft.Icons.IMAGE_OUTLINED,
                        data="compo",
                        on_click=handle_menu_click,
                    ),
                    ft.PopupMenuItem(
                        "Quit",
                        icon=ft.Icons.EXIT_TO_APP,
                        data="quit",
                        on_click=handle_menu_click,
                    ),
                ]
            ),
        ],
    )

    # 底部 NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Setting",
            ),
            ft.NavigationBarDestination(icon=ft.Icons.FILTER_LIST_ALT, label="Filter"),
            ft.NavigationBarDestination(
                icon=ft.Icons.DATA_EXPLORATION_OUTLINED, label="Data"
            ),
        ],
        on_change=on_navigation_change,
    )

    # 将内容添加到页面
    page.add(content_area)
    page.update()


# 运行应用
ft.run(main)
