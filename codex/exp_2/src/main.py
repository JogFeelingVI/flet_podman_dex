# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-15 00:52:00
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2025-12-15 13:30:38
import flet as ft
import math

class tipsEx(ft.SnackBar):
    def __init__(self, text:str):
        super().__init__(text)
        self._text = ft.Text(text, color=ft.Colors.RED_200)
        self.content = self._text
        self.bgcolor = ft.Colors.YELLOW_100
        
    
    def setText(self, text:str):
        self._text.value = text

def main(page: ft.Page):
    page.title = "youtebe flet exp 2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    side_length_a = ft.TextField(
        label="side length A/mm",
        hint_text="Enter side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_b = ft.TextField(
        label="side length B/mm",
        hint_text="Enter side length mm",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    side_length_c = ft.TextField(
        label="side length C/mm",
        hint_text="Enter side length mm",
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
        print(f'{abc=}')
        abc.sort()
        a, b, c = abc
        if a + b <= c:
            _tips.setText('The data you entered does not meet the definition of a triangle.')
            page.open(_tips)
            return
        s = (a + b + c) / 2
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        _tips.setText(f'T-abc {a}/{b}/{c} area {area}')
        page.open(_tips)
        page.update()

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
                            ft.Text("公式: \(S=\sqrt{p(p-a)(p-b)(p-c)}\)。"),
                            ft.Text("条件: 已知三角形三条边长 \(a,b,c\)。"),
                            ft.Text("步骤:", weight=ft.FontWeight.BOLD),
                            ft.Text("计算半周长 \(p={a+b+c}{2}\)。"),
                            ft.Text("代入公式计算面积 \(S\)。"),
                        ]
                    )
                ),
            ]
        )
    )


ft.app(main)
