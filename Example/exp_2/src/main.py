# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-15 00:52:00
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-16 11:43:18
import flet as ft
import math

class tipsEx(ft.SnackBar):
    def __init__(self, text:str):
        super().__init__(text)
        self._text = ft.Text(text, color=ft.Colors.RED_600)
        self.content = self._text
        self.bgcolor = ft.Colors.YELLOW_100
        
    
    def setText(self, text:str):
        self._text.value = text
        
class AppDialog(ft.CupertinoAlertDialog):
    def __init__(
        self,
        title: str,
        content: str,
        on_submit = None,              # 点击确定时的回调函数
        submit_text: str = "确定",
        cancel_text: str = "取消",
        is_destructive: bool = False, # 确定按钮是否显示为红色（警告）
    ):
        """
        :param title: 弹窗标题
        :param content: 弹窗内容文本
        :param on_submit: 点击“确定”执行的函数 (e) -> None
        :param submit_text: 确定按钮的文字
        :param cancel_text: 取消按钮的文字
        :param is_destructive: 如果为 True 确定按钮会变红（适合删除操作）
        """
        
        # 保存回调函数
        self.user_on_submit = on_submit if on_submit else None
        
        # 初始化父类
        super().__init__()

        # 1. 设置标题和内容 (你可以统一设置字体样式)
        self.title = ft.Text(title, weight=ft.FontWeight.BOLD)
        self.content = ft.Text(content, size=16)

        # 2. 构建按钮列表
        self.actions = [
            # 取消按钮 (默认逻辑：点击直接关闭)
            ft.CupertinoDialogAction(
                text=cancel_text,
                on_click=self.dismiss
            ),
            # 确定按钮
            ft.CupertinoDialogAction(
                text=submit_text,
                is_destructive_action=is_destructive,
                on_click=self.submit
            ),
        ]

    def dismiss(self, e):
        """关闭弹窗"""
        e.page.close(self)

    def submit(self, e):
        """执行回调并关闭弹窗"""
        # 1. 先关闭弹窗
        self.dismiss(e)
        # 2. 执行用户传入的逻辑
        if self.user_on_submit:
            self.user_on_submit(e)

def main(page: ft.Page):
    page.title = "youtebe flet exp 2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    side_length_a = ft.TextField(
        label="Triangle A/mm",
        hint_text="Enter Triangle side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_b = ft.TextField(
        label="Triangle B/mm",
        hint_text="Enter Triangle side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_c = ft.TextField(
        label="Triangle C/mm",
        hint_text="Enter Triangle side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    _tips = tipsEx(f"ALL Side Clear.")
    
    def clear_click(e):
        side_length_a.value = side_length_b.value = side_length_c.value = ""
        _tips.setText(f'Clear all triangle data.')
        page.open(_tips)
        page.update()

    def done_click(e):
        abc = []
        try:
            abc.append(int(side_length_a.value))
            abc.append(int(side_length_b.value))
            abc.append(int(side_length_c.value))
        except:
            _tips.setText('None of the data points for the triangle can be empty.')
            return
        abc.sort()
        a, b, c = abc
        if a + b <= c:
            error_dig = AppDialog(
                title = "错误提示",
                content = f"{a} {b} {c} 不符合三角形的基本原理."
            )
            page.open(error_dig)
            return
        s = (a + b + c) / 2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        area_dig = AppDialog(
            title="三角形面积",
            content=f"{a} {b} {c} 所构成的三角形面积为 {area}"
        )
        page.open(area_dig)

    page.add(
        ft.Column(
            [
                ft.Text(
                    value="计算物体面积",
                    text_align=ft.TextAlign.RIGHT,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_100,
                ),
                ft.Divider(height=20),
                side_length_a,
                side_length_b,
                side_length_c,
                ft.Divider(height=5),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Clear",
                            bgcolor=ft.Colors.RED,
                            color=ft.Colors.WHITE,
                            on_click=clear_click,
                        ),
                        ft.ElevatedButton(
                            text="Done",
                            bgcolor=ft.Colors.GREEN_100,
                            color=ft.Colors.WHITE,
                            on_click=done_click,
                        ),
                    ]
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "海伦公式 (Heron's Formula)", weight=ft.FontWeight.BOLD
                            ),
                            ft.Text("公式: S=sqrt(p(p-a)(p-b)(p-c))"),
                            ft.Text("条件: 已知三角形三条边长 a,b,b"),
                            ft.Text("步骤:", weight=ft.FontWeight.BOLD),
                            ft.Text("计算半周长 p={a+b+c} / 2"),
                            ft.Text("代入公式计算面积 (S)。"),
                        ]
                    )
                ),
            ]
        )
    )


ft.app(main)
